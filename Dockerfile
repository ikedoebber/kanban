# Base Python 3.13 slim
FROM python:3.13-slim

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=app.settings

# Diretório de trabalho
WORKDIR /app

# Dependências do sistema para PostgreSQL e build de pacotes Python
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretório para arquivos estáticos
RUN mkdir -p /app/staticfiles

# Argumentos de build (opcional)
ARG SECRET_KEY
ARG DEBUG=True
ARG ALLOWED_HOSTS="127.0.0.1,localhost,testserver"

# Transformar args em variáveis de ambiente
ENV SECRET_KEY=${SECRET_KEY}
ENV DEBUG=${DEBUG}
ENV ALLOWED_HOSTS=${ALLOWED_HOSTS}

# Copiar entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expor porta do Django
EXPOSE 48321

# CMD padrão usando entrypoint
CMD ["/app/entrypoint.sh", "python", "manage.py", "runserver", "0.0.0.0:48321"]
