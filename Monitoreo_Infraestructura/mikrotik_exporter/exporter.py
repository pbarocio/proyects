from prometheus_client import Gauge, Counter, start_http_server

LINK_STATUS = Gauge(
    'mikrotik_link_status', 
    'Estado del enlace WAN (1: Activo, 0: Inactivo/Caido)', 
    ['branch', 'link', 'gateway']
)

CICLOS_TOTAL = Counter(
    'monitoreo_ejecuciones_total', 
    'Total de ciclos de monitoreo completados'
)

def update_link_metric(branch, link, gateway, is_active):
    valor = 1.0 if is_active else 0.0
    LINK_STATUS.labels(branch=branch, link=link, gateway=gateway).set(valor)

def increment_execution():
    CICLOS_TOTAL.inc()
    
def start_metrics_server(port=8000):
    start_http_server(port)