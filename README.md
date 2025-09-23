# Sistema Clínica Mentalize

Sistema web completo para gestão de clínica de psicologia desenvolvido em Flask com dashboard administrativo avançado e funcionalidades completas de agendamento e prontuários.

## 🚀 Funcionalidades

### Área Pública
- **Página inicial**: Informações da clínica e formulário de cadastro de pacientes
- **Sistema de login**: Autenticação segura para diferentes tipos de usuários

### Área do Paciente
- **Dashboard pessoal**: Visão geral dos agendamentos e informações
- **Gestão de perfil**: Atualização de dados pessoais e contato
- **Agendamentos**: Visualização e gestão de consultas agendadas
- **Histórico**: Acesso ao histórico de sessões realizadas

### Área do Psicólogo
- **Dashboard profissional**: Visão geral da agenda e pacientes
- **Calendário interativo**: Gestão completa de horários e agendamentos
- **Prontuários eletrônicos**: Sistema completo de registro de sessões
- **Gestão de horários**: Configuração de disponibilidade de atendimento
- **Relatórios**: Acompanhamento de pacientes e sessões

### Área Administrativa
- **Dashboard executivo**: Indicadores e métricas da clínica
  - Agendamentos por mês
  - Taxa de retenção de pacientes
  - Frequência de sessões
  - Taxa de ocupação dos profissionais
  - Taxa de no-show
  - Número de casos ativos
- **Gestão de usuários**: Cadastro e gerenciamento de psicólogos
- **Relatórios gerenciais**: Análises e estatísticas da clínica

### Sistema de Prontuários
- **Registro de sessões**: Documentação completa dos atendimentos
- **Histórico de pacientes**: Acompanhamento longitudinal
- **Recorrência de atendimentos**: Controle de frequência e continuidade

## 🛠️ Tecnologias

### Backend
- **Flask 2.3.3**: Framework web principal
- **SQLAlchemy 3.0.5**: ORM para banco de dados
- **Flask-Login 0.6.3**: Sistema de autenticação
- **Flask-WTF 1.1.1**: Formulários e validação
- **Flask-Migrate 4.0.5**: Migrações de banco de dados
- **Flask-CORS 4.0.0**: Controle de CORS
- **Werkzeug 2.3.7**: Utilitários WSGI
- **PyJWT 2.8.0**: Tokens JWT para autenticação

### Frontend
- **HTML5**: Estrutura semântica
- **CSS3**: Estilização moderna e responsiva
- **JavaScript ES6+**: Interatividade e funcionalidades dinâmicas
- **Chart.js**: Gráficos interativos no dashboard
- **Bootstrap**: Framework CSS para responsividade

### Banco de Dados
- **SQLite**: Desenvolvimento local
- **PostgreSQL**: Produção (configurável)

### Testes
- **Pytest 7.4.2**: Framework de testes
- **Pytest-Flask 1.2.0**: Extensões para Flask
- **Pytest-Cov 4.1.0**: Cobertura de código

## 📋 Pré-requisitos

- **Python 3.8+**
- **pip** (gerenciador de pacotes Python)
- **Git** (para clonagem do repositório)

## 🔧 Instalação Local

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd Clinica_Mentalize
```

### 2. Crie e ative um ambiente virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure variáveis de ambiente (opcional)
```bash
# Crie um arquivo .env na raiz do projeto
DEFAULT_ADMIN_PASSWORD=sua_senha_admin
DEFAULT_PSICOLOGO_PASSWORD=sua_senha_psicologo
FLASK_CONFIG=development
SECRET_KEY=sua_chave_secreta
```

### 5. Execute a aplicação
```bash
python app.py
```

### 6. Acesse o sistema
- **URL**: http://localhost:5000
- **Usuários padrão criados automaticamente**:
  - **Admin**: admin@clinicamentalize.com.br (senha: admin123)
  - **Psicólogo**: cicera.santana@clinicamentalize.com.br (senha: senha123)

## 🧪 Testes

### Executar todos os testes
```bash
pytest
```

### Executar com cobertura de código
```bash
pytest --cov=app --cov-report=html
```

### Executar testes específicos
```bash
pytest tests/test_auth.py
pytest tests/test_models.py
```

## 📁 Estrutura do Projeto

```
Clinica_Mentalize/
├── app/                          # Aplicação principal
│   ├── __init__.py              # Factory da aplicação
│   ├── models.py                # Modelos do banco de dados
│   ├── auth/                    # Módulo de autenticação
│   │   ├── __init__.py
│   │   ├── routes.py           # Rotas de login/logout
│   │   └── forms.py            # Formulários de autenticação
│   ├── main/                    # Módulo principal
│   │   ├── __init__.py
│   │   ├── routes.py           # Rotas principais
│   │   └── forms.py            # Formulários principais
│   ├── admin/                   # Módulo administrativo
│   │   ├── __init__.py
│   │   ├── routes.py           # Dashboard e gestão
│   │   └── forms.py            # Formulários admin
│   ├── paciente/                # Módulo do paciente
│   │   ├── __init__.py
│   │   ├── routes.py           # Área do paciente
│   │   └── forms.py            # Formulários do paciente
│   ├── psicologo/               # Módulo do psicólogo
│   │   ├── __init__.py
│   │   ├── routes.py           # Área do psicólogo
│   │   └── forms.py            # Formulários do psicólogo
│   ├── static/                  # Arquivos estáticos
│   │   ├── css/                # Estilos CSS
│   │   ├── js/                 # Scripts JavaScript
│   │   └── images/             # Imagens
│   └── templates/               # Templates HTML
│       ├── base.html           # Template base
│       ├── index.html          # Página inicial
│       ├── auth/               # Templates de autenticação
│       ├── admin/              # Templates administrativos
│       ├── paciente/           # Templates do paciente
│       └── psicologo/          # Templates do psicólogo
├── tests/                       # Testes automatizados
├── config.py                    # Configurações da aplicação
├── app.py                       # Ponto de entrada da aplicação
├── requirements.txt             # Dependências Python
└── README.md                    # Documentação
```

## 🗄️ Modelos de Dados

### Usuario
- Usuários do sistema (admin, psicólogo, paciente)
- Autenticação e autorização

### Psicologo
- Dados profissionais dos psicólogos

### Paciente
- Informações dos pacientes
- Dados pessoais e histórico

### Agendamento
- Consultas agendadas
- Status e informações da sessão

### Sessao
- Registro das sessões realizadas
- Prontuários e observações

### Prontuario
- Histórico clínico dos pacientes
- Evolução e acompanhamento

### HorarioAtendimento
- Disponibilidade dos psicólogos
- Configuração de horários

## 🔒 Segurança

- **Autenticação**: Sistema seguro com hash de senhas
- **Autorização**: Controle de acesso por tipo de usuário
- **Validação**: Formulários com validação server-side
- **CSRF Protection**: Proteção contra ataques CSRF
- **SQL Injection**: Proteção via SQLAlchemy ORM

## 🌐 Deploy em Produção

### Configurações recomendadas:
- **Servidor**: Gunicorn + Nginx
- **Banco**: PostgreSQL
- **SSL**: Certificado HTTPS
- **Backup**: Rotina automatizada
- **Monitoramento**: Logs e métricas