from prometheus_client import start_http_server, Gauge, Counter
import time
import logging
from config import get_config
import mikrotik_api as mkt
import alert_manager as am
import topology as tp

# Métrica de Prometheus (1 = UP / Activo, 0 = DOWN / Inactivo)
LINK_STATUS = Gauge(
    'mikrotik_link_status', 
    'Estado del enlace WAN (1: Activo, 0: Inactivo/Caido)', 
    ['branch', 'link', 'gateway']
)

def run_monitoring_cycle(config, branches):
    """Ejecuta una ronda de escaneo sobre todas las sucursales."""
    for branch_name, branch_ip in branches.items():
        success, routes, err = mkt.get_routes(
            ip=branch_ip,
            port=config["api_port"],
            user=config["api_user"],
            password=config["api_password"]
        )
        
        if not success:
            logging.error(f"🔴 Sucursal {branch_name} inaccesible: {err}")
            # Aquí disparas alerta de Telegram de sucursal caída si aplica
            continue
        
        # Procesamos las rutas devueltas por la API
        for route in routes:
            link_name = route.get("comment", "SIN_ETIQUETA")
            gateway = route.get("gateway", "N/A")
            is_active = 1.0 if route.get("active") == "true" else 0.0
            
            # Actualizamos la métrica en memoria de inmediato
            LINK_STATUS.labels(
                branch=branch_name, 
                link=link_name, 
                gateway=gateway
            ).set(is_active)

if __name__ == '__main__':
    # 1. Inicia el servidor de métricas en el puerto 8000
    start_http_server(8000)
    print("🚀 Exportador de Prometheus activo en http://0.0.0.0:8000/metrics")
    
    config = get_config()
    branches = tp.load_branches(config)
    
    # 2. Bucle continuo de monitoreo
    while True:
        run_monitoring_cycle(config, branches)
        time.sleep(15)  # Intervalo de escaneo en segundos