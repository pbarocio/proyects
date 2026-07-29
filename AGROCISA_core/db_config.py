from dotenv import load_dotenv #Cargar variables de entorno
import pymysql
import os
from pathlib import Path

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
            charset='utf8mb4',
            autocommit=str(os.getenv("AUTOCOMMIT")),
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
            charset='utf8mb4',
            autocommit= False
            #cursorclass=pymysql.cursors.DictCursor  # Opcional: resultados como diccionarios
        )
        print("✅ Conexión a MariaDB establecida")
        return conexion
    except pymysql.Error as e:
        print(f"❌ Error de conexión a MariaDB: {e}")
        return None

def environment_info():
    try:
        return {
            'dir_responsivas' : str(Path(os.getenv("PATH_RESPONSIVAS")).expanduser()),
            'directorio' : str(Path(os.getenv("PATH_DIRECTORIO")).expanduser()),
            'directorio_nuevo' : str(Path(os.getenv("PATH_DIRECTORIO_NUEVO")).expanduser()),
            'dir_plantillas' : str(Path(os.getenv("PATH_PLANTILLAS")).expanduser()),
            'db_user' : str(Path(os.getenv("BDD_USER")))
        }
    except KeyError as e:
        raise SystemExit(f"Falta exportar la variable de entorno: {e}")