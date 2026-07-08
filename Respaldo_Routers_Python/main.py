import logging
from pathlib import Path #Librería para manejar directorios cómo objetos
from config import get_config
import bkcps_handler as bckps

logging.basicConfig(
    filename= get_config()["log_dir"] / "backups_routers.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s - %(filename)s",
    datefmt="%Y-%m-%d_%H:%M:%S"    
)

def create_dirs():
    try:
        config = get_config()
        bckps_dir = config["backups_dir"]
        bckps_log = config["log_dir"]
        bckps_log.mkdir(parents=True, exist_ok=True) # Crear la carpeta si no existe
        bckps_dir.mkdir(parents=True, exist_ok=True)
        return config,bckps_dir
    except Exception as error:
        logging.critical(f"❌ ¡¡¡ERROR CREANDO LOS DIRECTORIOS DE RESPALDO_ROUTERS!!! \nREVISA EL SERVIDOR\n{error}", exc_info=True)
        raise

def start():
    config,bckps_dir = create_dirs()
    bckps.orchestration(config,bckps_dir)

start()