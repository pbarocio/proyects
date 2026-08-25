import logging
from logging.handlers import RotatingFileHandler
from config import get_config
from state_manager import control
from pathlib import Path

path_logs = get_config()["log_dir"]
path_logs.mkdir(parents=True, exist_ok=True)
log_file = path_logs / "monitoreo_enlaces_agrocisa.log"

handler = RotatingFileHandler(
    log_file, 
    maxBytes=200 * 1024 * 1024,  # Máximo 5 MB por archivo
    backupCount=3              # Conserva hasta 3 archivos (.log.1, .log.2, etc.)
)

logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s - %(filename)s",
    datefmt="%Y-%m-%d_%H:%M:%S"
)

def start():
    logging.info(f"\n  📡 ESTABLECIENDO CONEXIONES 🔌 🏢🏬 ...")
    control()
    
start()