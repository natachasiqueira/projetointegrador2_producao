import pytest
import tempfile
import os
from app import create_app, db
from app.models import Usuario

@pytest.fixture
def app():
    """Fixture da aplicação Flask para testes"""
    # Cria um arquivo temporário para o banco de dados de teste
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app('testing')
    app.config['DATABASE'] = db_path
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Fixture do cliente de teste"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Fixture do runner CLI"""
    return app.test_cli_runner()

@pytest.fixture
def admin_user(app):
    """Fixture para criar um usuário administrador de teste"""
    with app.app_context():
        admin = Usuario(
            nome_completo='Admin Teste',
            email='admin@teste.com',
            telefone='(11) 99999-9999',
            tipo_usuario='admin'
        )
        admin.set_senha('senha123')
        db.session.add(admin)
        db.session.commit()
        return admin