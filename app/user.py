from flask import Blueprint, render_template, url_for, redirect
from flask_login import login_required, current_user
from app.models import User

bp = Blueprint('user', __name__, url_prefix='/user')


@bp.route('/')
@login_required
def index():
    if current_user.perusahaan:
        return redirect(url_for('homepage'))
    users = User.select().order_by(User.username.asc())
    ctx = {
        'users': users
    }
    return render_template('user/index.html', ctx=ctx)