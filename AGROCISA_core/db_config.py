from dotenv import load_dotenv #Cargar variables de entorno
import pymysql
import os
from pathlib import Path
from sqlalchemy import create_engine 

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