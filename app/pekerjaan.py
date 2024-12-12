from flask import Blueprint, render_template, abort
from peewee import DoesNotExist

from app.models import Pekerjaan

bp = Blueprint('pekerjaan', __name__, url_prefix='/task')


@bp.route('/<int:id>')
def show(id):
    try:
        task = Pekerjaan.get(id)
    except DoesNotExist:
        return abort(404)
    ctx = {
        'task': task
    }
    return render_template('pekerjaan/show.html', ctx=ctx)
