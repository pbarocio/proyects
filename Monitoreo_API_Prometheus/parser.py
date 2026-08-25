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

def parse_api_output(registers, current_timestamp, empty_timestamp):
    try:
        links = {}
        
        for item in registers:
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
        return links
            
    except Exception as error:
            logging.error(f"{error}\n\n❌ ‼️ 🔴 ERROR PARSEANDO LOS REGISTROS de {registers} ===> {error} ‼️", exc_info=True)
            return None