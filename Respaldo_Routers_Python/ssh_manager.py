from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
from paramiko.ssh_exception import SSHException
from netmiko import ConnectHandler #Librería para manejar conexión SSH al router y funcionalidades sendCommand() disconnect()
from alert_manager import send_notification
import logging

def connect_router(branch_name,branch_ip,config):
    connection_data = { # Definimos los parámetros de la conexión
        'device_type': config["device_type"],
        'host': branch_ip,
        'username': config["username"],
        'port': config["port"],
        'use_keys': True,
        'key_file': config["key_path"],
        'timeout': 30,           # Timeout global de la conexión (espera a que el router responda)
        'session_timeout': 30,   # Timeout para comandos (espera a que termine el comando)
    }
    
    try:
        ssh_session = ConnectHandler(**connection_data) # Abrimos el puente SSH
        
        return ssh_session
    except NetmikoTimeoutException: # El Mikrotik no responde (enlace muerto, sin luz, IP mal)
        logging.warning(f"❌ ¡¡¡TIMEOUT EN {branch_name}! NO HAY RESPUESTA DEL ROUTER...")
        send_notification(config,f"🛑 {branch_name} ESTÁ INACCESIBLE (Timeout).")
        return []
    
    except NetmikoAuthenticationException: # Alguien le movió al usuario o contraseña del Mikrotik
        logging.error(f"🔐 ¡¡¡ERROR DE AUTENTICACIÓN EN {branch_name}!!! CREDENCIALES INCORRECTAS.,.")
        send_notification(config,f"⚠️ ALERTA DE SEGURIDAD:\nCREDENCIALES RECHAZADAS EN {branch_name}.")
        return []
    
    except (SSHException, Exception) as e: # Un error raro del protocolo SSH o cualquier otra falla inesperada
        logging.critical(f"💥 ¡¡¡ERROR INESPERADO EN {branch_name}: {str(e)}")
        send_notification(config,f"🚨 ¡¡¡FALLA CRÍTICA SSH EN {branch_name}: \n{str(e)}")
        return []