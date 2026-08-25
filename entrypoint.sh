#!/bin/sh
# NOTE: This script must use Unix line endings (LF). Do not convert to Windows CRLF.

# O que este script faz:
# 1. Se AWS_SECRET_NAME estiver definida, busca a configuração do banco no
#    AWS Secrets Manager (via app.py); senão usa as variáveis de ambiente.
# 2. Entra em um loop que tenta se conectar ao banco de dados.
# 3. Só sai do loop quando o banco de dados está pronto para aceitar conexões.
# 4. Executa o comando de inicialização do banco de dados.
# 5. Inicia o servidor Gunicorn.

# Modo AWS: obtém host/porta/banco/usuário a partir do segredo.
# A senha nunca é exportada para o shell — só o app.py a lê.
if [ -n "$AWS_SECRET_NAME" ]; then
  echo "Carregando configuração do banco a partir do segredo '${AWS_SECRET_NAME}'..."
  set -- $(python -c "from app import DB_CONFIG as c; print(c['host'], c['port'], c['dbname'], c['user'])")
  DB_HOST="$1"
  DB_PORT="$2"
  DB_NAME="$3"
  DB_USER="$4"
fi

# Verifique se a configuração do banco de dados está disponível
if [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ] || [ -z "$DB_NAME" ]; then
  echo "Erro: Defina AWS_SECRET_NAME (deploy na AWS) ou as variáveis de ambiente DB_HOST, DB_PORT e DB_NAME."
  exit 1
fi

echo "Aguardando o banco de dados em ${DB_HOST}:${DB_PORT}..."

# Loop para aguardar o banco de dados ficar disponível
# Para PostgreSQL, podemos usar o `pg_isready`
# Adicione `postgresql-client` ao seu Dockerfile (ex: apt-get install -y postgresql-client)
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -q -U "$DB_USER"; do
  echo "Banco de dados indisponível - aguardando..."
  sleep 1
done

echo "Banco de dados disponível!"

# Executa o comando de inicialização/migração do banco de dados
echo "Executando a inicialização do banco de dados..."
flask init-db

# Inicia a aplicação principal (Gunicorn)
echo "Iniciando o servidor Gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 app:app