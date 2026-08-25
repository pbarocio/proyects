import requests
import datetime
import logging
import json
import file_utils as f_u
from config import get_config

def normalize_route_state(route_data: dict) -> str:
    """Traduce el JSON crudo de MikroTik a un estado/flag normalizado."""
    is_disabled = route_data.get("disabled") == "true"
    is_active = route_data.get("active") == "true"
    is_inactive = route_data.get("inactive") == "true"

    if is_disabled:
        return "X"
    if is_active:
        return "As"
    if is_inactive:
        return "Is"
    
    return "s"  # Backup en espera (standby)

def read_current_status():
    current_timestamp = str(int(datetime.datetime.now().timestamp())) #TimeStamp Actual
    empty_timestamp = "-" #Timestamp para enlaces activos
    data = get_config()
    api_port = data["api_port"]
    api_user = data["api_user"]
    api_password = data["api_password"]

    ROUTER_IP = "10.147.17.1"

    url = f"http://{ROUTER_IP}:{api_port}/rest/ip/route"
    params = {
        "dst-address" : "0.0.0.0/0",
        ".proplist": "comment,disabled,inactive,dst-address,gateway,distance,active"
    }

    try:
        response = requests.get(
            url,
            params=params,
            auth=(api_user, api_password),
            timeout=5
        )
        response.raise_for_status()
        
        rutas_raw = response.json()
        
        links = {}
        
# link_timestamp = str(f_u.get_current_timestamp(flag,current_timestamp,empty_timestamp))
# route_list[link] = {
#         "flag": flag,
#         "gateway": gateway,
#         "distance": distance,
#         "timestamp": link_timestamp,
#         "notification": None,
#         "lastrecord": current_timestamp,
#     }

        for item in rutas_raw:
            link = item.get("comment")
            if not link:
                continue
            
            flag = normalize_route_state(item)
            link_timestamp = f_u.get_current_timestamp(flag,current_timestamp,empty_timestamp)
                                
            links[link] = {
                "flag": flag,
                "gateway": item.get("gateway"),
                "distance" : item.get("distance"),
                "timestamp" : link_timestamp,
                "notification" : None,
                "lastrecord" : current_timestamp
            }
            print(f"Enlace: {link}, Flag: {flag}, Gateway: {item.get("gateway")}, Distance: {item.get("distance")}, Timestamp: {link_timestamp}, Notificacion: {None}, Lastrecord: {current_timestamp}")
            
        
        print("✅ Conexión exitosa a la REST API de MikroTik:")
        
    except requests.exceptions.Timeout:
            return False, [], "Timeout al conectar con el router"
    except requests.exceptions.HTTPError as e:
        return False, [], f"Error HTTP {response.status_code}: {e}"
    except requests.exceptions.RequestException as e:
            print(f"❌ Error al consultar la API: {e}")
    except Exception as e:
        return False, [], f"Error de conexión: {str(e)}"
    
read_current_status()