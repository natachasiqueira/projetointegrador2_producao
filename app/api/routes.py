from flask import jsonify, request
from . import bp
from app.models import Usuario, Paciente, Psicologo, Agendamento

@bp.route('/status')
def status():
    """Endpoint para verificar se a API está funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'API da Clínica Mentalize funcionando',
        'version': '1.0.0'
    })

# Importar rotas de horários
from . import horarios

# Placeholder para outras rotas da API que serão implementadas nos próximos módulos
@bp.route('/usuarios')
def usuarios():
    """Gestão de usuários - será implementada nos próximos módulos"""
    return jsonify({'message': 'Endpoint em desenvolvimento'})

@bp.route('/agendamentos')
def agendamentos():
    """Gestão de agendamentos - será implementada nos próximos módulos"""
    return jsonify({'message': 'Endpoint em desenvolvimento'})