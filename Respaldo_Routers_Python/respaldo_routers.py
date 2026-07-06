import datetime #Importar librería para manejar fecha y hora
from pathlib import Path #Librería para manejar directorios cómo objetos
from netmiko import ConnectHandler #Librería para manejar conexión SSH al router y funcionalidades sendCommand() disconnect()
import subprocess #Librería para comandos de shell
import json
import telebot #Librería para mensajes de Telegram
from config import get_config

def load_branches(config):
    try:
        with open(config["branches_file"], "r", encoding="utf-8") as file:
            branches = json.load(file)
        return branches
    except Exception as error:
        print("❌ ¡¡¡ERROR AL CARGAR EL ARCHIVO DE BRANCHES")
        print("\n" + "=" * 60 + f"❌ ¡¡¡ERROR AL CARGAR EL ARCHIVO BRANCHES !!!\n: {error}\n" + "=" * 60 + "\n")

def connect_router(branch_name,branch_ip,command,config):
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
        connection = ConnectHandler(**connection_data) # Abrimos el puente SSH
        data = connection.send_command(command) ##Eviar comando al router
        connection.disconnect()
        
        return data
        
    except Exception as error:
        print("\n" + "=" * 60 + f"❌ ¡¡¡ ERROR AL CONECTARSE A {branch_name} \n: {error}\n" + "=" * 60 + "\n")
        return None

def get_src(branch_name,branch_ip,branch_dir,command_export,config,time_format):
    try:
        file_bckp_name = f"{branch_name}_{time_format}.rsc" #Definimos el nombre de los archivos rsc
        write_file = branch_dir / file_bckp_name #Ruta para escribir el resultado del comando /export
        data_export = connect_router(branch_name,branch_ip,command_export,config) #Enviamos el comando para su ejecución en el Router
        if not data_export is None:
            write_file.write_text(data_export) #Escribir con Path
            print(f"\n✅ \"{file_bckp_name}\" GENERADO CORRECTAMENTE...")
        else:
            print("NO HAY ARCHIVO SRC QUÉ GENERAR")
    except Exception as error:
        print(f"❌ ERROR AL ESCRIBIR COMANDO EN {write_file} \n {error}")

def get_backup(branch_name,branch_ip,command_backup,router_file,config):
    try:
        data_backup = connect_router(branch_name,branch_ip,command_backup,config)
        print(f"\n✅ \"{router_file}\" GENERADO CORRECTAMENTE...")
    except Exception as error:
        print(f"❌ ERROR EJECUTANDO EL BACKUP {router_file} \n {error}")

def scp_connect(branch_ip,router_file,local_file,config):
    try:
        ssh_port = config["port"]
        key_path = config["key_path"]
        user_router = config["username"]
        scp_command = [
            "scp",
            "-P", str(ssh_port),
            "-i", key_path,
            f"{user_router}@{branch_ip}:{router_file}",
            str(local_file),
        ]
        subprocess.run(scp_command, check=True, capture_output=True, text=True)
        #scp_command = f"scp -P {ssh_port} -i {key_path} {user_router}@{branch_ip}:{router_file} {local_file}" # Construir el comando scp
        #subprocess.run(scp_command, shell=True, check=True, capture_output=True, text=True) #Ejecutar el comando SCP para copiar el archivo del router
        print(f"\n✅ \"{router_file}\" DESCARGADO CORRECTAMENTE...")
    except subprocess.CalledProcessError as e:
        print(f"❌ SCP falló: {e.stderr}")

def remove_backup_file(branch_name,branch_ip,remove_command,router_file,config):
    try:
        data_remove = connect_router(branch_name,branch_ip,remove_command,config) #Enviamos el comando de eliminar al router
        if "no such item" in data_remove.lower() or "failure" in data_remove.lower():
            print(f"\n *** ⚠️ ATENCIÓN: NO SE PUDO ELIMINAR {router_file} DEL ROUTER. REVISAR MANUALMENTE...")
            print("\n CERRANDO CONEXIÓN...  \n")
        else:
            print(f"\n🧹 \"{router_file}\" ELMINADO CORRECTAMENTE DEL ROUTER...\n")
    except Exception as error:
        print(f"❌ ERROR ELIMINANDO {router_file} \n {error}")
        
def send_notification(config,message):
    try:
        bot = telebot.TeleBot(config["telegram_token"]) #Definimos el bot
        bot.send_message(config["telegram_chat_id"], message)
    except Exception as e:
        print(f"❌ Error al enviar mensaje a Telegram: {e}")

def orchestration():
    ahora = datetime.datetime.now() #Extraemos la fecha y la hor y después la formateamosbranch_ip
    time_format = ahora.strftime("%Y-%m-%d_%H:%M:%S")
    config = get_config()
    bckps_dir = config["backups_dir"]
    bckps_dir.mkdir(parents=True, exist_ok=True) # Crear la carpeta si no existe
    branches = load_branches(config)
    for branch_name, branch_ip in branches.items():
        branch_dir = bckps_dir / str(branch_name) # Definir la ruta del Directorio de la Sucursal
        branch_dir.mkdir(parents=True, exist_ok=True) # Crear directorios si no existen
        print("*" * 65 + "\n" + f"*** 📡 INTENTANDO CONEXIÓN A {branch_name.upper()} ({branch_ip}) .... " + "\n" + "*" * 65)
        command_export = "/export" #Comando de Mikrotik que nos extrae toda la configuración que se ejecuta actualmente
        get_src(branch_name,branch_ip,branch_dir,command_export,config,time_format) #Correr el backup de rsc
        router_file = f"{branch_name}_{time_format}.backup" #Definir el nombre que va a tener el Binario en el router qué se descargará al equipo
        command_backup = f"/system backup save name={router_file} dont-encrypt=yes" #Comando de Mikrotik para que nos genere el respaldo binario
        local_file = branch_dir / router_file #Establecer ruta de binarios resultantes
        get_backup(branch_name,branch_ip,command_backup,router_file,config)
        scp_connect(branch_ip,router_file,local_file,config) #Descargamos el backup del router por scp al directorio de destino
        remove_command = f"/file remove [find name={router_file}]" #Construir el comando para eliminar el archivo generado en el Router
        remove_backup_file(branch_name,branch_ip,remove_command,router_file,config)
    
    send_notification(config,f"💾 EL RESPALDO DE LOS ROUTERS FUE GENERADO CON ÉXITO... ✅")

orchestration()