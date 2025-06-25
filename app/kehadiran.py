from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
import datetime
from peewee import fn

from app.models import Kehadiran, User

kehadiran_bp = Blueprint('kehadiran', __name__, url_prefix='/kehadiran')

@kehadiran_bp.route('/<string:username>', methods=['GET'])
@login_required
def user_kehadiran(username):
    """Kehadiran user by username"""
    if not current_user.is_adm:
        return redirect(url_for('homepage'))
    today = datetime.datetime.now().date()
    first_day = today.replace(day=1)
    person = User.get_or_none(User.username == username)
    kehadiran = Kehadiran.select().where(
        (Kehadiran.username == username) &
        (fn.DATE(Kehadiran.cdate) >= first_day) &
        (fn.DATE(Kehadiran.cdate) <= today)
    ).order_by(Kehadiran.cdate.desc())
    ctx = {
        'kehadiran': kehadiran,
        'title': f'Kehadiran {username}',
        'person': person,
        'personils': [(u.username, u.fullname) for u in User.select().where(User.is_adm == False).order_by(User.fullname)],
        'today': today
    }
    return render_template('kehadiran/show.html', ctx=ctx)

@kehadiran_bp.route('/', methods=['GET'])
@login_required
def index():
    """Kehadiran user"""
    today = datetime.datetime.now().date()
    kehadiran = Kehadiran.select().where(Kehadiran.username == current_user.username, fn.DATE(Kehadiran.cdate) == today).first()
    ctx = {
        'kehadiran': kehadiran,
        'title': 'Kehadiran'
    }
    return render_template('kehadiran/index.html', ctx=ctx)


@kehadiran_bp.route('/klok', methods=['POST'])
@login_required
def klok():
    """Kehadiran user"""
    user_agent = request.headers.get('User-Agent')
    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    if request.form.get('id_kehadiran'):
        # update
        absen = Kehadiran.get(int(request.form.get('id_kehadiran')))
        absen.keluar = datetime.datetime.now()
        absen.lok_keluar = request.form.get('lokasi')
        absen.ll_keluar = request.form.get('lonlat')
        absen.ua_keluar = user_agent
        absen.ip_keluar = ip_address
        absen.save()
        return redirect('/')
    absen = Kehadiran.create(
        user=current_user,
        username=current_user.username,
        masuk=datetime.datetime.now(),
        status='masuk',
        lok_masuk=request.form.get('lokasi'),
        ll_masuk=request.form.get('lonlat'),
        ip_masuk=ip_address,
        ua_masuk=user_agent
    )    
    return redirect(url_for('homepage'))