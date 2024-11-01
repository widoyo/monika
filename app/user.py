from flask import Blueprint, render_template

from app.models import User

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/')
def index():
    users = User.select()
    ctx = {
        'users': users
    }
    
    return render_template('user/index.html', ctx=ctx)