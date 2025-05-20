from flask import Flask, render_template, request, url_for, redirect, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect
from wtforms.validators import DataRequired
from urllib.parse import urlparse, urljoin
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from flask_wtf import FlaskForm
import datetime

from playhouse.flask_utils import FlaskDB

db_wrapper = FlaskDB()

login_manager = LoginManager()
login_manager.login_view = 'login'
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
    
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.get(user_id)
        except User.DoesNotExist:
            return None
    
    register_blueprint(app)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('homepage'))
        form = LoginForm()
        next = get_redirect_target()
        print('login', app.config['SECRET_KEY'])
        if form.validate_on_submit():
            print('validate_on_submit')
            try:
               user = User.get(User.username==form.username.data)
            except User.DoesNotExist:
                flash('username atau password keliru')
                return redirect(url_for('login'))
            if user is None or not user.check_password(form.password.data):
                flash('username atau password keliru')
                return redirect(url_for('login'))
            
            login_user(user)
            print('login_user')
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
    
    
    @app.route('/')
    @login_required
    def homepage():
        return render_template('index.html')    
    
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
