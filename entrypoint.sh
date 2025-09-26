#!/bin/bash
set -e

# Verifica se está em modo de debug
if [ "$DEBUG" = "True" ] || [ "$DEBUG" = "true" ]; then
    echo "⚠️ Modo DEBUG ativado"
else
    echo "🔒 Modo produção ativado"
fi

# Executa migrations
echo "🔍 Verificando migrations..."
python manage.py migrate --noinput
echo "✅ Migrations concluídas"

# Verifica se o banco está acessível
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
