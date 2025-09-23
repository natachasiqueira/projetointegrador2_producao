import pytest
from datetime import datetime, date, time
from app import db
from app.models import Usuario, Psicologo, Paciente, Agendamento, Prontuario, Sessao, HorarioAtendimento

class TestUsuario:
    """Testes para o modelo Usuario"""
    
    def test_criar_usuario(self, app):
        """Testa a criação de um usuário"""
        with app.app_context():
            usuario = Usuario(
                nome_completo='João Silva',
                email='joao@teste.com',
                telefone='(11) 99999-9999',
                tipo_usuario='paciente'
            )
            usuario.set_senha('senha123')
            
            db.session.add(usuario)
            db.session.commit()
            
            assert usuario.id is not None
            assert usuario.nome_completo == 'João Silva'
            assert usuario.email == 'joao@teste.com'
            assert usuario.tipo_usuario == 'paciente'
            assert usuario.ativo is True
            assert usuario.check_senha('senha123') is True
            assert usuario.check_senha('senha_errada') is False
    
    def test_usuario_unique_email(self, app):
        """Testa que o email deve ser único"""
        with app.app_context():
            # Primeiro usuário
            usuario1 = Usuario(
                nome_completo='João Silva',
                email='joao@teste.com',
                tipo_usuario='paciente'
            )
            usuario1.set_senha('senha123')
            db.session.add(usuario1)
            db.session.commit()
            
            # Segundo usuário com mesmo email
            usuario2 = Usuario(
                nome_completo='Maria Silva',
                email='joao@teste.com',
                tipo_usuario='psicologo'
            )
            usuario2.set_senha('senha456')
            db.session.add(usuario2)
            
            with pytest.raises(Exception):
                db.session.commit()

class TestPsicologo:
    """Testes para o modelo Psicologo"""
    
    def test_criar_psicologo(self, app):
        """Testa a criação de um psicólogo"""
        with app.app_context():
            # Criar usuário primeiro
            usuario = Usuario(
                nome_completo='Dr. Ana Santos',
                email='ana@teste.com',
                tipo_usuario='psicologo'
            )
            usuario.set_senha('senha123')
            db.session.add(usuario)
            db.session.commit()
            
            # Criar psicólogo
            psicologo = Psicologo(
                usuario_id=usuario.id
            )
            db.session.add(psicologo)
            db.session.commit()
            
            assert psicologo.id is not None
            assert psicologo.usuario_id == usuario.id
            assert psicologo.usuario.nome_completo == 'Dr. Ana Santos'

class TestPaciente:
    """Testes para o modelo Paciente"""
    
    def test_criar_paciente(self, app):
        """Testa a criação de um paciente"""
        with app.app_context():
            # Criar usuário primeiro
            usuario = Usuario(
                nome_completo='Maria Oliveira',
                email='maria@teste.com',
                tipo_usuario='paciente'
            )
            usuario.set_senha('senha123')
            db.session.add(usuario)
            db.session.commit()
            
            # Criar paciente
            paciente = Paciente(
                usuario_id=usuario.id
            )
            db.session.add(paciente)
            db.session.commit()
            
            assert paciente.id is not None
            assert paciente.usuario_id == usuario.id
            assert paciente.usuario.nome_completo == 'Maria Oliveira'

class TestAgendamento:
    """Testes para o modelo Agendamento"""
    
    def test_criar_agendamento(self, app):
        """Testa a criação de um agendamento"""
        with app.app_context():
            # Criar usuários
            usuario_psi = Usuario(
                nome_completo='Dr. Ana Santos',
                email='ana@teste.com',
                tipo_usuario='psicologo'
            )
            usuario_psi.set_senha('senha123')
            
            usuario_pac = Usuario(
                nome_completo='Maria Oliveira',
                email='maria@teste.com',
                tipo_usuario='paciente'
            )
            usuario_pac.set_senha('senha123')
            
            db.session.add_all([usuario_psi, usuario_pac])
            db.session.commit()
            
            # Criar psicólogo e paciente
            psicologo = Psicologo(usuario_id=usuario_psi.id)
            paciente = Paciente(usuario_id=usuario_pac.id, psicologo_id=1)
            
            db.session.add_all([psicologo, paciente])
            db.session.commit()
            
            # Criar agendamento
            agendamento = Agendamento(
                paciente_id=paciente.id,
                psicologo_id=psicologo.id,
                data_hora=datetime(2024, 3, 15, 14, 30),
                observacoes='Primeira consulta'
            )
            db.session.add(agendamento)
            db.session.commit()
            
            assert agendamento.id is not None
            assert agendamento.status == 'agendado'
            assert agendamento.data_hora == datetime(2024, 3, 15, 14, 30)
            assert agendamento.observacoes == 'Primeira consulta'

class TestHorarioAtendimento:
    """Testes para o modelo HorarioAtendimento"""
    
    def test_criar_horario_atendimento(self, app):
        """Testa a criação de horário de atendimento"""
        with app.app_context():
            # Criar usuário e psicólogo
            usuario = Usuario(
                nome_completo='Dr. Ana Santos',
                email='ana@teste.com',
                tipo_usuario='psicologo'
            )
            usuario.set_senha('senha123')
            db.session.add(usuario)
            db.session.commit()
            
            psicologo = Psicologo(usuario_id=usuario.id)
            db.session.add(psicologo)
            db.session.commit()
            
            # Criar horário de atendimento
            horario = HorarioAtendimento(
                psicologo_id=psicologo.id,
                dia_semana=1,  # Terça-feira
                hora_inicio=time(9, 0),
                hora_fim=time(17, 0)
            )
            db.session.add(horario)
            db.session.commit()
            
            assert horario.id is not None
            assert horario.dia_semana == 1
            assert horario.hora_inicio == time(9, 0)
            assert horario.hora_fim == time(17, 0)
            assert horario.ativo is True