from flask import Blueprint, render_template, abort
from peewee import DoesNotExist

from app.models import Proyek

bp = Blueprint('proyek', __name__, url_prefix='/proyek')


@bp.route('/<int:id>')
def show(id):
    try:
        proyek = Proyek.get(id)
    except DoesNotExist:
        return abort(404)
    ctx = {
        'proyek': proyek
    }
    return render_template('proyek/show.html', ctx=ctx)


@bp.route('/')
def index():
    proyeks = Proyek.select()
    ctx = {
        'proyeks': proyeks
    }
    return render_template('proyek/index.html', ctx=ctx)