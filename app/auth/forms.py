from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models import Usuario

class LoginForm(FlaskForm):
    """Formulário de login"""
    email = StringField('E-mail', validators=[
        DataRequired(message='E-mail é obrigatório'),
        Email(message='E-mail inválido')
    ])
    senha = PasswordField('Senha', validators=[
        DataRequired(message='Senha é obrigatória')
    ])
    tipo_usuario = SelectField('Tipo de Usuário', choices=[
        ('paciente', 'Paciente'),
        ('psicologo', 'Psicólogo'),
        ('admin', 'Administrador')
    ], validators=[DataRequired(message='Selecione o tipo de usuário')])
    submit = SubmitField('Entrar')

class RegistroPacienteForm(FlaskForm):
    """Formulário de registro de paciente"""
    nome_completo = StringField('Nome Completo', validators=[
        DataRequired(message='Nome completo é obrigatório'),
        Length(min=2, max=200, message='Nome deve ter entre 2 e 200 caracteres')
    ])
    email = StringField('E-mail', validators=[
        DataRequired(message='E-mail é obrigatório'),
        Email(message='E-mail inválido')
    ])
    telefone = StringField('Telefone', validators=[
        DataRequired(message='Telefone é obrigatório'),
        Length(min=10, max=20, message='Telefone deve ter entre 10 e 20 caracteres')
    ])
    senha = PasswordField('Senha', validators=[
        DataRequired(message='Senha é obrigatória'),
        Length(min=6, message='Senha deve ter pelo menos 6 caracteres')
    ])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[
        DataRequired(message='Confirmação de senha é obrigatória'),
        EqualTo('senha', message='Senhas devem ser iguais')
    ])
    submit = SubmitField('Cadastrar')
    
    def validate_email(self, email):
        """Valida se o e-mail já não está em uso"""
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este e-mail já está cadastrado. Use outro e-mail.')

class AlterarSenhaForm(FlaskForm):
    """Formulário para alterar senha"""
    senha_atual = PasswordField('Senha Atual', validators=[
        DataRequired(message='Senha atual é obrigatória')
    ])
    nova_senha = PasswordField('Nova Senha', validators=[
        DataRequired(message='Nova senha é obrigatória'),
        Length(min=6, message='Senha deve ter pelo menos 6 caracteres')
    ])
    confirmar_nova_senha = PasswordField('Confirmar Nova Senha', validators=[
        DataRequired(message='Confirmação de nova senha é obrigatória'),
        EqualTo('nova_senha', message='Senhas devem ser iguais')
    ])
    submit = SubmitField('Alterar Senha')

class EditarPerfilForm(FlaskForm):
    """Formulário para editar perfil do usuário"""
    nome_completo = StringField('Nome Completo', validators=[
        DataRequired(message='Nome completo é obrigatório'),
        Length(min=2, max=200, message='Nome deve ter entre 2 e 200 caracteres')
    ])
    telefone = StringField('Telefone', validators=[
        DataRequired(message='Telefone é obrigatório'),
        Length(min=10, max=20, message='Telefone deve ter entre 10 e 20 caracteres')
    ])
    submit = SubmitField('Salvar Alterações')