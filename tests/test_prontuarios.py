import pytest
from datetime import datetime, date, time, timedelta
from app import create_app, db
from app.models import Usuario, Psicologo, Paciente, Agendamento, Prontuario, Sessao
from flask_login import login_user


@pytest.fixture
def app():
    """Criar aplicação de teste"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de teste"""
    return app.test_client()


@pytest.fixture
def psicologo_user(app):
    """Criar usuário psicólogo para testes"""
    with app.app_context():
        # Criar usuário
        usuario = Usuario(
            email='psicologo@teste.com',
            nome_completo='Dr. João Silva',
            telefone='11999999999',
            tipo_usuario='psicologo'
        )
        usuario.set_senha('senha123')
        db.session.add(usuario)
        db.session.commit()
        
        # Criar psicólogo
        psicologo = Psicologo(
            usuario_id=usuario.id,
        )
        db.session.add(psicologo)
        db.session.commit()
        
        # Refresh para garantir que os objetos estão anexados
        db.session.refresh(usuario)
        db.session.refresh(psicologo)
        
        return usuario, psicologo


@pytest.fixture
def paciente_user(app):
    """Criar usuário paciente para testes"""
    with app.app_context():
        # Criar usuário
        usuario = Usuario(
            email='paciente@teste.com',
            nome_completo='Maria Santos',
            telefone='11888888888',
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
        
        # Refresh para garantir que os objetos estão anexados
        db.session.refresh(usuario)
        db.session.refresh(paciente)
        
        return usuario, paciente


@pytest.fixture
def agendamento_teste(app, psicologo_user, paciente_user):
    """Criar agendamento de teste"""
    with app.app_context():
        _, psicologo = psicologo_user
        _, paciente = paciente_user
        
        agendamento = Agendamento(
            paciente_id=paciente.id,
            psicologo_id=psicologo.id,
            data_hora=datetime.combine(date.today(), time(14, 0)),
            status='agendado'
        )
        db.session.add(agendamento)
        db.session.commit()
        
        # Refresh para garantir que o objeto está anexado
        db.session.refresh(agendamento)
        
        return agendamento


class TestProntuarios:
    """Testes do Sistema de Prontuários"""
    
    def test_acesso_prontuarios_sem_login(self, client):
        """Testar acesso à página de prontuários sem login"""
        response = client.get('/psicologo/prontuarios')
        assert response.status_code == 302  # Redirect para login
    
    def test_acesso_prontuarios_com_psicologo(self, client, app, psicologo_user, agendamento_teste):
        """Testar acesso à página de prontuários com psicólogo logado"""
        with app.app_context():
            usuario, _ = psicologo_user
            
            with client.session_transaction() as sess:
                sess['_user_id'] = str(usuario.id)
                sess['_fresh'] = True
            
            response = client.get('/psicologo/prontuarios')
            assert response.status_code == 200
            assert b'Prontu\xc3\xa1rios' in response.data
    
    def test_acesso_prontuario_individual_valido(self, client, app, psicologo_user, paciente_user, agendamento_teste):
        """Testar acesso ao prontuário individual de um paciente válido"""
        with app.app_context():
            usuario, _ = psicologo_user
            _, paciente = paciente_user
            
            # Re-query para garantir que os objetos estão anexados à sessão atual
            paciente = Paciente.query.get(paciente.id)
            usuario = Usuario.query.get(usuario.id)
            
            with client.session_transaction() as sess:
                sess['_user_id'] = str(usuario.id)
                sess['_fresh'] = True
            
            response = client.get(f'/psicologo/prontuario/{paciente.id}')
            assert response.status_code == 200
            assert paciente.usuario.nome_completo.encode() in response.data
    
    def test_acesso_prontuario_individual_invalido(self, client, app, psicologo_user):
        """Testar acesso ao prontuário de paciente inexistente ou sem permissão"""
        with app.app_context():
            usuario, _ = psicologo_user
            
            with client.session_transaction() as sess:
                sess['_user_id'] = str(usuario.id)
                sess['_fresh'] = True
            
            response = client.get('/psicologo/prontuario/999')
            assert response.status_code == 302  # Redirect
    
    def test_criacao_automatica_prontuario(self, client, app, psicologo_user, paciente_user, agendamento_teste):
        """Testar criação automática de prontuário ao acessar pela primeira vez"""
        with app.app_context():
            usuario, psicologo = psicologo_user
            _, paciente = paciente_user
            
            # Verificar que não existe prontuário
            prontuario_antes = Prontuario.query.filter_by(
                paciente_id=paciente.id,
                psicologo_id=psicologo.id
            ).first()
            assert prontuario_antes is None
            
            with client.session_transaction() as sess:
                sess['_user_id'] = str(usuario.id)
                sess['_fresh'] = True
            
            response = client.get(f'/psicologo/prontuario/{paciente.id}')
            assert response.status_code == 200
            
            # Verificar que o prontuário foi criado
            prontuario_depois = Prontuario.query.filter_by(
                paciente_id=paciente.id,
                psicologo_id=psicologo.id
            ).first()
            assert prontuario_depois is not None
    
    def test_adicionar_anotacao_api(self, client, app, psicologo_user, paciente_user, agendamento_teste):
        """Testar API para adicionar nova anotação"""
        with app.app_context():
            usuario, _ = psicologo_user
            _, paciente = paciente_user
            
            with client.session_transaction() as sess:
                sess['_user_id'] = str(usuario.id)
                sess['_fresh'] = True
            
            # Dados da anotação
            data_anotacao = {
                'data_sessao': '2024-01-15',
                'anotacoes': 'Primeira sessão. Paciente apresentou boa receptividade.'
            }
            
            response = client.post(
                f'/psicologo/paciente/{paciente.id}/anotacao',
                json=data_anotacao,
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'Anotação adicionada com sucesso' in data['message']
            
            # Verificar se a sessão foi criada no banco
            sessao = Sessao.query.first()
            assert sessao is not None
            assert sessao.anotacoes == data_anotacao['anotacoes']
    
    def test_adicionar_anotacao_sem_dados(self, client, app, psicologo_user, paciente_user, agendamento_teste):
        """Testar API para adicionar anotação sem dados obrigatórios"""
        with app.app_context():
            usuario, _ = psicologo_user
            _, paciente = paciente_user
            
            with client.session_transaction() as sess:
                sess['_user_id'] = str(usuario.id)
                sess['_fresh'] = True
            
            response = client.post(
                f'/psicologo/paciente/{paciente.id}/anotacao',
                json={},
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = response.get_json()
            assert 'Anotações são obrigatórias' in data['error']
    
    def test_historico_paciente_api(self, client, app, psicologo_user, paciente_user, agendamento_teste):
        """Testar API para buscar histórico de sessões"""
        with app.app_context():
            usuario, psicologo = psicologo_user
            _, paciente = paciente_user
            
            # Criar prontuário e sessão de teste
            prontuario = Prontuario(
                paciente_id=paciente.id,
                psicologo_id=psicologo.id,
                observacoes_gerais="Teste"
            )
            db.session.add(prontuario)
            db.session.commit()
            
            sessao = Sessao(
                prontuario_id=prontuario.id,
                data_sessao=date.today(),
                anotacoes="Sessão de teste"
            )
            db.session.add(sessao)
            db.session.commit()
            
            with client.session_transaction() as sess:
                sess['_user_id'] = str(usuario.id)
                sess['_fresh'] = True
            
            response = client.get(f'/psicologo/paciente/{paciente.id}/historico')
            assert response.status_code == 200
            
            data = response.get_json()
            assert 'sessoes' in data
            assert len(data['sessoes']) == 1
            assert data['sessoes'][0]['anotacoes'] == "Sessão de teste"
    
    def test_acesso_negado_paciente_outro_psicologo(self, client, app, psicologo_user, paciente_user):
        """Testar que psicólogo não pode acessar paciente de outro psicólogo"""
        with app.app_context():
            usuario, _ = psicologo_user
            _, paciente = paciente_user
            
            # Não criar agendamento (sem relacionamento)
            
            with client.session_transaction() as sess:
                sess['_user_id'] = str(usuario.id)
                sess['_fresh'] = True
            
            response = client.get(f'/psicologo/prontuario/{paciente.id}')
            assert response.status_code == 302  # Redirect por falta de permissão
    
    def test_busca_pacientes_prontuarios(self, client, app, psicologo_user, paciente_user, agendamento_teste):
        """Testar busca de pacientes na página de prontuários"""
        with app.app_context():
            usuario, _ = psicologo_user
            _, paciente = paciente_user
            
            # Re-query para garantir que os objetos estão anexados à sessão atual
            paciente = Paciente.query.get(paciente.id)
            usuario = Usuario.query.get(usuario.id)
            
            with client.session_transaction() as sess:
                sess['_user_id'] = str(usuario.id)
                sess['_fresh'] = True
            
            # Buscar por nome
            response = client.get(f'/psicologo/prontuarios?search={paciente.usuario.nome_completo[:5]}')
            assert response.status_code == 200
            assert paciente.usuario.nome_completo.encode() in response.data
            
            # Buscar por email
            response = client.get(f'/psicologo/prontuarios?search={paciente.usuario.email[:5]}')
            assert response.status_code == 200
            assert paciente.usuario.email.encode() in response.data


if __name__ == '__main__':
    pytest.main([__file__])