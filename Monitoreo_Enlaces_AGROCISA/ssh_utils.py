import logging
from netmiko import ConnectHandler #Librería para manejar conexión SSH al router y funcionalidades sendCommand() disconnect()

def connect_router(config,branch_name,branch_ip):
    connection_data = { #Ingresamos los datos del router para la conexión
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
        connection = ConnectHandler(**connection_data) #Ejecutamos la conexión al router
        command = connection.send_command("/ip route print where dst-address=0.0.0.0/0") #Enviamos el comando al router y guardamos el resultado
        connection.disconnect() #Nos desconectamos de la sesión
        emoji1 ="🔐"
        emoji2 = "✅"
        print(f"\n  {emoji1:^2}{branch_name:^13}{emoji2:^2}...")
        logging.info(f"CONECTANDO A {emoji1:^2}{branch_name:^13}{emoji2:^2}...")
        command = command.strip().splitlines() #Limpiamos los espacios en blanco y dividimos la lectura en líneas
        command = command[3:] #Ignoramos las 3 primeras filas de la tabla de ruteo porque son informativas
        return True,command #Enviamos el resultado del comando
    
    except Exception as error:
        emoji ="🔴"
        emoji2 ="⚠️⚠️⚠️"
        logging.error(f"\n{emoji2:^6}{emoji:^3}{branch_name:^10}  ESTÁ FUERA‼️ \n\n{error}", exc_info=True)
        return False,[]