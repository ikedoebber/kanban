#!/bin/bash
set -e

# Verifica se está em modo debug
if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ]; then
    echo "⚠️ Modo DEBUG ativado"
else
    echo "🔒 Modo produção ativado"
fi

# Executa migrations
echo "🔍 Aplicando migrations..."
python manage.py migrate --noinput
echo "✅ Migrations concluídas"

# Coleta arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput
echo "✅ Staticfiles coletados"

# Testa conexão com o banco
echo "🔌 Testando conexão com o banco..."
python manage.py shell -c "
import sys
from django.db import connection
try:
    connection.ensure_connection()
    print('✅ Banco de dados acessível')
except Exception as e:
    print(f'❌ Erro de conexão: {e}')
    sys.exit(1)
"

# Executa o comando do CMD
echo "🚀 Iniciando aplicação..."
exec "$@"
