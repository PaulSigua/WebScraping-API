import pyodbc
import os
from dotenv import load_dotenv
from fastapi import HTTPException
from datetime import datetime, timedelta

load_dotenv()

# Diccionario de configuraciones para múltiples bases de datos
DB_CONFIG = {
    1: {"name": f"{os.getenv('DB_NAME_1')}"},
    2: {"name": f"{os.getenv('DB_NAME_2')}"},
}

def create_db_connection(db_id: int):
    """Crea una conexión nueva a la base de datos especificada."""
    if db_id not in DB_CONFIG:
        raise ValueError(f"ID de base de datos no reconocido: {db_id}")
    
    try:
        conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={os.getenv('DB_SERVER')};"
            f"DATABASE={DB_CONFIG[db_id]['name']};"
            f"UID={os.getenv('DB_USERNAME')};"
            f"PWD={os.getenv('DB_PASSWORD')};",
            timeout=5
        )
        print(f"[INFO] Conexión establecida con {DB_CONFIG[db_id]['name']}")
        return conn
    except Exception as e:
        print(f"[ERROR] Error al conectar con la base de datos {DB_CONFIG[db_id]['name']}: {e}")
        return None

def get_db_connection(db_id: int):
    """Conexión reutilizable en endpoints de FastAPI (no persistente entre peticiones)."""
    conn = create_db_connection(db_id)
    if conn is None:
        raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail="Error validando conexión: " + str(e))
    
    return conn

# Función para ejecutar INSERT
def execute_insert_query(db_id, query, params):
    try:
        conn = get_db_connection(db_id)
        if conn is None:
            return {'error': f'Error al conectar con la base de datos {DB_CONFIG[db_id]["name"]}'}
        
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return {'message': 'INSERT ejecutado correctamente'}
    except Exception as e:
        message = f'Error al ejecutar INSERT en {DB_CONFIG[db_id]["name"]}: {e}'
        print(message)
        return None
    finally:
        if conn:
            conn.close()

def execute_select_query(db_id, query):
    try:
        conn = get_db_connection(db_id)
        cursor = conn.cursor()
        result = cursor.execute(query)
        row = result.fetchone()
        if row:
            return row[0]  # Retorna el valor de la primera columna
        else:
            return None
    except Exception as e:
        message = f'Error al ejecutar SELECT en {DB_CONFIG[db_id]["name"]} : {e}'
        print(message)
        return None
    finally:
        if conn:
            conn.close()

def execute_params_query(db_id, query, param):
    try:
        conn = get_db_connection(db_id)

        cursor = conn.cursor()
        cursor.execute(query, param)
        conn.commit()
    except Exception as e:
        message = f'Error al ejecutar QUERY en {DB_CONFIG[db_id]["name"]} : {e}'
        print(message)
        return None
    finally:
        if conn:
            conn.close()
            
def execute_query(db_id, query):
    try:
        conn = get_db_connection(db_id)

        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()
    except Exception as e:
        message = f'Error al ejecutar QUERY en {DB_CONFIG[db_id]["name"]} : {e}'
        print(message)
        return None
    finally:
        if conn:
            conn.close()

# Función para registrar logs en la base de datos
def log_to_db(db_id, id_group, log_level, message, endpoint, status_code):
    log_time = datetime.now() - timedelta(hours=6)
    query = """INSERT INTO Logs_Info (id_group, log_time, log_level, message, endpoint, status_code) VALUES (?, ?, ?, ?, ?, ?)"""
    return execute_insert_query(db_id, query, (id_group, log_time, log_level, message, endpoint, status_code))

# QUERYS EMAIL

user_mail_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 5 AND prm_descripcion = 'user_mail'"""

password_mail_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 5 AND prm_descripcion = 'password_mail'"""

server_mail_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 5 AND prm_descripcion = 'domain_mail'"""

port_mail_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 5 AND prm_descripcion = 'port'"""

endpoint_mail_query = """SELECT prm_valor
                FROM dbo.Parametros_Sistema
                WHERE id_grupo = 5 AND prm_descripcion = 'mail_sis'"""

# FUNCIONES MAIL
def get_user_mail():
    return execute_select_query(1, user_mail_query)

def get_pass_mail():
    return execute_select_query(password_mail_query)

def get_port_mail():
    return execute_select_query(port_mail_query)

def get_server_mail():
    return execute_select_query(server_mail_query)

def get_user_endpoint():
    return execute_select_query(endpoint_mail_query)