from prometheus_client import start_http_server, Gauge
import time
import random

# Definimos la métrica: 1 = Arriba, 0 = Caído
LINK_STATUS = Gauge('mikrotik_link_status', 'Estado del enlace 1 up 0 down', ['branch', 'link'])

if __name__ == '__main__':
    # 1. Abre un mini servidor HTTP en el puerto 8000
    start_http_server(8000)
    print("Exportador corriendo en http://localhost:8000/metrics")

    # 2. Simulador de tu ciclo de monitoreo
    while True:
        # Aquí es donde tu Netmiko actualizaría el valor real
        LINK_STATUS.labels(branch='PENJAMO', link='TELMEX-1').set(1)
        LINK_STATUS.labels(branch='LAPIEDAD', link='TELMEX-1').set(random.choice([0, 1]))
        time.sleep(5)