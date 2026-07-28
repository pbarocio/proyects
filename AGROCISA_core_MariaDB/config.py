from pathlib import Path #Librería para manejar directorios cómo objetos
import os #Libreria del Sistema Operativo
from dotenv import load_dotenv #Cargar variables de entorno

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path) # === CARGAR .env ===

def get_config():
    return {
        "files_dir" : Path(os.getenv("FILES_DIR")).expanduser(),
    }