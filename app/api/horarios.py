from flask import jsonify, request
from datetime import datetime, timedelta
from app.models import Psicologo, HorarioAtendimento, Agendamento
from . import bp

# API para listar horários disponíveis
@bp.route('/psicologos/<int:id>/horarios_disponiveis', methods=['GET'])
def listar_horarios_disponiveis(id):
    psicologo = Psicologo.query.get_or_404(id)
    data_str = request.args.get('data')
    
    if not data_str:
        return jsonify({'erro': 'Data não informada'}), 400
    
    try:
        data = datetime.strptime(data_str, '%d/%m/%Y').date()
    except ValueError:
        return jsonify({'erro': 'Formato de data inválido'}), 400
    
    # Verificar se o psicólogo atende neste dia
    dia_semana = data.weekday()
    horario_atendimento = HorarioAtendimento.query.filter_by(
        psicologo_id=psicologo.id,
        dia_semana=dia_semana
    ).first()
    
    if not horario_atendimento:
        return jsonify({'horarios_disponiveis': []})
    
    # Gerar horários de 15 em 15 minutos (00, 15, 30, 45)
    hora_atual = horario_atendimento.hora_inicio
    hora_fim = horario_atendimento.hora_fim
    
    horarios = []
    while hora_atual < hora_fim:
        # Verificar se os minutos são 00, 15, 30 ou 45
        if hora_atual.minute in [0, 15, 30, 45]:
            horario = hora_atual.strftime('%H:%M')
            horarios.append(horario)
        
        # Avançar para o próximo intervalo de 15 minutos
        hora_atual = (datetime.combine(datetime.today(), hora_atual) + timedelta(minutes=15)).time()
    
    # Remover horários já agendados
    agendamentos = Agendamento.query.filter_by(
        psicologo_id=psicologo.id,
        data=data,
        status='confirmado'
    ).all()
    
    horarios_ocupados = [agendamento.hora_inicio.strftime('%H:%M') for agendamento in agendamentos]
    horarios_disponiveis = [horario for horario in horarios if horario not in horarios_ocupados]
    
    return jsonify({'horarios_disponiveis': horarios_disponiveis})