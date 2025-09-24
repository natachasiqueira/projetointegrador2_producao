import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuração base da aplicação"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-desenvolvimento-nao-usar-em-producao'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///clinica_mentalize.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-chave-desenvolvimento'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hora
    
    # Configurações da clínica
    CLINICA_NOME = "Clínica Mentalize"
    CLINICA_ENDERECO = "R. Progresso, 735 – Centro, Francisco Morato - SP, CEP 07901-080"
    CLINICA_EMAIL = "contato@clinicamentalize.com.br"
    CLINICA_TELEFONE = "(11) 96331-3561"

class DevelopmentConfig(Config):
    """Configuração para desenvolvimento"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuração para produção"""
    DEBUG = False
    TESTING = False
    # O Render fornece a DATABASE_URL automaticamente
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Configurações de segurança para produção
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    
    # Configurações específicas do PostgreSQL
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

class TestingConfig(Config):
    """Configuração para testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Dicionário de configurações
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}