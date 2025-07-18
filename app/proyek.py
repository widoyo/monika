from flask import Blueprint, render_template, abort
from peewee import DoesNotExist

from app.models import Proyek, Pekerjaan, build_tree

bp = Blueprint('proyek', __name__, url_prefix='/proyek')


@bp.route('/<int:id>')
def show(id):
    try:
        proyek = Proyek.get(id)
    except DoesNotExist:
        return abort(404)
    all_pek = Pekerjaan.select().where(Pekerjaan.proyek == proyek).order_by(Pekerjaan.uraian)
    # Build the tree structure from the flat list of Pekerjaan
    pekerjaan_tree = build_tree(all_pek)
    ctx = {
        'proyek': proyek,
        'pekerjaan_tree': pekerjaan_tree,
    }
    return render_template('proyek/show.html', ctx=ctx)


@bp.route('/')
def index():
    proyeks = Proyek.select()
    ctx = {
        'proyeks': proyeks
    }
    return render_template('proyek/index.html', ctx=ctx)