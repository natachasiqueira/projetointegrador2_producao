from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from . import bp
from app.models import db, Paciente, Psicologo
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

@bp.route('/')
@bp.route('/index')
def index():
    """Página inicial"""
    return render_template('index.html')

@bp.route('/dashboard')
@login_required
def dashboard_redirect():
    """Redireciona para a área apropriada baseada no tipo de usuário"""
    if current_user.tipo_usuario == 'admin':
        return redirect(url_for('main.area_admin'))
    elif current_user.tipo_usuario == 'psicologo':
        return redirect(url_for('main.area_psicologo'))
    elif current_user.tipo_usuario == 'paciente':
        return redirect(url_for('main.area_paciente'))
    else:
        return redirect(url_for('main.index'))

@bp.route('/area-admin')
@login_required
def area_admin():
    """Redireciona para o dashboard administrativo atualizado"""
    if current_user.tipo_usuario != 'admin':
        return redirect(url_for('main.dashboard_redirect'))
    return redirect(url_for('admin.dashboard'))

@bp.route('/area-psicologo')
@login_required
def area_psicologo():
    """Redireciona para o dashboard atualizado do psicólogo"""
    if current_user.tipo_usuario != 'psicologo':
        return redirect(url_for('main.dashboard_redirect'))
    return redirect(url_for('psicologo.dashboard'))

@bp.route('/area-paciente')
@login_required
def area_paciente():
    """Redireciona para o dashboard atualizado do paciente"""
    if current_user.tipo_usuario != 'paciente':
        return redirect(url_for('main.dashboard_redirect'))
    return redirect(url_for('paciente.dashboard'))