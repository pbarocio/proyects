from pathlib import Path #Librería para manejar directorios cómo objetos
import os #Libreria del Sistema Operativo
import json
from dotenv import load_dotenv #Cargar variables de entorno

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path) # === CARGAR .env ===

def get_config():
    return {
        "username": str(os.getenv("SSH_USERNAME")),
        "port": int(os.getenv("SSH_PORT")),
        "device_type": str(os.getenv("SSH_DEVICE_TYPE")),
        "key_path": str(Path(os.getenv("SSH_KEY_PATH")).expanduser()),
        "topology_file": Path(os.getenv("TOPOLOGY_FILE")).expanduser(),
        "log_dir": Path(os.getenv("LOG_DIR")).expanduser(),
        "telegram_token": str(os.getenv("TELEGRAM_TOKEN")),
        "telegram_chat_id": int(os.getenv("TELEGRAM_CHAT_ID")),
    }