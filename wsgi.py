import os
from app import create_app

# Criar a instância da aplicação para o Gunicorn
app = create_app(os.getenv('FLASK_CONFIG') or 'production')

if __name__ == "__main__":
    app.run()