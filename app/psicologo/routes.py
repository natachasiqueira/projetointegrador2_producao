from flask import render_template, request, redirect, url_for, flash, jsonify
from app.psicologo import bp
from app.models import Paciente, Psicologo, Agendamento, Prontuario, Sessao, HorarioAtendimento, db
from datetime import date, datetime, time, timedelta
from flask_login import login_required, current_user
from sqlalchemy import func, extract

def psicologo_required(f):
    """Decorator para verificar se o usuário é um psicólogo"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo_usuario != 'psicologo':
            flash('Acesso negado. Área restrita para psicólogos.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@psicologo_required
def dashboard():
    """Dashboard principal do psicólogo"""
    psicologo = Psicologo.query.filter_by(usuario_id=current_user.id).first()
    
    if not psicologo:
        flash('Perfil de psicólogo não encontrado.', 'error')
        return redirect(url_for('main.index'))
    
    # Estatísticas básicas
    hoje = date.today()
    mes_atual = hoje.month
    ano_atual = hoje.year
    
    # Total de pacientes únicos
    total_pacientes = db.session.query(Agendamento.paciente_id).filter_by(
        psicologo_id=psicologo.id
    ).distinct().count()
    
    # Consultas hoje
    consultas_hoje = Agendamento.query.filter_by(psicologo_id=psicologo.id).filter(
        func.date(Agendamento.data_hora) == hoje
    ).count()
    
    # Consultas este mês
    consultas_mes = Agendamento.query.filter_by(psicologo_id=psicologo.id).filter(
        extract('month', Agendamento.data_hora) == mes_atual,
        extract('year', Agendamento.data_hora) == ano_atual
    ).count()
    
    # Próximas consultas (próximos 7 dias)
    proximas_consultas = Agendamento.query.filter_by(psicologo_id=psicologo.id).filter(
        Agendamento.data_hora >= datetime.now(),
        func.date(Agendamento.data_hora) <= (datetime.now() + timedelta(days=7))
    ).order_by(Agendamento.data_hora).limit(5).all()
    
    # Consultas de hoje detalhadas
    consultas_hoje_detalhes = Agendamento.query.filter_by(psicologo_id=psicologo.id).filter(
        func.date(Agendamento.data_hora) == hoje
    ).order_by(Agendamento.data_hora).all()
    
    return render_template('psicologo/dashboard.html', 
                         title='Dashboard - Psicólogo',
                         psicologo=psicologo,
                         hoje=hoje,
                         total_pacientes=total_pacientes,
                         agendamentos_hoje=consultas_hoje_detalhes,
                         agendamentos_mes=consultas_mes,
                         proximos_agendamentos=proximas_consultas)

@bp.route('/perfil', methods=['GET', 'POST'])
@login_required
@psicologo_required
def perfil():
    """Página de perfil do psicólogo"""
    psicologo = Psicologo.query.filter_by(usuario_id=current_user.id).first()
    
    if not psicologo:
        flash('Perfil de psicólogo não encontrado.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            # Atualizar dados do usuário
            nome_completo = request.form.get('nome_completo', '').strip()
            telefone = request.form.get('telefone', '').strip()
            nova_senha = request.form.get('nova_senha', '').strip()
            confirmar_senha = request.form.get('confirmar_senha', '').strip()
            
            # Validações
            if not nome_completo:
                flash('Nome completo é obrigatório.', 'error')
                return render_template('psicologo/perfil.html', 
                                     title='Meu Perfil',
                                     psicologo=psicologo)
            
            # Validar senha se fornecida
            if nova_senha:
                if len(nova_senha) < 6:
                    flash('A nova senha deve ter pelo menos 6 caracteres.', 'error')
                    return render_template('psicologo/perfil.html', 
                                         title='Meu Perfil',
                                         psicologo=psicologo)
                
                if nova_senha != confirmar_senha:
                    flash('As senhas não coincidem.', 'error')
                    return render_template('psicologo/perfil.html', 
                                         title='Meu Perfil',
                                         psicologo=psicologo)
            
            # Atualizar dados do usuário
            current_user.nome_completo = nome_completo
            current_user.telefone = telefone
            
            # Atualizar senha se fornecida
            if nova_senha:
                current_user.set_senha(nova_senha)
            
            db.session.commit()
            flash('Dados atualizados com sucesso!', 'success')
            return redirect(url_for('psicologo.perfil'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar dados: {str(e)}', 'error')
        
    return render_template('psicologo/perfil.html', 
                         title='Meu Perfil',
                         psicologo=psicologo)

@bp.route('/calendario')
@login_required
@psicologo_required
def calendario():
    """Calendário de agendamentos do psicólogo"""
    psicologo = Psicologo.query.filter_by(usuario_id=current_user.id).first()
    
    if not psicologo:
        flash('Perfil de psicólogo não encontrado.', 'error')
        return redirect(url_for('main.index'))
    
    # Obter mês e ano dos parâmetros ou usar atual
    mes_param = request.args.get('mes', type=int)
    ano_param = request.args.get('ano', type=int)
    
    hoje = date.today()
    
    if mes_param and ano_param:
        mes_atual = mes_param
        ano_atual = ano_param
    else:
        mes_atual = hoje.month
        ano_atual = hoje.year
    
    # Nomes dos meses em português
    meses_pt = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    
    mes_nome = f"{meses_pt[mes_atual]} de {ano_atual}"
    
    # Calcular primeiro e último dia do mês
    primeiro_dia = date(ano_atual, mes_atual, 1)
    if mes_atual == 12:
        ultimo_dia = date(ano_atual + 1, 1, 1) - timedelta(days=1)
    else:
        ultimo_dia = date(ano_atual, mes_atual + 1, 1) - timedelta(days=1)
    
    # Buscar agendamentos do mês específico
    agendamentos_mes = Agendamento.query.filter(
        Agendamento.psicologo_id == psicologo.id,
        Agendamento.data_hora >= datetime.combine(primeiro_dia, datetime.min.time()),
        Agendamento.data_hora <= datetime.combine(ultimo_dia, datetime.max.time())
    ).order_by(Agendamento.data_hora).all()
    
    # Separar agendamentos futuros e passados
    agendamentos_futuros = [ag for ag in agendamentos_mes if ag.data_hora.date() >= hoje]
    agendamentos_passados = [ag for ag in agendamentos_mes if ag.data_hora.date() < hoje]
    
    # Calcular mês anterior e próximo
    if mes_atual == 1:
        mes_anterior = 12
        ano_anterior = ano_atual - 1
    else:
        mes_anterior = mes_atual - 1
        ano_anterior = ano_atual
    
    if mes_atual == 12:
        mes_proximo = 1
        ano_proximo = ano_atual + 1
    else:
        mes_proximo = mes_atual + 1
        ano_proximo = ano_atual
    
    return render_template('psicologo/calendario.html', 
                         title='Calendário',
                         agendamentos=agendamentos_mes,
                         agendamentos_futuros=agendamentos_futuros,
                         agendamentos_passados=agendamentos_passados,
                         mes_nome=meses_pt[mes_atual],
                         ano=ano_atual,
                         mes_atual=mes_atual,
                         mes_atual_num=mes_atual,
                         ano_atual=ano_atual,
                         mes_anterior=mes_anterior,
                         ano_anterior=ano_anterior,
                         mes_proximo=mes_proximo,
                         ano_proximo=ano_proximo)

@bp.route('/horarios-atendimento', methods=['GET', 'POST'])
@login_required
@psicologo_required
def horarios_atendimento():
    """Gestão de horários de atendimento do psicólogo"""
    psicologo = Psicologo.query.filter_by(usuario_id=current_user.id).first()
    
    if not psicologo:
        flash('Perfil de psicólogo não encontrado.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        try:
            # Remover horários existentes
            HorarioAtendimento.query.filter_by(psicologo_id=psicologo.id).delete()
            
            # Dias da semana (0=segunda, 1=terça, ..., 6=domingo)
            dias_semana = ['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo']
            
            for i, dia in enumerate(dias_semana):
                # Verificar se o dia está ativo
                ativo = request.form.get(f'{dia}_ativo') == 'on'
                
                if ativo:
                    # Horário da manhã
                    inicio_manha = request.form.get(f'{dia}_inicio_manha')
                    fim_manha = request.form.get(f'{dia}_fim_manha')
                    
                    if inicio_manha and fim_manha:
                        horario_manha = HorarioAtendimento(
                            psicologo_id=psicologo.id,
                            dia_semana=i,
                            hora_inicio=time.fromisoformat(inicio_manha),
                            hora_fim=time.fromisoformat(fim_manha),
                            ativo=True
                        )
                        db.session.add(horario_manha)
                    
                    # Horário da tarde
                    inicio_tarde = request.form.get(f'{dia}_inicio_tarde')
                    fim_tarde = request.form.get(f'{dia}_fim_tarde')
                    
                    if inicio_tarde and fim_tarde:
                        horario_tarde = HorarioAtendimento(
                            psicologo_id=psicologo.id,
                            dia_semana=i,
                            hora_inicio=time.fromisoformat(inicio_tarde),
                            hora_fim=time.fromisoformat(fim_tarde),
                            ativo=True
                        )
                        db.session.add(horario_tarde)
            
            db.session.commit()
            flash('Horários de atendimento atualizados com sucesso!', 'success')
            return redirect(url_for('psicologo.horarios_atendimento'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao salvar horários: {str(e)}', 'error')
    
    # Buscar horários existentes
    horarios_existentes = HorarioAtendimento.query.filter_by(psicologo_id=psicologo.id).all()
    
    # Organizar horários por dia da semana
    horarios_por_dia = {}
    for horario in horarios_existentes:
        dia = horario.dia_semana
        if dia not in horarios_por_dia:
            horarios_por_dia[dia] = []
        horarios_por_dia[dia].append(horario)
    
    return render_template('psicologo/horarios_atendimento.html', 
                         title='Horários de Atendimento',
                         psicologo=psicologo,
                         horarios_por_dia=horarios_por_dia)


# ==================== SISTEMA DE PRONTUÁRIOS ====================

@bp.route('/prontuarios')
@login_required
@psicologo_required
def prontuarios():
    """Lista todos os pacientes do psicólogo para acesso aos prontuários"""
    psicologo = Psicologo.query.filter_by(usuario_id=current_user.id).first()
    
    # Buscar todos os pacientes que têm agendamentos com este psicólogo
    pacientes = db.session.query(Paciente).join(Agendamento).filter(
        Agendamento.psicologo_id == psicologo.id
    ).distinct().all()
    
    # Buscar termo de pesquisa
    search = request.args.get('search', '')
    if search:
        pacientes = [p for p in pacientes if search.lower() in p.usuario.nome_completo.lower() or search.lower() in p.usuario.email.lower()]
    
    return render_template('psicologo/prontuarios.html', 
                         title='Prontuários',
                         pacientes=pacientes,
                         search=search)


@bp.route('/prontuario/<int:paciente_id>')
@login_required
@psicologo_required
def prontuario_individual(paciente_id):
    """Exibe o prontuário individual de um paciente"""
    psicologo = Psicologo.query.filter_by(usuario_id=current_user.id).first()
    
    # Verificar se o paciente tem agendamentos com este psicólogo
    paciente = db.session.query(Paciente).join(Agendamento).filter(
        Paciente.id == paciente_id,
        Agendamento.psicologo_id == psicologo.id
    ).first()
    
    if not paciente:
        flash('Paciente não encontrado ou você não tem permissão para acessar este prontuário.', 'error')
        return redirect(url_for('psicologo.prontuarios'))
    
    # Buscar ou criar prontuário
    prontuario = Prontuario.query.filter_by(
        paciente_id=paciente_id,
        psicologo_id=psicologo.id
    ).first()
    
    if not prontuario:
        prontuario = Prontuario(
            paciente_id=paciente_id,
            psicologo_id=psicologo.id,
            observacoes_gerais=""
        )
        db.session.add(prontuario)
        db.session.commit()
    
    # Buscar sessões do prontuário
    sessoes = Sessao.query.filter_by(prontuario_id=prontuario.id).order_by(Sessao.data_sessao.desc()).all()
    
    # Buscar agendamentos do paciente com este psicólogo
    agendamentos = Agendamento.query.filter_by(
        paciente_id=paciente_id,
        psicologo_id=psicologo.id
    ).order_by(Agendamento.data_hora.desc()).all()
    
    return render_template('psicologo/prontuario_individual.html',
                         title=f'Prontuário - {paciente.usuario.nome_completo}',
                         paciente=paciente,
                         prontuario=prontuario,
                         sessoes=sessoes,
                         agendamentos=agendamentos)


@bp.route('/paciente/<int:paciente_id>/historico')
@login_required
@psicologo_required
def historico_paciente(paciente_id):
    """API para buscar histórico de sessões do paciente"""
    psicologo = Psicologo.query.filter_by(usuario_id=current_user.id).first()
    
    # Verificar permissão
    paciente = db.session.query(Paciente).join(Agendamento).filter(
        Paciente.id == paciente_id,
        Agendamento.psicologo_id == psicologo.id
    ).first()
    
    if not paciente:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Buscar prontuário
    prontuario = Prontuario.query.filter_by(
        paciente_id=paciente_id,
        psicologo_id=psicologo.id
    ).first()
    
    if not prontuario:
        return jsonify({'sessoes': []})
    
    # Buscar sessões
    sessoes = Sessao.query.filter_by(prontuario_id=prontuario.id).order_by(Sessao.data_sessao.desc()).all()
    
    sessoes_data = []
    for sessao in sessoes:
        sessoes_data.append({
            'id': sessao.id,
            'data_sessao': sessao.data_sessao.strftime('%d/%m/%Y'),
            'anotacoes': sessao.anotacoes,
            'data_criacao': sessao.data_criacao.strftime('%d/%m/%Y %H:%M')
        })
    
    return jsonify({'sessoes': sessoes_data})


@bp.route('/paciente/<int:paciente_id>/anotacao', methods=['POST'])
@login_required
@psicologo_required
def adicionar_anotacao(paciente_id):
    """API para adicionar nova anotação/sessão ao prontuário"""
    psicologo = Psicologo.query.filter_by(usuario_id=current_user.id).first()
    
    # Verificar permissão
    paciente = db.session.query(Paciente).join(Agendamento).filter(
        Paciente.id == paciente_id,
        Agendamento.psicologo_id == psicologo.id
    ).first()
    
    if not paciente:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Buscar ou criar prontuário
    prontuario = Prontuario.query.filter_by(
        paciente_id=paciente_id,
        psicologo_id=psicologo.id
    ).first()
    
    if not prontuario:
        prontuario = Prontuario(
            paciente_id=paciente_id,
            psicologo_id=psicologo.id,
            observacoes_gerais=""
        )
        db.session.add(prontuario)
        db.session.commit()
    
    # Obter dados da requisição
    data = request.get_json()
    if not data or 'anotacoes' not in data:
        return jsonify({'error': 'Anotações são obrigatórias'}), 400
    
    # Criar nova sessão
    nova_sessao = Sessao(
        prontuario_id=prontuario.id,
        data_sessao=datetime.strptime(data.get('data_sessao', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
        anotacoes=data['anotacoes']
    )
    
    db.session.add(nova_sessao)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Anotação adicionada com sucesso',
        'sessao': {
            'id': nova_sessao.id,
            'data_sessao': nova_sessao.data_sessao.strftime('%d/%m/%Y'),
            'anotacoes': nova_sessao.anotacoes,
            'data_criacao': nova_sessao.data_criacao.strftime('%d/%m/%Y %H:%M')
        }
    })


@bp.route('/prontuario/<int:paciente_id>/recorrencia', methods=['POST'])
@login_required
@psicologo_required
def configurar_recorrencia(paciente_id):
    """Configura recorrência de agendamentos para um paciente"""
    psicologo = Psicologo.query.filter_by(usuario_id=current_user.id).first()
    
    # Verificar permissão
    paciente = db.session.query(Paciente).join(Agendamento).filter(
        Paciente.id == paciente_id,
        Agendamento.psicologo_id == psicologo.id
    ).first()
    
    if not paciente:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Obter dados da requisição
    data = request.get_json()
    if not data or 'dia_semana' not in data or 'horario' not in data:
        return jsonify({'error': 'Dia da semana e horário são obrigatórios'}), 400
    
    try:
        dia_semana = int(data['dia_semana'])  # 0=Segunda, 1=Terça, etc.
        horario = datetime.strptime(data['horario'], '%H:%M').time()
        
        # Buscar ou criar prontuário
        prontuario = Prontuario.query.filter_by(
            paciente_id=paciente_id,
            psicologo_id=psicologo.id
        ).first()
        
        if not prontuario:
            prontuario = Prontuario(
                paciente_id=paciente_id,
                psicologo_id=psicologo.id,
                observacoes_gerais=""
            )
            db.session.add(prontuario)
        
        # Atualizar recorrência no prontuário
        prontuario.recorrencia_dia_semana = dia_semana
        prontuario.recorrencia_horario = horario
        
        # Gerar 12 agendamentos futuros
        agendamentos_criados = 0
        data_atual = datetime.now().date()
        
        # Encontrar a próxima data do dia da semana especificado
        dias_ate_proximo = (dia_semana - data_atual.weekday()) % 7
        if dias_ate_proximo == 0:
            dias_ate_proximo = 7  # Se for hoje, começar na próxima semana
        
        proxima_data = data_atual + timedelta(days=dias_ate_proximo)
        
        for i in range(12):
            data_agendamento = proxima_data + timedelta(weeks=i)
            
            # Verificar se já existe agendamento nesta data e horário
            agendamento_existente = Agendamento.query.filter_by(
                paciente_id=paciente_id,
                psicologo_id=psicologo.id,
                data_agendamento=data_agendamento,
                horario=horario
            ).first()
            
            if not agendamento_existente:
                novo_agendamento = Agendamento(
                    paciente_id=paciente_id,
                    psicologo_id=psicologo.id,
                    data_agendamento=data_agendamento,
                    horario=horario,
                    status='agendado'
                )
                db.session.add(novo_agendamento)
                agendamentos_criados += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Recorrência configurada com sucesso. {agendamentos_criados} agendamentos criados.',
            'agendamentos_criados': agendamentos_criados
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao configurar recorrência: {str(e)}'}), 500


@bp.route('/agendamento/<int:agendamento_id>/marcar-ausente', methods=['POST'])
@login_required
@psicologo_required
def marcar_ausente(agendamento_id):
    """Marcar consulta como ausente"""
    try:
        psicologo = Psicologo.query.filter_by(usuario_id=current_user.id).first()
        
        # Buscar o agendamento
        agendamento = Agendamento.query.filter_by(
            id=agendamento_id,
            psicologo_id=psicologo.id
        ).first()
        
        if not agendamento:
            return jsonify({'error': 'Agendamento não encontrado'}), 404
        
        # Atualizar status
        agendamento.status = 'ausencia'
        db.session.commit()
        
        flash('Consulta marcada como ausência com sucesso!', 'success')
        return jsonify({'success': True, 'message': 'Consulta marcada como ausência'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao marcar ausência: {str(e)}'}), 500


@bp.route('/agendamento/<int:agendamento_id>/marcar-realizada', methods=['POST'])
@login_required
@psicologo_required
def marcar_realizada(agendamento_id):
    """Marcar consulta como realizada"""
    try:
        psicologo = Psicologo.query.filter_by(usuario_id=current_user.id).first()
        
        # Buscar o agendamento
        agendamento = Agendamento.query.filter_by(
            id=agendamento_id,
            psicologo_id=psicologo.id
        ).first()
        
        if not agendamento:
            return jsonify({'error': 'Agendamento não encontrado'}), 404
        
        # Atualizar status
        agendamento.status = 'realizado'
        db.session.commit()
        
        flash('Consulta marcada como realizado com sucesso!', 'success')
        return jsonify({'success': True, 'message': 'Consulta marcada como realizado'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao marcar como realizado: {str(e)}'}), 500