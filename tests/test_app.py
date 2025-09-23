import pytest
from app import create_app, db

class TestApp:
    """Testes básicos da aplicação"""
    
    def test_app_creation(self):
        """Testa se a aplicação é criada corretamente"""
        app = create_app('testing')
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_config(self):
        """Testa as configurações da aplicação"""
        app = create_app('testing')
        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
        assert app.config['WTF_CSRF_ENABLED'] is False
    
    def test_index_route(self, client):
        """Testa a rota principal"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Cl\xc3\xadnica Mentalize' in response.data
    
    def test_api_status(self, client):
        """Testa o endpoint de status da API"""
        response = client.get('/api/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'ok'
        assert 'API da Clínica Mentalize' in data['message']
    
    def test_auth_routes_exist(self, client):
        """Testa se as rotas de autenticação existem"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        
        response = client.get('/auth/logout')
        assert response.status_code == 200
    
    def test_area_routes_exist(self, client):
        """Testa se as rotas das áreas existem"""
        response = client.get('/paciente')
        assert response.status_code == 200
        
        response = client.get('/psicologo')
        assert response.status_code == 200
        
        response = client.get('/admin')
        assert response.status_code == 200