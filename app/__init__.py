from flask import Flask, render_template, abort
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf.csrf import CSRFProtect

from playhouse.flask_utils import FlaskDB

db_wrapper = FlaskDB()

login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    #app.config['DATABASE'] = 'postgresql://citauser:thispass@localhost:5432/citadb'
    app.config.from_pyfile('config.py')
    db_wrapper.init_app(app)
    csrf.init_app(app)
    
    register_bluprint(app)
    
    return app


def register_bluprint(app):
    
    from app.proyek import bp as bp_proyek
    from app.user import bp as bp_user
    from app.unitorg import bp as bp_unitorg
    
    app.register_blueprint(bp_proyek)
    app.register_blueprint(bp_user)
    app.register_blueprint(bp_unitorg)