from flask import Blueprint, render_template

from app.models import UnitOrg

bp = Blueprint('unitorg', __name__, url_prefix='/org')


@bp.route('/')
def index():
    orgs = UnitOrg.select()
    ctx = {
        'unitorg': orgs
    }
    
    return render_template('org/index.html', ctx=ctx)