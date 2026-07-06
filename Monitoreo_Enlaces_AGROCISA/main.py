import logging
from state_manager import control

logging.basicConfig(
    filename="monitoreo_enlaces_agrocisa.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s - %(filename)s",
    datefmt="%Y-%m-%d_%H:%M:%S"
)

def start():
    print(f"\n  📡 ESTABLECIENDO CONEXIONES 🔌 🏢🏬 ...")
    control()
    
start()