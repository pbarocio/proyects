from dotenv import load_dotenv #Cargar variables de entorno
import pymysql
import mysql.connector
import os
from pathlib import Path
from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder
import paramiko
import pandas as pd

# --- PARCHE PARA PYTHON 3.14 / PARAMIKO Y SSHTUNNEL ---
if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = paramiko.PKey.PKey if hasattr(paramiko.PKey, 'PKey') else paramiko.RSAKey
# ------------------------------------------------------

def obtener_empleados_vps():
    """
    Abre un túnel SSH seguro al VPS de GoDaddy, lee la tabla de empleados
    de la base de datos central y la regresa como un DataFrame de Pandas.
    """
    # 1. Configurar y arrancar el Túnel SSH
    tunnel = SSHTunnelForwarder(
        (os.getenv("SSH_HOST"), int(os.getenv("SSH_PORT"))),                    # Host SSH / IP del VPS
        ssh_username=os.getenv("SSH_USER"),         # 'agrocisa'
        ssh_password=os.getenv("SSH_PASS"),         # Tu clave de SSH / GoDaddy
        remote_bind_address=(os.getenv("VPS_HOST"), int(os.getenv("VPS_DB_PORT"))),     # Apunta al MariaDB dentro del VPS
        allow_agent=False
    )
    
    tunnel.start()
    print("🔓 Túnel SSH abierto con éxito.")

    try:
        # 2. Conectar a MariaDB a través del puerto local que asignó el túnel
        conexion = mysql.connector.connect(
            host=os.getenv("VPS_HOST"),
            port=tunnel.local_bind_port,            # Puerto dinámico del túnel
            user=os.getenv("VPS_DB_USER"),          # 'agrocisa' o el usuario de MariaDB
            password=os.getenv("VPS_DB_PASS"),      # Clave de la BD
            database=os.getenv("VPS_DB")       # La base de datos de César
        )

        # 3. Traerte los datos directo a Pandas
        query = "SELECT codigo, nombre, apellido_materno, apellido_paterno FROM empleados WHERE estatus = 'ACTIVO' ORDER BY codigo ASC"
        df_empleados = pd.read_sql(query, conexion)
        
        conexion.close()
        return df_empleados

    finally:
        # 4. SIEMPRE cerrar el túnel para no dejar conexiones colgadas en el servidor
        tunnel.stop()
        print("🔒 Túnel SSH cerrado.")

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path) # === CARGAR .env ===

def get_connection():
    """Retorna una conexión a MariaDB"""
    try:
        conexion = pymysql.connect(
            host=str(os.getenv("HOST")),
            user=str(os.getenv("BDD_USER")),
            password=str(os.getenv("BDD_PASSWORD")),
            database=str(os.getenv("DATABASE")),
            port=3306,
            charset='utf8mb4',
            autocommit=False,
            #cursorclass=pymysql.cursors.DictCursor  # Opcional: resultados como diccionarios
        )
        print("✅ Conexión a MariaDB establecida")
        return conexion
    except pymysql.Error as e:
        print(f"❌ Error de conexión a MariaDB: {e}")
        return None

def get_connection_nueva():
    """Retorna una conexión a MariaDB"""
    try:
        conexion = pymysql.connect(
            host=str(os.getenv("HOST")),
            user=str(os.getenv("BDD_USER")),
            password=str(os.getenv("BDD_PASSWORD")),
            port=3306,
            charset='utf8mb4',
            autocommit= False
            #cursorclass=pymysql.cursors.DictCursor  # Opcional: resultados como diccionarios
        )
        print("✅ Conexión a MariaDB establecida")
        return conexion
    except pymysql.Error as e:
        print(f"❌ Error de conexión a MariaDB: {e}")
        return None
    
def get_engine():
    """Retorna un engine de SQLAlchemy (para pandas y operaciones ORM)"""
    try:
        user = str(os.getenv("BDD_USER"))
        password = str(os.getenv("BDD_PASSWORD"))
        host = str(os.getenv("HOST"))
        database = str(os.getenv("DATABASE"))
        
        engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}?charset=utf8mb4")
        print("✅ Engine de SQLAlchemy creado")
        return engine
    except Exception as e:
        print(f"❌ Error al crear el engine: {e}")
        return None

def get_files_path():
    try:
        return {
            'dir_responsivas' : Path(os.getenv("PATH_RESPONSIVAS")).expanduser(),
            'directorio' : str(Path(os.getenv("PATH_DIRECTORIO")).expanduser()),
            'directorio_nuevo' : str(Path(os.getenv("PATH_DIRECTORIO_NUEVO")).expanduser()),
            'dir_plantillas' : Path(os.getenv("PATH_PLANTILLAS")).expanduser(),
            'db_user' : str(Path(os.getenv("BDD_USER")))
        }
    except KeyError as e:
        raise SystemExit(f"Falta exportar la variable de entorno: {e}")