# 🚀 Guia de Deploy - Clínica Mentalize no Render

Este guia contém todas as instruções necessárias para fazer o deploy da aplicação Clínica Mentalize no Render.

## 📋 Pré-requisitos

- Conta no [Render](https://render.com)
- Repositório Git com o código da aplicação
- Código já preparado para produção (arquivos já incluídos neste projeto)

## 🔧 Arquivos de Configuração Criados

Os seguintes arquivos foram criados/modificados para suportar o deploy no Render:

- ✅ `requirements.txt` - Dependências atualizadas com PostgreSQL e Gunicorn
- ✅ `Procfile` - Comando para iniciar a aplicação
- ✅ `config.py` - Configurações de produção para PostgreSQL
- ✅ `app.py` - Ajustes para modo de produção
- ✅ `.env.example` - Exemplo de variáveis de ambiente
- ✅ `init_db.py` - Script de inicialização do banco de dados
- ✅ `render.yaml` - Configuração automática do Render

## 🚀 Passo a Passo do Deploy

### 1. Preparar o Repositório Git

```bash
# Adicionar todos os arquivos ao Git
git add .
git commit -m "Preparar aplicação para deploy no Render"
git push origin main
```

### 2. Criar Serviço Web no Render

1. Acesse [render.com](https://render.com) e faça login
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório Git
4. Configure o serviço:
   - **Name**: `clinica-mentalize`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### 3. Criar Banco de Dados PostgreSQL

1. No dashboard do Render, clique em "New +" → "PostgreSQL"
2. Configure o banco:
   - **Name**: `clinica-mentalize-db`
   - **Database Name**: `clinica_mentalize`
   - **User**: `clinica_user`
3. Anote a **Database URL** que será gerada

### 4. Configurar Variáveis de Ambiente

No painel do seu Web Service, vá em "Environment" e adicione:

```
FLASK_CONFIG=production
FLASK_ENV=production
SECRET_KEY=[gere uma chave segura de 32+ caracteres]
JWT_SECRET_KEY=[gere uma chave JWT segura de 32+ caracteres]
DEFAULT_ADMIN_PASSWORD=[senha segura para o admin]
DATABASE_URL=[URL do banco PostgreSQL criado no passo 3]
```

**⚠️ IMPORTANTE**: 
- Gere chaves seguras para `SECRET_KEY` e `JWT_SECRET_KEY`
- Use uma senha forte para `DEFAULT_ADMIN_PASSWORD`
- A `DATABASE_URL` será fornecida automaticamente pelo Render se você conectar o banco

### 5. Conectar Banco de Dados ao Web Service

1. No painel do Web Service, vá em "Environment"
2. Clique em "Add Environment Variable"
3. Selecione "Add from Database" e escolha o banco criado
4. Isso adicionará automaticamente a `DATABASE_URL`

### 6. Deploy da Aplicação

1. Clique em "Deploy Latest Commit" ou faça um novo push para o repositório
2. Aguarde o build e deploy completarem
3. A aplicação estará disponível na URL fornecida pelo Render

### 7. Inicializar Banco de Dados (Primeira Execução)

Após o primeiro deploy bem-sucedido, execute o script de inicialização:

1. No painel do Web Service, vá em "Shell"
2. Execute: `python init_db.py`
3. Isso criará as tabelas e o usuário administrador padrão

## 🔐 Primeiro Acesso

Após o deploy, acesse sua aplicação e faça login com:

- **Email**: `admin@clinicamentalize.com.br`
- **Senha**: A senha definida em `DEFAULT_ADMIN_PASSWORD`

**⚠️ IMPORTANTE**: Altere a senha do administrador após o primeiro login!

## 🔧 Comandos Úteis

### Verificar Logs
```bash
# No painel do Render, vá em "Logs" para ver os logs da aplicação
```

### Executar Comandos no Servidor
```bash
# No painel do Render, vá em "Shell" para acessar o terminal
python init_db.py  # Reinicializar banco de dados
flask db upgrade   # Aplicar migrações (se houver)
```

### Atualizar Aplicação
```bash
# Faça push das alterações para o repositório
git add .
git commit -m "Atualização da aplicação"
git push origin main
# O Render fará o deploy automaticamente
```

## 🛠️ Solução de Problemas

### Erro de Conexão com Banco de Dados
- Verifique se a `DATABASE_URL` está configurada corretamente
- Certifique-se de que o banco PostgreSQL está ativo

### Erro 500 - Internal Server Error
- Verifique os logs no painel do Render
- Certifique-se de que todas as variáveis de ambiente estão configuradas
- Execute `python init_db.py` se for o primeiro deploy

### Aplicação não Inicia
- Verifique se o `Procfile` está correto
- Confirme que todas as dependências estão no `requirements.txt`
- Verifique os logs de build no Render

## 📞 Suporte

Se encontrar problemas durante o deploy, verifique:

1. **Logs do Render**: Painel → Logs
2. **Configurações**: Todas as variáveis de ambiente estão definidas?
3. **Banco de Dados**: O PostgreSQL está conectado e ativo?
4. **Build**: O build foi concluído sem erros?

---

## 🎉 Parabéns!

Sua aplicação Clínica Mentalize agora está rodando na nuvem com Render! 

A aplicação estará disponível 24/7 com:
- ✅ PostgreSQL como banco de dados
- ✅ HTTPS automático
- ✅ Backups automáticos
- ✅ Escalabilidade automática
- ✅ Monitoramento integrado