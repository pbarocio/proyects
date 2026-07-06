import logging
from config import get_config
from state_manager import control
from pathlib import Path

logging.basicConfig(
    filename= get_config()["log_dir"] / "monitoreo_enlaces_agrocisa.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s - %(filename)s",
    datefmt="%Y-%m-%d_%H:%M:%S"
)

def start():
    logging.info(f"\n  📡 ESTABLECIENDO CONEXIONES 🔌 🏢🏬 ...")
    control()
    
start()