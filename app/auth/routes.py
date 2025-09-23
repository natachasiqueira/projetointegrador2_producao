from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from . import bp
from app import db
from app.models import Usuario, Paciente
from app.auth.forms import LoginForm, RegistroPacienteForm, AlterarSenhaForm, EditarPerfilForm

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard_redirect'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(
            email=form.email.data,
            tipo_usuario=form.tipo_usuario.data
        ).first()
        
        if usuario and usuario.check_senha(form.senha.data) and usuario.ativo:
            login_user(usuario)
            next_page = request.args.get('next')
            
            # Redireciona para a área apropriada baseada no tipo de usuário
            if not next_page:
                if usuario.tipo_usuario == 'psicologo':
                    next_page = url_for('main.area_psicologo')
                elif usuario.tipo_usuario == 'paciente':
                    next_page = url_for('main.area_paciente')
                elif usuario.tipo_usuario == 'admin':
                    next_page = url_for('admin.dashboard')
            
            flash('Login realizado com sucesso!', 'success')
            return redirect(next_page)
        else:
            flash('E-mail, senha ou tipo de usuário incorretos.', 'error')
    
    return render_template('auth/login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Logout do usuário"""
    logout_user()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('main.index'))

@bp.route('/registro-paciente', methods=['GET', 'POST'])
def registro_paciente():
    """Registro de novo paciente"""
    form = RegistroPacienteForm()
    if form.validate_on_submit():
        # Criar usuário
        usuario = Usuario(
            nome_completo=form.nome_completo.data,
            email=form.email.data,
            telefone=form.telefone.data,
            tipo_usuario='paciente'
        )
        usuario.set_senha(form.senha.data)
        
        db.session.add(usuario)
        db.session.flush()  # Para obter o ID do usuário
        
        # Criar paciente
        paciente = Paciente(
            usuario_id=usuario.id
        )
        
        db.session.add(paciente)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Você já pode fazer login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/registro_paciente.html', form=form)

@bp.route('/alterar-senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    """Alterar senha do usuário logado"""
    form = AlterarSenhaForm()
    if form.validate_on_submit():
        if current_user.check_senha(form.senha_atual.data):
            current_user.set_senha(form.nova_senha.data)
            db.session.commit()
            flash('Senha alterada com sucesso!', 'success')
            return redirect(url_for('main.dashboard_redirect'))
        else:
            flash('Senha atual incorreta.', 'error')
    
    return render_template('auth/alterar_senha.html', form=form)

@bp.route('/editar-perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    """Editar perfil do usuário logado"""
    form = EditarPerfilForm()
    
    if form.validate_on_submit():
        current_user.nome_completo = form.nome_completo.data
        current_user.telefone = form.telefone.data
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('main.dashboard_redirect'))
    elif request.method == 'GET':
        # Preenche o formulário com os dados atuais
        form.nome_completo.data = current_user.nome_completo
        form.telefone.data = current_user.telefone
    
    return render_template('auth/editar_perfil.html', form=form)

# API Routes para autenticação
@bp.route('/api/login', methods=['POST'])
def api_login():
    """API de login"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('senha') or not data.get('tipo_usuario'):
        return jsonify({'error': 'E-mail, senha e tipo de usuário são obrigatórios'}), 400
    
    usuario = Usuario.query.filter_by(
        email=data['email'],
        tipo_usuario=data['tipo_usuario']
    ).first()
    
    if usuario and usuario.check_senha(data['senha']) and usuario.ativo:
        login_user(usuario)
        return jsonify({
            'message': 'Login realizado com sucesso',
            'usuario': {
                'id': usuario.id,
                'nome': usuario.nome_completo,
                'email': usuario.email,
                'tipo': usuario.tipo_usuario
            }
        }), 200
    else:
        return jsonify({'error': 'Credenciais inválidas'}), 401

@bp.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    """API de logout"""
    logout_user()
    return jsonify({'message': 'Logout realizado com sucesso'}), 200