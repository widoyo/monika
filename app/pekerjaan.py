from flask import Blueprint, render_template, abort, redirect, url_for
from peewee import DoesNotExist
import json

from app.models import Pekerjaan, build_tree

bp = Blueprint('pekerjaan', __name__, url_prefix='/task')


@bp.route('/<int:id>/realisasi', methods=['POST'])
def update_realisasi(id):
    return {'ok': True}


@bp.route('<int:id>/rencana', methods=['POST'])
def update_rencana(id):
    return {'ok': True} 


@bp.route('/<int:id>')
def show(id):
    '''Tampilkan Pekerjaan dg <id>'''
    try:
        task = Pekerjaan.get(id)
    except DoesNotExist:
        return abort(404)
    template = 'pekerjaan/show.html'
    ctx = {
        'task': task,
    }
    if task.is_has_children:
        all_pek = task.children
        all_minggu = [p.minggu_mulai for p in all_pek if p.minggu_mulai]
        minggu_pertama = all_minggu[0]
        all_waktu_akhir = [p.waktu_akhir.isocalendar()[1] for p in all_pek if p.waktu_akhir]
        
        all_waktu_akhir.sort(reverse=True)
        minggu_terakhir = all_waktu_akhir[0]
        pekerjaan_tree = build_tree(all_pek)
        template = 'pekerjaan/show_child.html'
        ctx.update({'pekerjaan_tree': pekerjaan_tree, 'awal_minggu': minggu_pertama})
    
    return render_template(template, ctx=ctx)


@bp.route('/<int:id>', methods=['POST'])
def update(id):
    try:
        task = Pekerjaan.get(id)
    except DoesNotExist:
        return abort(404)
    
    # Update logic here, e.g., task.uraian = request.form['uraian']
    existing_realisasi = json.loads(task.realisasi)
    # task.save()
    
    return redirect(url_for('pekerjaan.show', id=task.id))