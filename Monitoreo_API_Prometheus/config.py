from pathlib import Path #Librería para manejar directorios cómo objetos
import os #Libreria del Sistema Operativo
import json
from dotenv import load_dotenv #Cargar variables de entorno

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path) # === CARGAR .env ===

def get_config():
    return {
        "api_port": int(os.getenv("API_PORT")),
        "api_user": str(os.getenv("API_USER")),
        "api_password": str(os.getenv("API_PASSWORD")),
        "topology_file": Path(os.getenv("TOPOLOGY_FILE")).expanduser(),
        "log_dir": Path(os.getenv("LOG_DIR")).expanduser(),
        "telegram_token": str(os.getenv("TELEGRAM_TOKEN")),
        "telegram_chat_id": int(os.getenv("TELEGRAM_CHAT_ID")),
    }