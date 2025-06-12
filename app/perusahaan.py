from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from flask_login import current_user

perusahaan_bp = Blueprint('perusahaan', __name__)

from app.models import Perusahaan

@perusahaan_bp.route('/perusahaan', methods=['GET'])
def list_perusahaan():
    perusahaan_list = Perusahaan.select().order_by(Perusahaan.nama.asc())
    return render_template('perusahaan/index.html', perusahaan_list=perusahaan_list)