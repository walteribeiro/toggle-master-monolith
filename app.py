import os
import json
import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def carregar_config_db():
    config = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT", "5432"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
    }

    secret_name = os.getenv("AWS_SECRET_NAME")
    if not secret_name:
        return config

    client = boto3.session.Session().client(
        service_name="secretsmanager",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
    )
    try:
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise RuntimeError(
            f"Não foi possível ler o segredo '{secret_name}' no AWS Secrets Manager: {e}"
        ) from e

    secret = json.loads(response["SecretString"])

    # Aceita tanto chaves no padrão DB_* quanto no padrão dos secrets
    # gerados pelo console do RDS (username/password/host/port/dbname).
    config["host"] = secret.get("DB_HOST") or secret.get("host") or config["host"]
    config["port"] = str(secret.get("DB_PORT") or secret.get("port") or config["port"])
    config["dbname"] = secret.get("DB_NAME") or secret.get("dbname") or config["dbname"]
    config["user"] = secret.get("DB_USER") or secret.get("username") or config["user"]
    config["password"] = secret.get("DB_PASSWORD") or secret.get("password") or config["password"]
    return config

DB_CONFIG = carregar_config_db()

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        database=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    return conn

def init_db():
    print("Tentando inicializar a tabela 'flags'...")
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS flags (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) UNIQUE NOT NULL,
                is_enabled BOOLEAN NOT NULL DEFAULT false,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cur.close()
        conn.close()
        print("Tabela 'flags' inicializada com sucesso.")
    except psycopg2.OperationalError as e:
        print(f"Erro de conexão ao inicializar o banco de dados: {e}")
    except Exception as e:
        print(f"Um erro inesperado ocorreu durante a inicialização do DB: {e}")

@app.cli.command("init-db")
def init_db_command():
    init_db()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route('/flags', methods=['POST'])
def create_flag():
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "O campo 'name' é obrigatório"}), 400
    
    name = data['name']
    is_enabled = data.get('is_enabled', False)
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO flags (name, is_enabled) VALUES (%s, %s)", (name, is_enabled))
        conn.commit()
    except psycopg2.IntegrityError:
        return jsonify({"error": f"A flag '{name}' já existe"}), 409
    except Exception as e:
        return jsonify({"error": "Erro interno no servidor ao criar a flag", "details": str(e)}), 500
    finally:
        if 'cur' in locals() and not cur.closed:
            cur.close()
        if 'conn' in locals() and not conn.closed:
            conn.close()
            
    return jsonify({"message": f"Flag '{name}' criada com sucesso"}), 201

@app.route('/flags', methods=['GET'])
def get_flags():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT name, is_enabled FROM flags ORDER BY name")
        flags = cur.fetchall()
    except Exception as e:
        return jsonify({"error": "Erro interno no servidor ao buscar as flags", "details": str(e)}), 500
    finally:
        if 'cur' in locals() and not cur.closed:
            cur.close()
        if 'conn' in locals() and not conn.closed:
            conn.close()

    return jsonify(flags), 200

@app.route('/flags/<string:name>', methods=['GET'])
def get_flag_status(name):
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT name, is_enabled FROM flags WHERE name = %s", (name,))
        flag = cur.fetchone()
    except Exception as e:
        return jsonify({"error": "Erro interno no servidor ao buscar a flag", "details": str(e)}), 500
    finally:
        if 'cur' in locals() and not cur.closed:
            cur.close()
        if 'conn' in locals() and not conn.closed:
            conn.close()
    
    if flag:
        return jsonify(flag), 200
    return jsonify({"error": "Flag não encontrada"}), 404

@app.route('/flags/<string:name>', methods=['PUT'])
def update_flag(name):
    data = request.get_json()
    if data is None or 'is_enabled' not in data or not isinstance(data['is_enabled'], bool):
        return jsonify({"error": "O campo 'is_enabled' (booleano) é obrigatório"}), 400
        
    is_enabled = data['is_enabled']
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE flags SET is_enabled = %s WHERE name = %s", (is_enabled, name))
        
        if cur.rowcount == 0:
            return jsonify({"error": "Flag não encontrada"}), 404
            
        conn.commit()
    except Exception as e:
        return jsonify({"error": "Erro interno no servidor ao atualizar a flag", "details": str(e)}), 500
    finally:
        if 'cur' in locals() and not cur.closed:
            cur.close()
        if 'conn' in locals() and not conn.closed:
            conn.close()
    
    return jsonify({"message": f"Flag '{name}' atualizada"}), 200

@app.route('/flags/<string:name>', methods=['DELETE'])
def delete_flag(name):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM flags WHERE name = %s", (name,))

        if cur.rowcount == 0:
            return jsonify({"error": "Flag não encontrada"}), 404

        conn.commit()
    except Exception as e:
        return jsonify({"error": "Erro interno no servidor ao deletar a flag", "details": str(e)}), 500
    finally:
        if 'cur' in locals() and not cur.closed:
            cur.close()
        if 'conn' in locals() and not conn.closed:
            conn.close()

    return jsonify({"message": f"Flag '{name}' deletada"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)