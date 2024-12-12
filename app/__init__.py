from flask import Flask, render_template, abort
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect

from playhouse.flask_utils import FlaskDB

db_wrapper = FlaskDB()

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Silakan login untuk mengakses...'

csrf = CSRFProtect()

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

    @app.route('/login')
    def login():
        return render_template('login.html')
    
    @app.route('/')
    def homepage():
        return render_template('index.html')    
    
    return app


def register_blueprint(app):
    
    from app.proyek import bp as bp_proyek
    from app.user import bp as bp_user
    from app.unitorg import bp as bp_unitorg
    from app.pekerjaan import bp as bp_pekerjaan
    
    app.register_blueprint(bp_proyek)
    app.register_blueprint(bp_user)
    app.register_blueprint(bp_unitorg)
    app.register_blueprint(bp_pekerjaan)