from flask import Blueprint

bp = Blueprint('paciente', __name__)

from app.paciente import routes