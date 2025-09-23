from flask import Blueprint

bp = Blueprint('psicologo', __name__)

from app.psicologo import routes