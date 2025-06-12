from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
import datetime
from peewee import fn

from app.models import Kehadiran, User

kehadiran_bp = Blueprint('kehadiran', __name__, url_prefix='/kehadiran')

@kehadiran_bp.route('/<string:username>', methods=['GET'])
@login_required
def user_kehadiran(username):
    """Kehadiran user by username"""
    today = datetime.datetime.now().date()
    first_day = today.replace(day=1)
    person = User.get_or_none(User.username == username)
    kehadiran = Kehadiran.select().where(
        (Kehadiran.username == username) &
        (fn.DATE(Kehadiran.cdate) >= first_day) &
        (fn.DATE(Kehadiran.cdate) <= today)
    ).order_by(Kehadiran.cdate.desc())
    ctx = {
        'kehadiran': kehadiran,
        'title': f'Kehadiran {username}',
        'person': person,
        'today': today
    }
    return render_template('kehadiran/show.html', ctx=ctx)

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