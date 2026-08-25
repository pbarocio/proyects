import requests
import datetime
import logging
import json
import file_utils as f_u
from config import get_config

def get_api_router(config, branch_name, branch_ip):
    api_port = config["api_port"]
    api_user = config["api_user"]
    api_password = config["api_password"]

    url = f"http://{branch_ip}:{api_port}/rest/ip/route"
    params = {
        "dst-address" : "0.0.0.0/0",
        ".proplist": "comment,disabled,inactive,dst-address,gateway,distance,active"
    }

    try:
        emoji1 ="🔐"
        emoji2 = "✅"
        logging.info(f"CONECTANDO A {emoji1:^2}{branch_name:^13}{emoji2:^2}...")
        
        response = requests.get(
            url,
            params=params,
            auth=(api_user, api_password),
            timeout=5
        )
        #response.raise_for_status()
        
        rutas_raw = response.json()       
        
        return True, rutas_raw, []
        
    except requests.exceptions.Timeout:
        logging.error(f"🚨 ¡¡¡TIMEOUT EN \"{branch_name}\"!!! NO HAY RESPUESTA DEL ROUTER... ❌")
        return False, [], "Timeout al conectar con el router"
    except requests.exceptions.HTTPError as e:
        logging.critical(f"💥 ¡¡¡Error HTTP en \"{branch_name}\" ⚠️ {response.status_code}: {e} \n{str(e)}", exc_info=True)
        return False, [], f"Error HTTP {response.status_code}: {e}"
    except requests.exceptions.RequestException as e:
        logging.critical(f"💥 Error al consultar la API en \"{branch_name}\" ⚠️ {e}", exc_info=True)
        return False, [], f"💥 Error al consultar la API ⚠️ {e}"
    except Exception as e:
        emoji ="🔴"
        emoji2 ="⚠️⚠️⚠️"
        logging.critical(f"\"{emoji2:^6}{emoji:^3}{branch_name:^10}\"ESTÁ FUERA‼️\n{error}", exc_info=True)
        return False, [], f"Error de conexión: {str(e)}"