from flask import Flask, render_template, request, url_for, redirect, flash, Response
from flask_login import LoginManager, current_user, login_user, logout_user, login_required  # type: ignore
from flask_wtf.csrf import CSRFProtect
from wtforms.validators import DataRequired
from urllib.parse import urlparse, urljoin
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from flask_wtf import FlaskForm
import datetime
import peewee as pw
import csv
from io import StringIO

from playhouse.flask_utils import FlaskDB

db_wrapper = FlaskDB()

login_manager = LoginManager()
login_manager.login_view = 'login'  # type: ignore
login_manager.login_message = 'Silakan login untuk mengakses...'

csrf = CSRFProtect()

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc

def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target
        
def redirect_back(endpoint, **values):
    target = request.form['next'] 
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)

def create_app():
    app = Flask(__name__)
    #app.config['DATABASE'] = 'postgresql://citauser:thispass@localhost:5432/citadb'
    app.config.from_pyfile('config.py')
    db_wrapper.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    
    @app.template_filter('strftime')
    def _jinja2_filter_datetime(value, fmt=None):
        if not value:
            return ''
        if fmt is None:
            fmt = '%d %b %Y'
        return value.strftime(fmt)

    @app.template_filter('seconds_to_hm')
    def seconds_to_hm_filter(value):
        if not value or value <= 0:
            return ''
        hours = value // 3600
        minutes = (value % 3600) // 60
        return f"{hours:02d}:{minutes:02d}"

    from app.models import User, Kehadiran  # Ensure Kehadiran is a peewee.Model subclass
    from peewee import DoesNotExist

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.get(user_id)
        except DoesNotExist:
            return None
    
    register_blueprint(app)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('homepage'))
        form = LoginForm()
        next = get_redirect_target()
        if form.validate_on_submit():
            try:
               user = User.get(User.username==form.username.data)
            except DoesNotExist:
                flash('username atau password keliru')
                return redirect(url_for('login'))
            if user is None or not user.check_password(form.password.data):
                flash('username atau password keliru')
                return redirect(url_for('login'))
                
            login_user(user)
            user.last_login = datetime.datetime.now()
            user.save()
            return redirect_back('homepage')
        else:
            if request.method == 'POST':
                flash('Form tidak valid. Silakan periksa kembali input Anda.')
        return render_template('login.html', title='Sign In', form=form, next=next)
    
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect('/')    
    
    
    @app.route('/download')
    @login_required
    def download():
        """Download file"""
        kehadiran = request.args.get('kehadiran', None)
        if kehadiran:
            s = request.args.get('s', None)
            if s:
                try:
                    sampling = datetime.datetime.strptime(s, '%Y-%m').date()
                except ValueError:
                    pass
                try:
                    sampling = datetime.datetime.strptime(s, '%Y/%m').date()
                except ValueError:
                    pass
            else:
                sampling = datetime.datetime.now().date()
            # ambil data kehadiran untuk tahun dan bulan sesuai sampling
            # Aggregate Kehadiran: group by username, count masuk, sum durasi (keluar - masuk)
            # Make sure Kehadiran is a peewee.Model and has an 'id' field; otherwise, use the correct primary key field
            kehadiran_list = (
                Kehadiran
                .select(
                    Kehadiran.username,
                    User.fullname.alias('nama'),
                    pw.fn.COUNT(getattr(Kehadiran, 'id', Kehadiran._meta.primary_key)).alias('jumlah_masuk'),
                    pw.fn.SUM(Kehadiran.keluar - Kehadiran.masuk).alias('total_durasi')
                )
                .join(User, on=(Kehadiran.username == User.username))
                .where(
                    (pw.fn.DATE_PART('year', Kehadiran.masuk) == sampling.year) & 
                    (pw.fn.DATE_PART('month', Kehadiran.masuk) == sampling.month) & 
                    (Kehadiran.keluar.is_null(False))
                )
                .group_by(Kehadiran.username, User.fullname)
                .order_by(Kehadiran.username)
                .dicts()
            )
            si = StringIO()
            cw = csv.writer(si, delimiter=';')
            cw.writerow(['Kehadiran Bulan', sampling.strftime('%B %Y')])
            cw.writerow(['Nama', 'Hari Kerja', 'Jam Kerja', 'Jam/Hari'])
            for r in kehadiran_list:
                total_durasi_jam = 0
                # Convert total_durasi (timedelta or seconds) to hours:minutes format
                total_durasi = r.get('total_durasi', 0) or 0
                if isinstance(total_durasi, datetime.timedelta):
                    total_seconds = int(total_durasi.total_seconds())
                else:
                    total_seconds = int(total_durasi)
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                durasi_str = f"{hours:02d}:{minutes:02d}"
                # Calculate jam_per_hari as total_durasi divided by jumlah_masuk, formatted as HH:MM
                jumlah_masuk = r.get('jumlah_masuk', 0) or 1
                avg_per_hari_seconds = total_seconds // jumlah_masuk if jumlah_masuk else 0
                jam_per_hari_hours = avg_per_hari_seconds // 3600
                jam_per_hari_minutes = (avg_per_hari_seconds % 3600) // 60
                jam_per_hari_str = f"{jam_per_hari_hours:02d}:{jam_per_hari_minutes:02d}"
                
                cw.writerow([r.get('nama', ''), r.get('jumlah_masuk', 0), durasi_str, jam_per_hari_str])

            output = si.getvalue()
            si.close()
            return Response(
                output,
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment;filename=kehadiran_{sampling.year}_{sampling.month:02d}.csv'}
            )            
        return render_template('download.html')
    
    
    @app.route('/')
    @login_required
    def homepage():
        """Halaman utama"""
        template_name = 'index.html'
        s = request.args.get('s', None)
        today = datetime.datetime.now().date()
        sampling = today
        if s:
            try:
                sampling = datetime.datetime.strptime(s, '%Y-%m').date()
            except ValueError:
                pass
            try:
                sampling = datetime.datetime.strptime(s, '%Y/%m').date()
            except ValueError:
                pass
        # jika sampling > today, paksakan samplaing = today
        if sampling > today:
            sampling = today
        # jika sampling < bulan ini, paksakan tanggal sampling = akhir bulan bersangkutan
        if sampling.month < today.month or sampling.year < today.year:
            sampling = datetime.datetime(sampling.year, sampling.month, 1) + datetime.timedelta(days=31)
            sampling = sampling.replace(day=1) - datetime.timedelta(days=1) 
        ctx = {
            'title': 'Dashboard',
            'now': datetime.datetime.now(),
            'today': today,
            'sampling': sampling,
        }
        if current_user.is_adm:
            template_name = 'index_adm.html'
            first_day = sampling.replace(day=1)
            # Get all Kehadiran for this month
            kehadiran_qs = (Kehadiran
                .select()
                .where(
                    (pw.fn.DATE(Kehadiran.masuk) >= first_day) &
                    (pw.fn.DATE(Kehadiran.masuk) <= sampling)
                )
                .order_by(Kehadiran.masuk.desc())
            )
            # Group by day for template
            from collections import defaultdict
            grouped = defaultdict(list)
            for k in kehadiran_qs:
                print(k.masuk, k.username)
                day = k.masuk.date()
                grouped[day].append(k)

            ctx['grouped_kehadiran'] = dict(grouped)
        else:
            template_name = 'index_perusahaan.html'
            kehadiran = Kehadiran.select().where(Kehadiran.username == current_user.username, pw.fn.DATE(Kehadiran.cdate) == datetime.datetime.now().date()).first()
            form_absen = ''
            if not kehadiran:
                form_absen = 'kehadiran/_form_absen_masuk.html'
            elif kehadiran.is_inside:
                if datetime.datetime.now() - kehadiran.masuk >= datetime.timedelta(hours=1):
                    form_absen = 'kehadiran/_form_absen_keluar.html'
            ctx['form_absen'] = form_absen                
            ctx['kehadiran'] = kehadiran
            # Generate list of dates from the 1st of the month to today
            first_day = sampling.replace(day=1)
            date_list = [first_day + datetime.timedelta(days=i) for i in range((sampling - first_day).days + 1)]
            ctx['date_list'] = date_list
            rekap_kehadiran = (Kehadiran
                .select()
                .where(
                    (Kehadiran.username == current_user.username) &
                    (pw.fn.DATE(Kehadiran.cdate) >= first_day) &
                    (pw.fn.DATE(Kehadiran.cdate) <= sampling)
                )
                .order_by(Kehadiran.cdate)
            )
            # Buat dictionary untuk mapping tanggal ke Kehadiran
            kehadiran_dates  = dict([(k.masuk.date().day, k) for k in rekap_kehadiran])
            rekap_kehadiran_list = []
            for d in date_list:
                if d.day in kehadiran_dates.keys():
                    print(f"Found kehadiran for date: {d}")
                    obj = kehadiran_dates[d.day].__dict__['__data__']
                    obj.update({'tanggal': d})
                else:
                    obj = {'tanggal': d}
                rekap_kehadiran_list.append(obj)
            ctx['rekap_kehadiran'] = rekap_kehadiran_list

        return render_template(template_name, ctx=ctx)
    
    return app


def register_blueprint(app):
    
    from app.proyek import bp as bp_proyek
    from app.user import bp as bp_user
    from app.unitorg import bp as bp_unitorg
    from app.pekerjaan import bp as bp_pekerjaan
    from app.perusahaan import perusahaan_bp as bp_perusahaan
    from app.kehadiran import kehadiran_bp as bp_kehadiran
    
    app.register_blueprint(bp_proyek)
    app.register_blueprint(bp_user)
    app.register_blueprint(bp_unitorg)
    app.register_blueprint(bp_pekerjaan)
    app.register_blueprint(bp_perusahaan)
    app.register_blueprint(bp_kehadiran)
