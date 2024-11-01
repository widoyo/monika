from flask import Blueprint, render_template, request

from app.models import Proyek

bp = Blueprint('proyek', __name__, url_prefix='proyek')

@bp.route('/')
def index():
    proyeks = Proyek.select()
    ctx = {
        'proyek': proyeks
    }
    return render_template('proyek/index.html', ctx=ctx)