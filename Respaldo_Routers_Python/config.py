import os #Libreria del Sistema Operativo
from dotenv import load_dotenv #Cargar variables de entorno
from pathlib import Path #Librería para manejar directorios cómo objetos

env_path = Path(__file__).parent / ".env" #Definimos el directorio del .env
load_dotenv(env_path) #Cargamos el .env

def get_config():
    return {
        "device_type": str(os.getenv("SSH_DEVICE_TYPE")),
        "username": str(os.getenv("SSH_USERNAME")),
        "port": int(os.getenv("SSH_PORT")),
        "key_path": str(Path((os.getenv("SSH_KEY_PATH"))).expanduser()), #Convertimos a String la ruta de la llave del Router
        "branches_file": Path(os.getenv("TOPOLOGY_FILE")).expanduser(),
        "backups_dir": Path(os.getenv("BCKP_DIR")), #Extraemos la ruta del Directorio de Repaldo
        "log_dir": Path(os.getenv("LOG_DIR")).expanduser(),
        "telegram_token": str(os.getenv("TELEGRAM_TOKEN")),
        "telegram_chat_id": int(os.getenv("TELEGRAM_CHAT_ID")),
    }