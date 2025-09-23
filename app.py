import os
from app import create_app, db
from app.models import Usuario, Psicologo, Paciente, Agendamento, Prontuario, Sessao, HorarioAtendimento

# Criação da aplicação
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

@app.shell_context_processor
def make_shell_context():
    """Contexto do shell para facilitar testes e desenvolvimento"""
    return {
        'db': db,
        'Usuario': Usuario,
        'Psicologo': Psicologo,
        'Paciente': Paciente,
        'Agendamento': Agendamento,
        'Prontuario': Prontuario,
        'Sessao': Sessao,
        'HorarioAtendimento': HorarioAtendimento
    }

@app.cli.command()
def init_db():
    """Inicializa o banco de dados"""
    db.create_all()
    print('Banco de dados inicializado.')

@app.cli.command()
def init_default_users():
    """Inicializa usuários padrão do sistema"""
    from werkzeug.security import generate_password_hash
    
    # Dados dos usuários padrão
    default_users = [
        {
            'nome_completo': 'Administrativo',
            'tipo_usuario': 'admin',
            'email': 'admin@clinicamentalize.com.br',
            'telefone': '(11) 96331-3561',
            'senha': os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')
        },
        {
            'nome_completo': 'Cícera Santana',
            'tipo_usuario': 'psicologo',
            'email': 'cicera.santana@clinicamentalize.com.br',
            'telefone': '(11) 96331-3561',
            'senha': os.getenv('DEFAULT_PSICOLOGO_PASSWORD', 'senha123')
        }
    ]
    
    for user_data in default_users:
        # Verifica se o usuário já existe
        existing_user = Usuario.query.filter_by(email=user_data['email']).first()
        
        if not existing_user:
            # Cria o usuário
            new_user = Usuario(
                nome_completo=user_data['nome_completo'],
                tipo_usuario=user_data['tipo_usuario'],
                email=user_data['email'],
                telefone=user_data['telefone'],
                senha_hash=generate_password_hash(user_data['senha'])
            )
            
            db.session.add(new_user)
            print(f"Usuário criado: {user_data['nome_completo']} ({user_data['email']})")
        else:
            print(f"Usuário já existe: {user_data['nome_completo']} ({user_data['email']})")
    
    try:
        db.session.commit()
        print("Usuários padrão inicializados com sucesso!")
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao criar usuários padrão: {e}")

# Inicialização automática dos usuários padrão na primeira execução
def initialize_default_users():
    """Inicializa usuários padrão automaticamente na primeira execução"""
    try:
        # Verifica se já existem usuários no sistema
        user_count = Usuario.query.count()
        if user_count == 0:
            from werkzeug.security import generate_password_hash
            
            # Dados dos usuários padrão
            default_users = [
                {
                    'nome_completo': 'Administrativo',
                    'tipo_usuario': 'admin',
                    'email': 'admin@clinicamentalize.com.br',
                    'telefone': '(11) 96331-3561',
                    'senha': os.getenv('DEFAULT_ADMIN_PASSWORD', 'admin123')
                },
                {
                    'nome_completo': 'Cícera Santana',
                    'tipo_usuario': 'psicologo',
                    'email': 'cicera.santana@clinicamentalize.com.br',
                    'telefone': '(11) 96331-3561',
                    'senha': os.getenv('DEFAULT_PSICOLOGO_PASSWORD', 'senha123')
                }
            ]
            
            for user_data in default_users:
                new_user = Usuario(
                    nome_completo=user_data['nome_completo'],
                    tipo_usuario=user_data['tipo_usuario'],
                    email=user_data['email'],
                    telefone=user_data['telefone'],
                    senha_hash=generate_password_hash(user_data['senha'])
                )
                db.session.add(new_user)
            
            db.session.commit()
            print("Usuários padrão criados automaticamente!")
    except Exception as e:
        print(f"Erro na inicialização automática: {e}")

# Chama a inicialização na primeira execução
with app.app_context():
    db.create_all()
    initialize_default_users()

if __name__ == '__main__':
    app.run(debug=True)