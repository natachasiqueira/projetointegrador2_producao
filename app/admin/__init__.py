from flask import Blueprint

admin = Blueprint('admin', __name__, url_prefix='/admin')

from app.admin.routes import init_routes
init_routes(admin)