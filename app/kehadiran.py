from flask import Blueprint, render_template, request, redirect
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
    if current_user.is_adm:
        kehadiran_list = Kehadiran.select().order_by(Kehadiran.cdate.desc())
    elif current_user.is_supervisi:
        
        kehadiran_list = Kehadiran.select().where(Kehadiran.unitorg == current_user.unitorg).order_by(Kehadiran.cdate.desc())
    else:
        kehadiran_list = Kehadiran.select().where(Kehadiran.username == current_user.username, fn.DATE(Kehadiran.cdate) == today).order_by(Kehadiran.cdate.desc())
    ctx = {
        'kehadiran_list': kehadiran_list,
        'title': 'Kehadiran'
    }
    return render_template('kehadiran/index.html', ctx=ctx)


@kehadiran_bp.route('/klok', methods=['POST'])
@login_required
def klok():
    """Kehadiran user"""
    absen = Kehadiran.create(
        username=current_user.username,
        status='in',
        ll=request.form.get('ll'))    
    return redirect('/kehadiran')