# Use Python 3.13 como base
FROM python:3.13-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=app.settings

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para arquivos estáticos
RUN mkdir -p /app/staticfiles

# ========================================
# Argumentos de Build (baseados no seu .env)
# ========================================
ARG SECRET_KEY
ARG DEBUG=True
ARG ALLOWED_HOSTS="127.0.0.1,localhost,testserver"
ARG DATABASE_ENGINE="django.db.backends.sqlite3"
ARG DATABASE_NAME="db.sqlite3"

# Converter argumentos de build em variáveis de ambiente
ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=${DEBUG}
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS}
ENV DATABASE_ENGINE=${DATABASE_ENGINE}
ENV DATABASE_NAME=${DATABASE_NAME}

# Copiar e tornar executável o entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expor porta
EXPOSE 48321

# Comando padrão para iniciar o servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:48321"]