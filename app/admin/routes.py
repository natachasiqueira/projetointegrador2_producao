import pytz
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Usuario, Psicologo, Paciente, Agendamento, Admin, db
from sqlalchemy import func, case, String, cast
from functools import wraps

def admin_required(f):
    """Decorator para verificar se o usuário é admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo_usuario != 'admin':
            flash('Acesso negado. Apenas administradores podem acessar esta área.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def init_routes(admin):
    """Inicializa as rotas do admin"""
    
    @admin.route('/dashboard')
    @login_required
    @admin_required
    def dashboard():
        """Dashboard administrativo"""
        # Estatísticas básicas (excluindo administradores dos psicólogos)
        total_pacientes = Paciente.query.count()
        total_psicologos = Psicologo.query.join(Usuario).filter(Usuario.tipo_usuario == 'psicologo').count()
        total_agendamentos = Agendamento.query.count()
        
        # Dados reais para os gráficos
        from datetime import datetime, timedelta
        
        # Defina o fuso horário para UTC para evitar erros de comparação
        agora_utc = datetime.now(pytz.utc)
        data_limite = agora_utc - timedelta(days=180)  # aproximadamente 6 meses

        # Agendamentos por mês (últimos 6 meses)
        agendamentos_query = db.session.query(
            func.to_char(Agendamento.data_hora, 'MM').label('mes_num'),
            func.count(Agendamento.id).label('total')
        ).filter(
            Agendamento.data_hora >= data_limite
        ).group_by(
            func.to_char(Agendamento.data_hora, 'MM')
        ).order_by(
            func.to_char(Agendamento.data_hora, 'MM')
        ).all()
        
        # Converter números dos meses para nomes
        meses_nomes = {
            '01': 'Jan', '02': 'Fev', '03': 'Mar', '04': 'Abr',
            '05': 'Mai', '06': 'Jun', '07': 'Jul', '08': 'Ago',
            '09': 'Set', '10': 'Out', '11': 'Nov', '12': 'Dez'
        }
        
        agendamentos_por_mes = []
        for item in agendamentos_query:
            mes_nome = meses_nomes.get(item.mes_num, item.mes_num)
            agendamentos_por_mes.append({'mes': mes_nome, 'total': item.total})
        
        # 1. Taxa de Retenção de Pacientes (por mês)
        # Primeiro, obter todos os meses com agendamentos
        meses_query = db.session.query(
            func.to_char(Agendamento.data_hora, 'YYYY-MM').label('mes')
        ).filter(
            Agendamento.data_hora >= data_limite,
            Agendamento.status.in_(['realizado', 'confirmado'])
        ).group_by(
            func.to_char(Agendamento.data_hora, 'YYYY-MM')
        ).all()
        
        taxa_retencao = []
        for mes_item in meses_query:
            mes = mes_item.mes
            
            # Total de pacientes únicos no mês
            total_pacientes = db.session.query(
                func.count(func.distinct(Agendamento.paciente_id))
            ).filter(
                func.to_char(Agendamento.data_hora, 'YYYY-MM') == mes,
                Agendamento.status.in_(['realizado', 'confirmado'])
            ).scalar() or 0
            
            # Pacientes que tiveram mais de 1 sessão no mês
            pacientes_multiplas_sessoes = db.session.query(
                Agendamento.paciente_id
            ).filter(
                func.to_char(Agendamento.data_hora, 'YYYY-MM') == mes,
                Agendamento.status.in_(['realizado', 'confirmado'])
            ).group_by(
                Agendamento.paciente_id
            ).having(
                func.count(Agendamento.id) >= 2
            ).count()
            
            if total_pacientes > 0:
                taxa = (pacientes_multiplas_sessoes / total_pacientes) * 100
                taxa_retencao.append({
                    'mes': mes,
                    'taxa': round(taxa, 1)
                })
            else:
                taxa_retencao.append({
                    'mes': mes,
                    'taxa': 0
                })
        
        # 2. Frequência de Sessões (distribuição)
        frequencia_query = db.session.query(
            Agendamento.paciente_id,
            func.count(Agendamento.id).label('total_sessoes')
        ).filter(
            Agendamento.status == 'realizado'
        ).group_by(Agendamento.paciente_id).all()
        
        distribuicao_sessoes = {'1-5': 0, '6-10': 0, '11-15': 0, '16+': 0}
        for item in frequencia_query:
            if item.total_sessoes <= 5:
                distribuicao_sessoes['1-5'] += 1
            elif item.total_sessoes <= 10:
                distribuicao_sessoes['6-10'] += 1
            elif item.total_sessoes <= 15:
                distribuicao_sessoes['11-15'] += 1
            else:
                distribuicao_sessoes['16+'] += 1
        
        # 3. Taxa de Ocupação dos Profissionais
        ocupacao_query = db.session.query(
            Usuario.nome_completo.label('nome'),
            func.count(Agendamento.id).label('agendamentos_realizados')
        ).join(
            Psicologo, Usuario.id == Psicologo.usuario_id
        ).outerjoin(
            Agendamento, Psicologo.id == Agendamento.psicologo_id
        ).filter(
            Usuario.tipo_usuario == 'psicologo',
            Agendamento.data_hora >= data_limite
        ).group_by(
            Usuario.nome_completo
        ).all()
        
        # Assumindo 40 horas/semana * 4 semanas * 6 meses = 960 horas disponíveis
        horas_disponiveis = 960
        taxa_ocupacao = []
        for item in ocupacao_query:
            # Assumindo 1 hora por sessão
            ocupacao = (item.agendamentos_realizados / horas_disponiveis) * 100
            taxa_ocupacao.append({
                'nome': item.nome.split()[0],  # Primeiro nome
                'ocupacao': round(ocupacao, 1)
            })
        
        # 4. Taxa de No-Show (por mês)
        noshow_query = db.session.query(
            func.to_char(Agendamento.data_hora, 'YYYY-MM').label('mes'),
            func.count(Agendamento.id).label('total_agendamentos'),
            func.sum(case((Agendamento.status == 'ausencia', 1), else_=0)).label('faltas')
        ).filter(
            Agendamento.data_hora >= data_limite
        ).group_by(
            func.to_char(Agendamento.data_hora, 'YYYY-MM')
        ).all()
        
        taxa_noshow = []
        for item in noshow_query:
            if item.total_agendamentos > 0:
                taxa = (item.faltas / item.total_agendamentos) * 100
                mes_formatado = item.mes.split('-')[1] + '/' + item.mes.split('-')[0][-2:]
                taxa_noshow.append({'mes': mes_formatado, 'taxa': round(taxa, 1)})
        
        # 5. Número de Casos Ativos por Profissional
        casos_ativos_query = db.session.query(
            Usuario.nome_completo.label('nome'),
            func.count(func.distinct(Agendamento.paciente_id)).label('casos_ativos')
        ).join(
            Psicologo, Usuario.id == Psicologo.usuario_id
        ).outerjoin(
            Agendamento, Psicologo.id == Agendamento.psicologo_id
        ).filter(
            Usuario.tipo_usuario == 'psicologo',
            Agendamento.status.in_(['agendado', 'confirmado', 'realizado']),
            Agendamento.data_hora >= agora_utc - timedelta(days=90)  # últimos 3 meses
        ).group_by(
            Usuario.nome_completo
        ).all()
        
        casos_ativos = []
        for item in casos_ativos_query:
            casos_ativos.append({
                'nome': item.nome.split()[0],  # Primeiro nome
                'casos': item.casos_ativos
            })
        
        return render_template('admin/dashboard.html', 
                             total_pacientes=total_pacientes,
                             total_psicologos=total_psicologos,
                             total_agendamentos=total_agendamentos,
                             agendamentos_por_mes=agendamentos_por_mes,
                             taxa_retencao=taxa_retencao,
                             distribuicao_sessoes=distribuicao_sessoes,
                             taxa_ocupacao=taxa_ocupacao,
                             taxa_noshow=taxa_noshow,
                             casos_ativos=casos_ativos)
    
    @admin.route('/cadastrar_psicologo', methods=['GET', 'POST'])
    @login_required
    @admin_required
    def cadastrar_psicologo():
        """Cadastrar novo psicólogo"""
        if request.method == 'POST':
            nome = request.form.get('nome')
            email = request.form.get('email')
            telefone = request.form.get('telefone')
            senha = request.form.get('senha')
            confirmar_senha = request.form.get('confirmar_senha')
            
            # Validações básicas
            if not all([nome, email, telefone, senha, confirmar_senha]):
                flash('Todos os campos são obrigatórios!', 'error')
                return render_template('admin/cadastrar_psicologo.html')
            
            if senha != confirmar_senha:
                flash('As senhas não coincidem!', 'error')
                return render_template('admin/cadastrar_psicologo.html')
            
            if len(senha) < 6:
                flash('A senha deve ter pelo menos 6 caracteres!', 'error')
                return render_template('admin/cadastrar_psicologo.html')
            
            try:
                # Verificar se o email já existe
                usuario_existente = Usuario.query.filter_by(email=email).first()
                if usuario_existente:
                    flash('Este email já está cadastrado!', 'error')
                    return render_template('admin/cadastrar_psicologo.html')
                
                # Criar novo usuário
                novo_usuario = Usuario(
                    nome_completo=nome,
                    email=email,
                    telefone=telefone,
                    tipo_usuario='psicologo'
                )
                novo_usuario.set_senha(senha)
                
                db.session.add(novo_usuario)
                db.session.flush()  # Para obter o ID do usuário
                
                # Criar registro de psicólogo
                novo_psicologo = Psicologo(usuario_id=novo_usuario.id)
                db.session.add(novo_psicologo)
                
                db.session.commit()
                
                flash('Psicólogo cadastrado com sucesso!', 'success')
                return redirect(url_for('admin.dashboard'))
                
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao cadastrar psicólogo: {e}") # Adicionado para depuração
                return render_template('admin/cadastrar_psicologo.html')
        
        return render_template('admin/cadastrar_psicologo.html')