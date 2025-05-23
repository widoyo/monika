from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
import datetime
from peewee import fn

from app.models import Kehadiran

kehadiran_bp = Blueprint('kehadiran', __name__, url_prefix='/kehadiran')

@kehadiran_bp.route('/', methods=['GET'])
@login_required
def index():
    """Kehadiran user"""
    today = datetime.datetime.now().date()
    kehadiran = Kehadiran.select().where(Kehadiran.username == current_user.username, fn.DATE(Kehadiran.cdate) == today).first()
    ctx = {
        'kehadiran': kehadiran,
        'title': 'Kehadiran'
    }
    return render_template('kehadiran/index.html', ctx=ctx)


@kehadiran_bp.route('/klok', methods=['POST'])
@login_required
def klok():
    """Kehadiran user"""
    if request.form.get('id_kehadiran'):
        # update
        absen = Kehadiran.get(int(request.form.get('id_kehadiran')))
        absen.keluar = datetime.datetime.now()
        absen.keterangan = request.form.get('lokasi')
        absen.ll = request.form.get('lonlat')
        absen.save()
        return redirect('/')
    absen = Kehadiran.create(
        username=current_user.username,
        masuk=datetime.datetime.now(),
        status='masuk',
        keterangan=request.form.get('lokasi'),
        ll=request.form.get('lonlat'))    
    return redirect(url_for('homepage'))