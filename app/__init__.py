from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from config import config

# Inicialização das extensões
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name='default'):
    """Factory function para criar a aplicação Flask"""
    app = Flask(__name__)
    
    # Configuração da aplicação
    app.config.from_object(config[config_name])
    
    # Inicialização das extensões
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Configuração do Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, faça login para acessar esta página.'
    login_manager.login_message_category = 'info'
    
    # Registro dos blueprints
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
# Registrar blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.paciente import bp as paciente_bp
    app.register_blueprint(paciente_bp, url_prefix='/paciente')
    
    from app.psicologo import bp as psicologo_bp
    app.register_blueprint(psicologo_bp, url_prefix='/psicologo')
    
    from app.admin import admin as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Importação dos modelos para que sejam reconhecidos pelo SQLAlchemy
    from app import models
    
    # Filtros personalizados para tradução
    @app.template_filter('dia_semana_pt')
    def dia_semana_pt(data):
        """Converte dia da semana para português"""
        dias = {
            'Monday': 'Segunda-feira',
            'Tuesday': 'Terça-feira', 
            'Wednesday': 'Quarta-feira',
            'Thursday': 'Quinta-feira',
            'Friday': 'Sexta-feira',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo'
        }
        return dias.get(data.strftime('%A'), data.strftime('%A'))
    
    @app.template_filter('mes_pt')
    def mes_pt(data):
        """Converte mês para português"""
        meses = {
            'January': 'Janeiro',
            'February': 'Fevereiro',
            'March': 'Março',
            'April': 'Abril',
            'May': 'Maio',
            'June': 'Junho',
            'July': 'Julho',
            'August': 'Agosto',
            'September': 'Setembro',
            'October': 'Outubro',
            'November': 'Novembro',
            'December': 'Dezembro'
        }
        return meses.get(data.strftime('%B'), data.strftime('%B'))
    
    return app