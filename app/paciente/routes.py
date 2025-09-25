from flask import render_template, flash, redirect, url_for, request, session, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from app.paciente import bp
from app.models import Paciente, Agendamento, Psicologo, Usuario, Prontuario, HorarioAtendimento, db
from datetime import datetime, timedelta, timezone

@bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard do paciente"""
    from datetime import datetime
    
    # Buscar o paciente atual
    paciente = Paciente.query.filter_by(usuario_id=current_user.id).first()
    
    if not paciente:
        flash('Perfil de paciente não encontrado.', 'error')
        return redirect(url_for('auth.login'))
    
    # Buscar próximos agendamentos
    proximos_agendamentos = Agendamento.query.filter(
        Agendamento.paciente_id == paciente.id,
        Agendamento.data_hora >= datetime.now(timezone.utc),
        Agendamento.status.in_(['agendado', 'confirmado'])
    ).order_by(Agendamento.data_hora.asc()).limit(5).all()
    
    # Buscar psicólogos disponíveis para agendamento
    psicologos = Psicologo.query.all()
    
    return render_template('paciente/dashboard.html', 
                         proximos_agendamentos=proximos_agendamentos,
                         psicologos=psicologos)

@bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    """Perfil do paciente"""
    if request.method == 'POST':
        try:
            # Atualizar dados pessoais
            current_user.nome_completo = request.form.get('nome', '').strip()
            current_user.email = request.form.get('email', '').strip()
            current_user.telefone = request.form.get('telefone', '').strip()
            
            # Buscar o paciente relacionado (não é mais necessário para telefone)
            paciente = Paciente.query.filter_by(usuario_id=current_user.id).first()
            
            # Verificar se uma nova senha foi fornecida
            nova_senha = request.form.get('nova_senha', '').strip()
            confirmar_senha = request.form.get('confirmar_senha', '').strip()
            
            if nova_senha:
                if nova_senha != confirmar_senha:
                    flash('As senhas não coincidem.', 'error')
                    return redirect(url_for('paciente.perfil'))
                
                if len(nova_senha) < 6:
                    flash('A senha deve ter pelo menos 6 caracteres.', 'error')
                    return redirect(url_for('paciente.perfil'))
                
                current_user.senha_hash = generate_password_hash(nova_senha)
            
            # Salvar alterações
            db.session.commit()
            flash('Perfil atualizado com sucesso!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao atualizar perfil. Tente novamente.', 'error')
            print(f"Erro ao atualizar perfil: {e}")
        
        return redirect(url_for('paciente.perfil'))
    
    # GET request - buscar dados do paciente
    paciente = Paciente.query.filter_by(usuario_id=current_user.id).first()
    
    # Buscar agendamentos futuros e passados
    agendamentos_futuros = []
    agendamentos_passados = []
    
    if paciente:
        agendamentos = Agendamento.query.filter_by(paciente_id=paciente.id).order_by(Agendamento.data_hora.desc()).all()
        agora = datetime.now(timezone.utc)
        
        for agendamento in agendamentos:
            if agendamento.data_hora >= agora:
                agendamentos_futuros.append(agendamento)
            else:
                agendamentos_passados.append(agendamento)
    
    return render_template('paciente/perfil.html', 
                         paciente=paciente or {},
                         agendamentos_futuros=agendamentos_futuros,
                         agendamentos_passados=agendamentos_passados)

@bp.route('/agendamentos')
@login_required
def agendamentos():
    """Lista de agendamentos do paciente"""
    from datetime import datetime
    
    # Buscar o paciente atual
    paciente = Paciente.query.filter_by(usuario_id=current_user.id).first()
    
    if not paciente:
        flash('Perfil de paciente não encontrado.', 'error')
        return redirect(url_for('paciente.dashboard'))
    
    # Buscar todos os agendamentos do paciente
    agendamentos_list = Agendamento.query.filter_by(paciente_id=paciente.id).order_by(Agendamento.data_hora.desc()).all()
    
    return render_template('paciente/agendamentos.html', agendamentos=agendamentos_list, moment=datetime)

@bp.route('/agendar', methods=['POST'])
@login_required
def agendar():
    """Agendar nova consulta via AJAX"""
    if request.method == 'POST':
        try:
            # Buscar o paciente atual
            paciente = Paciente.query.filter_by(usuario_id=current_user.id).first()
            
            if not paciente:
                flash('Perfil de paciente não encontrado.', 'error')
                return redirect(url_for('paciente.dashboard'))
            
            # Obter dados do formulário
            psicologo_id = request.form.get('psicologo_id')
            data_str = request.form.get('data')
            horario_str = request.form.get('horario')
            observacoes = request.form.get('observacoes', '').strip()
            
            # Validações
            if not all([psicologo_id, data_str, horario_str]):
                flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
                return redirect(url_for('paciente.agendamentos'))
            
            # Verificar se o psicólogo existe
            psicologo = Psicologo.query.get(psicologo_id)
            if not psicologo:
                flash('Psicólogo não encontrado.', 'error')
                return redirect(url_for('paciente.agendamentos'))
            
            # Converter data e horário em um único datetime
            data_hora_str = f"{data_str} {horario_str}"
            data_hora = datetime.strptime(data_hora_str, '%Y-%m-%d %H:%M')
            
            # Verificar se a data não é no passado
            if data_hora < datetime.now(timezone.utc):
                flash('Não é possível agendar consultas para datas e horários passados.', 'error')
                return redirect(url_for('paciente.agendamentos'))
            
            # Criar novo agendamento
            novo_agendamento = Agendamento(
                paciente_id=paciente.id,
                psicologo_id=psicologo_id,
                data_hora=data_hora,
                status='agendado',
                observacoes=observacoes
            )
            
            db.session.add(novo_agendamento)
            db.session.commit()
            
            flash('Consulta agendada com sucesso!', 'success')
            return redirect(url_for('paciente.agendamentos'))
            
        except Exception as e:
            db.session.rollback()
            flash('Erro ao agendar consulta. Tente novamente.', 'error')
            return redirect(url_for('paciente.agendamentos'))

# APIs para o modal de agendamento
@bp.route('/api/psicologos')
@login_required
def api_psicologos():
    """API para buscar psicólogos disponíveis e verificar se paciente tem psicólogo fixo"""
    try:
        # Buscar o paciente atual
        paciente = Paciente.query.filter_by(usuario_id=current_user.id).first()
        
        if not paciente:
            return jsonify({'error': 'Perfil de paciente não encontrado'}), 404
        
        # Buscar todos os agendamentos do paciente (não cancelados)
        agendamentos_paciente = Agendamento.query.filter(
            Agendamento.paciente_id == paciente.id,
            Agendamento.status != 'cancelado'
        ).all()
        
        # Verificar se há psicólogo fixo (paciente já tem consultas)
        psicologo_fixo_id = None
        if agendamentos_paciente:
            # Se há agendamentos, usar o psicólogo do primeiro agendamento como fixo
            psicologo_fixo_id = agendamentos_paciente[0].psicologo_id
        
        # Buscar todos os psicólogos disponíveis (excluindo administradores)
        psicologos = Psicologo.query.join(Usuario).filter(Usuario.tipo_usuario == 'psicologo').all()
        psicologos_data = []
        
        if psicologo_fixo_id:
            # Se há psicólogo fixo, retornar apenas ele (se não for admin)
            psicologo_fixo = Psicologo.query.join(Usuario).filter(
                Psicologo.id == psicologo_fixo_id,
                Usuario.tipo_usuario == 'psicologo'
            ).first()
            if psicologo_fixo:
                psicologos_data.append({
                    'id': psicologo_fixo.id,
                    'nome': psicologo_fixo.usuario.nome_completo,
                    'fixo': True
                })
        else:
            # Se não há psicólogo fixo, retornar todos os psicólogos (excluindo admins)
            for psicologo in psicologos:
                psicologos_data.append({
                    'id': psicologo.id,
                    'nome': psicologo.usuario.nome_completo,
                    'fixo': False
                })
        
        return jsonify({
            'psicologos': psicologos_data
        })
        
    except Exception as e:
        print(f"Erro na API de psicólogos: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@bp.route('/api/horarios-disponiveis')
@login_required
def api_horarios_disponiveis():
    """API para buscar horários disponíveis de um psicólogo em uma data"""
    try:
        psicologo_id = request.args.get('psicologo_id')
        data_str = request.args.get('data')
        
        if not psicologo_id or not data_str:
            return jsonify({'error': 'Parâmetros obrigatórios: psicologo_id e data'}), 400
        
        # Converter string para data
        data = datetime.strptime(data_str, '%Y-%m-%d').date()
        
        # Buscar psicólogo
        psicologo = Psicologo.query.get(psicologo_id)
        if not psicologo:
            return jsonify({'error': 'Psicólogo não encontrado'}), 404
        
        # Verificar se a data não é no passado
        if data < datetime.now().date():
            return jsonify({'horarios': []})
        
        # Verificar se o psicólogo atende neste dia da semana
        dia_semana = data.weekday()  # 0=Segunda, 1=Terça, ..., 6=Domingo
        
        horarios_atendimento = HorarioAtendimento.query.filter_by(
            psicologo_id=psicologo_id,
            dia_semana=dia_semana,
            ativo=True
        ).all()  # Buscar TODOS os horários do dia (pode ter múltiplos turnos)
        
        if not horarios_atendimento:
            return jsonify({'horarios': []})
        
        # Gerar horários disponíveis baseados em TODOS os turnos do psicólogo
        horarios_disponiveis = []
        
        for horario_atendimento in horarios_atendimento:
            hora_atual = horario_atendimento.hora_inicio
            hora_fim = horario_atendimento.hora_fim
            
            while hora_atual < hora_fim:
                # Gerar slots de 1 hora
                horario_str = hora_atual.strftime('%H:%M')
                if horario_str not in horarios_disponiveis:  # Evitar duplicatas
                    horarios_disponiveis.append(horario_str)
                
                # Avançar para a próxima hora
                hora_atual = (datetime.combine(datetime.today(), hora_atual) + timedelta(hours=1)).time()
        
        # Ordenar os horários
        horarios_disponiveis.sort()
        
        # Buscar agendamentos já existentes nesta data para este psicólogo
        data_inicio = datetime.combine(data, datetime.min.time())
        data_fim = datetime.combine(data, datetime.max.time())
        
        agendamentos_existentes = Agendamento.query.filter(
            Agendamento.psicologo_id == psicologo_id,
            Agendamento.data_hora >= data_inicio,
            Agendamento.data_hora <= data_fim,
            Agendamento.status.in_(['agendado', 'confirmado'])
        ).all()
        
        horarios_ocupados = [ag.data_hora.strftime('%H:%M') for ag in agendamentos_existentes]
        
        # Filtrar horários ocupados
        horarios_finais = [h for h in horarios_disponiveis if h not in horarios_ocupados]
        
        return jsonify({'horarios': horarios_finais})
        
    except Exception as e:
        print(f"Erro na API de horários: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@bp.route('/agendar_modal', methods=['POST'])
@login_required
def agendar_modal():
    """Processar agendamento via modal"""
    try:
        # Buscar o paciente atual
        paciente = Paciente.query.filter_by(usuario_id=current_user.id).first()
        
        if not paciente:
            flash('Perfil de paciente não encontrado.', 'error')
            return redirect(url_for('paciente.dashboard'))
        
        # Obter dados do formulário
        psicologo_id = request.form.get('psicologo_id')
        data_str = request.form.get('data')
        horario_str = request.form.get('horario')
        observacoes = request.form.get('observacoes', '')
        
        # Validações
        if not psicologo_id or not data_str or not horario_str:
            flash('Todos os campos obrigatórios devem ser preenchidos.', 'error')
            return redirect(url_for('paciente.dashboard'))
        
        # Converter data e horário em datetime
        data_hora_str = f"{data_str} {horario_str}"
        data_hora = datetime.strptime(data_hora_str, '%Y-%m-%d %H:%M')
        
        # Verificar se psicólogo existe
        psicologo = Psicologo.query.get(psicologo_id)
        if not psicologo:
            flash('Psicólogo não encontrado.', 'error')
            return redirect(url_for('paciente.dashboard'))
        
        # Verificar se paciente já tem psicólogo fixo
        agendamentos_paciente = Agendamento.query.filter(
            Agendamento.paciente_id == paciente.id,
            Agendamento.status != 'cancelado'
        ).all()
        
        # Se paciente já tem agendamentos, deve manter o mesmo psicólogo
        if agendamentos_paciente and str(agendamentos_paciente[0].psicologo_id) != psicologo_id:
            flash('Para manter a continuidade do tratamento, você deve agendar com o mesmo psicólogo das consultas anteriores.', 'warning')
            return redirect(url_for('paciente.dashboard'))
        
        # Verificar se horário ainda está disponível
        conflito = Agendamento.query.filter_by(
            psicologo_id=psicologo_id,
            data_hora=data_hora,
            status='agendado'
        ).first()
        
        if conflito:
            flash('Este horário não está mais disponível.', 'error')
            return redirect(url_for('paciente.dashboard'))
        
        # Criar novo agendamento
        novo_agendamento = Agendamento(
            paciente_id=paciente.id,
            psicologo_id=psicologo_id,
            data_hora=data_hora,
            observacoes=observacoes,
            status='agendado'
        )
        
        db.session.add(novo_agendamento)
        
        # Se é o primeiro agendamento, criar prontuário
        if not agendamentos_paciente:
            prontuario_existente = Prontuario.query.filter_by(
                paciente_id=paciente.id,
                psicologo_id=psicologo_id
            ).first()
            
            if not prontuario_existente:
                novo_prontuario = Prontuario(
                    paciente_id=paciente.id,
                    psicologo_id=psicologo_id,
                    observacoes_gerais=f'Prontuário criado automaticamente no primeiro agendamento em {datetime.now().strftime("%d/%m/%Y %H:%M")}'
                )
                db.session.add(novo_prontuario)
        
        db.session.commit()
        
        flash(f'Consulta agendada com sucesso para {data_hora.strftime("%d/%m/%Y às %H:%M")} com Dr(a). {psicologo.usuario.nome_completo}!', 'success')
        
    except ValueError as e:
        flash('Formato de data ou horário inválido.', 'error')
        return redirect(url_for('paciente.dashboard'))
    except Exception as e:
        db.session.rollback()
        flash('Erro ao agendar consulta. Tente novamente.', 'error')
        print(f"Erro ao agendar consulta via modal: {e}")
    
    return redirect(url_for('paciente.dashboard'))
    
    return redirect(url_for('paciente.agendamentos'))

@bp.route('/confirmar/<int:agendamento_id>', methods=['POST'])
@login_required
def confirmar_agendamento(agendamento_id):
    """Confirmar agendamento"""
    try:
        # Buscar o paciente atual
        paciente = Paciente.query.filter_by(usuario_id=current_user.id).first()
        
        if not paciente:
            return jsonify({'error': 'Perfil de paciente não encontrado'}), 404
        
        # Buscar o agendamento
        agendamento = Agendamento.query.filter_by(
            id=agendamento_id, 
            paciente_id=paciente.id
        ).first()
        
        if not agendamento:
            return jsonify({'error': 'Agendamento não encontrado'}), 404
        
        # Verificar se pode confirmar (apenas agendamentos com status 'agendado')
        if agendamento.status != 'agendado':
            return jsonify({'error': 'Apenas consultas agendadas podem ser confirmadas'}), 400
        
        # Atualizar status para confirmado
        agendamento.status = 'confirmado'
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Consulta confirmada com sucesso'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao confirmar consulta: {str(e)}'}), 500

@bp.route('/cancelar/<int:agendamento_id>', methods=['POST'])
@login_required
def cancelar_agendamento(agendamento_id):
    """Cancelar agendamento"""
    try:
        # Buscar o paciente atual
        paciente = Paciente.query.filter_by(usuario_id=current_user.id).first()
        
        if not paciente:
            flash('Perfil de paciente não encontrado.', 'error')
            return redirect(url_for('paciente.agendamentos'))
        
        # Buscar o agendamento
        agendamento = Agendamento.query.filter_by(
            id=agendamento_id, 
            paciente_id=paciente.id
        ).first()
        
        if not agendamento:
            flash('Agendamento não encontrado.', 'error')
            return redirect(url_for('paciente.agendamentos'))
        
        # Verificar se pode cancelar (não pode cancelar consultas já realizadas)
        if agendamento.status == 'realizado':
            flash('Não é possível cancelar consultas já realizadas.', 'error')
            return redirect(url_for('paciente.agendamentos'))
        
        # Atualizar status para cancelado
        agendamento.status = 'cancelado'
        db.session.commit()
        
        flash('Consulta cancelada com sucesso.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Erro ao cancelar consulta. Tente novamente.', 'error')
        print(f"Erro ao cancelar consulta: {e}")
    
    return redirect(url_for('paciente.agendamentos'))

@bp.route('/reagendar_consulta/<int:agendamento_id>')
@login_required
def reagendar_consulta(agendamento_id):
    """Reagendar consulta"""
    # Buscar o paciente atual
    paciente = Paciente.query.filter_by(usuario_id=current_user.id).first()
    
    if not paciente:
        flash('Perfil de paciente não encontrado.', 'error')
        return redirect(url_for('paciente.agendamentos'))
    
    # Buscar o agendamento
    agendamento = Agendamento.query.filter_by(
        id=agendamento_id, 
        paciente_id=paciente.id
    ).first()
    
    if not agendamento:
        flash('Agendamento não encontrado.', 'error')
        return redirect(url_for('paciente.agendamentos'))
    
    # Por enquanto, redirecionar para nova consulta
    # TODO: Implementar funcionalidade específica de reagendamento
    flash('Funcionalidade de reagendamento será implementada em breve. Por favor, cancele a consulta atual e agende uma nova.', 'info')
    return redirect(url_for('paciente.agendamentos'))