from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    """Carrega o usuário pelo ID para o Flask-Login"""
    return Usuario.query.get(int(user_id))

class Usuario(UserMixin, db.Model):
    """Modelo base para todos os usuários do sistema"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    tipo_usuario = db.Column(db.Enum('admin', 'psicologo', 'paciente', name='tipo_usuario_enum'), nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    psicologo = db.relationship('Psicologo', backref='usuario', uselist=False, cascade='all, delete-orphan')
    paciente = db.relationship('Paciente', backref='usuario', uselist=False, cascade='all, delete-orphan')
    admin = db.relationship('Admin', backref='usuario', uselist=False, cascade='all, delete-orphan')
    
    def set_senha(self, senha):
        """Define a senha do usuário com hash"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

class Admin(db.Model):
    """Modelo para administradores"""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, unique=True)
    
    def __repr__(self):
        return f'<Admin {self.usuario.nome_completo}>'

class Psicologo(db.Model):
    """Modelo para psicólogos"""
    __tablename__ = 'psicologos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, unique=True)
    
    # Relacionamentos
    pacientes = db.relationship('Paciente', backref='psicologo_responsavel', lazy='dynamic')
    agendamentos = db.relationship('Agendamento', backref='psicologo', lazy='dynamic')
    prontuarios = db.relationship('Prontuario', backref='psicologo', lazy='dynamic')
    horarios_atendimento = db.relationship('HorarioAtendimento', backref='psicologo', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Psicologo {self.usuario.nome_completo}>'

class Paciente(db.Model):
    """Modelo para pacientes"""
    __tablename__ = 'pacientes'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, unique=True)
    psicologo_id = db.Column(db.Integer, db.ForeignKey('psicologos.id'), nullable=True)
    
    # Relacionamentos
    agendamentos = db.relationship('Agendamento', backref='paciente', lazy='dynamic')
    prontuarios = db.relationship('Prontuario', backref='paciente', lazy='dynamic')
    
    def __repr__(self):
        return f'<Paciente {self.usuario.nome_completo}>'

class Agendamento(db.Model):
    """Modelo para agendamentos"""
    __tablename__ = 'agendamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    psicologo_id = db.Column(db.Integer, db.ForeignKey('psicologos.id'), nullable=False)
    data_hora = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.Enum('agendado', 'confirmado', 'realizado', 'cancelado', 'ausencia', name='status_agendamento_enum'), 
                      default='agendado', nullable=False)
    observacoes = db.Column(db.Text, nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamento com sessões
    sessao = db.relationship('Sessao', backref='agendamento', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Agendamento {self.paciente.usuario.nome_completo} - {self.data_hora}>'

class Prontuario(db.Model):
    """Modelo para prontuários"""
    __tablename__ = 'prontuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    psicologo_id = db.Column(db.Integer, db.ForeignKey('psicologos.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    observacoes_gerais = db.Column(db.Text, nullable=True)
    
    # Configurações de recorrência
    recorrencia_ativa = db.Column(db.Boolean, default=False, nullable=False)
    recorrencia_dia_semana = db.Column(db.Integer, nullable=True)  # 0=Segunda, 1=Terça, etc.
    recorrencia_horario = db.Column(db.Time, nullable=True)
    
    # Relacionamentos
    sessoes = db.relationship('Sessao', backref='prontuario', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Prontuario {self.paciente.usuario.nome_completo}>'

class Sessao(db.Model):
    """Modelo para sessões/consultas realizadas"""
    __tablename__ = 'sessoes'
    
    id = db.Column(db.Integer, primary_key=True)
    prontuario_id = db.Column(db.Integer, db.ForeignKey('prontuarios.id'), nullable=False)
    agendamento_id = db.Column(db.Integer, db.ForeignKey('agendamentos.id'), nullable=True)
    data_sessao = db.Column(db.DateTime, nullable=False)
    anotacoes = db.Column(db.Text, nullable=True)
    proxima_sessao = db.Column(db.DateTime, nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<Sessao {self.prontuario.paciente.usuario.nome_completo} - {self.data_sessao}>'

class HorarioAtendimento(db.Model):
    """Modelo para horários de atendimento dos psicólogos"""
    __tablename__ = 'horarios_atendimento'
    
    id = db.Column(db.Integer, primary_key=True)
    psicologo_id = db.Column(db.Integer, db.ForeignKey('psicologos.id'), nullable=False)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0=Segunda, 1=Terça, ..., 6=Domingo
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time, nullable=False)
    ativo = db.Column(db.Boolean, default=True, nullable=False)
    
    def __repr__(self):
        dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        return f'<HorarioAtendimento {dias[self.dia_semana]} {self.hora_inicio}-{self.hora_fim}>'