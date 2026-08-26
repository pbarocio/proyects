import logging
from logging.handlers import RotatingFileHandler
from config import get_config
from state_manager import control
from pathlib import Path
import time
import exporter

path_logs = get_config()["log_dir"]
path_logs.mkdir(parents=True, exist_ok=True)
log_file = path_logs / "monitoreo_enlaces_agrocisa.log"

handler = RotatingFileHandler(
    log_file, 
    maxBytes=200 * 1024 * 1024,  # Máximo 200 MB por archivo
    backupCount=3              # Conserva hasta 3 archivos (.log.1, .log.2, etc.)
)

logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s - %(filename)s",
    datefmt="%Y-%m-%d_%H:%M:%S"
)

def start():
    logging.info("🚀 Iniciando servicio continuo de monitoreo y métricas...")
    
    # 1. Arranca el mesero HTTP en background (hilo demonio)
    exporter.start_metrics_server(port=8000)
    
    # 2. Bucle infinito del cocinero
    while True:
        try:
            logging.info("\n  📡 ESTABLECIENDO CONEXIONES 🔌 🏢🏬 ...")
            control()
        except Exception as error:
            logging.error(f"❌ Error en la ronda de monitoreo: {error}", exc_info=True)
            
        # 3. Pausa de respiro para routers y enlaces
        time.sleep(15)
    
if __name__ == "__main__":
    start()