#!/usr/bin/env python3
"""
Script de inicialização do banco de dados para produção
Este script deve ser executado após o deploy no Render para configurar o banco de dados
"""

import os
import sys
from app import create_app, db
from app.models import Usuario
from werkzeug.security import generate_password_hash

def init_database():
    """Inicializa o banco de dados e cria usuários padrão"""
    
    # Configura o ambiente para produção
    os.environ['FLASK_CONFIG'] = 'production'
    
    # Cria a aplicação
    app = create_app('production')
    
    with app.app_context():
        try:
            print("Criando tabelas do banco de dados...")
            db.create_all()
            print("✓ Tabelas criadas com sucesso!")
            
            # Verifica se já existe um usuário admin
            admin_email = 'admin@clinicamentalize.com.br'
            admin_user = Usuario.query.filter_by(email=admin_email).first()
            
            if not admin_user:
                print("Criando usuário administrador padrão...")
                
                # Senha padrão (deve ser alterada após o primeiro login)
                default_password = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'admin123')
                
                new_admin = Usuario(
                    nome_completo='Administrativo',
                    tipo_usuario='admin',
                    email=admin_email,
                    telefone='(11) 96331-3561',
                    senha_hash=generate_password_hash(default_password)
                )
                
                db.session.add(new_admin)
                db.session.commit()
                
                print("✓ Usuário administrador criado com sucesso!")
                print(f"  Email: {admin_email}")
                print(f"  Senha: {default_password}")
                print("  ⚠️  IMPORTANTE: Altere a senha após o primeiro login!")
            else:
                print("✓ Usuário administrador já existe.")
            
            print("\n🎉 Inicialização do banco de dados concluída com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro durante a inicialização: {e}")
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    init_database()