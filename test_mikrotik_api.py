import requests
import json

# Datos del router de tu casa
ROUTER_IP = "172.16.10.1"
PORT = 8080  # o 8080 si lo cambiaste
USER = "api_user"
PASSWORD = "B4r0c10#9475"

url = f"http://{ROUTER_IP}:{PORT}/rest/ip/route"
params = {".proplist": ".id,dst-address,gateway,distance,active,comment,disabled"}

try:
    response = requests.get(
        url,
        params=params,
        auth=(USER, PASSWORD),
        timeout=5
    )
    response.raise_for_status()
    
    rutas = response.json()
    print("✅ Conexión exitosa a la REST API de MikroTik:")
    print(json.dumps(rutas, indent=4))

except requests.exceptions.RequestException as e:
    print(f"❌ Error al consultar la API: {e}")