import logging
import datetime #Importar librería para manejar fecha y hora
from pathlib import Path #Librería para manejar directorios cómo objetos
import subprocess #Librería para comandos de shell
from topology import load_branches
from ssh_manager import connect_router
from alert_manager import send_notification

def get_src(branch_name,branch_ip,branch_dir,command_export,config,time_format):
    try:
        file_bckp_name = f"{branch_name}_{time_format}.rsc" #Definimos el nombre de los archivos rsc
        write_file = branch_dir / file_bckp_name #Ruta para escribir el resultado del comando /export
        data_export = connect_router(branch_name,branch_ip,command_export,config) #Enviamos el comando para su ejecución en el Router
        if data_export is not None:
            write_file.write_text(data_export) #Escribir con Path
            logging.info(f"✅ \"{file_bckp_name}\" GENERADO CORRECTAMENTE...")
        else:
            logging.error("¡¡¡ERROR!!! NO HAY ARCHIVO SRC QUÉ GENERAR!... ", exc_info=True)
            send_notification(config,f"❌ ¡ERROR! NO HAY CONFIGURACIONES EL EL ROUTER DE {branch_name}, NO HAY SRC QUÉ GENERAR")
    except Exception as error:
        logging.critical(f"❌ ERROR AL ESCRIBIR COMANDO EN {write_file} \n {error}", exc_info=True)
        send_notification(config,f"❌ ERROR AL GUARDAD COMANDO EN {write_file} \nREVISA EL SERVIDOR \n{error}")

def get_backup(branch_name,branch_ip,command_backup,router_file,config):
    try:
        data_backup = connect_router(branch_name,branch_ip,command_backup,config)
        if "backup saved" in data_backup:
            logging.info(f"✅ \"{router_file}\" GENERADO CORRECTAMENTE...")
        else:
            logging.info(f"❌ ¡¡¡ERROR!!! {branch_name} NO PUDO GENERAR EL BINARIO: \"{router_file}\"...\n\"{data_backup}\"")
            send_notification(config,f"❌¡¡ERROR!! {branch_name} NO PUDO GENERAR EL BINARIO: \n\"{router_file}\"...\n\"{data_backup}\"")
            raise RuntimeError(f"Fallo al generar backup en el router: {router_file}")
    except Exception as error:
        logging.error(f"❌ ERROR EJECUTANDO EL BACKUP {router_file} \n {error}")
        send_notification(config,f"❌ ¡¡¡ERROR GENERANDO RESPALDO EN :{branch_name} \n NO SE PUDO EJECUTAR EL COMANDO \n{router_file}!")

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
        logging.info(f"✅ \"{router_file}\" DESCARGADO CORRECTAMENTE...")
    except subprocess.CalledProcessError as e:
        logging.error(f"❌ SCP falló: {e.stderr}")
        send_notification(config,f"❌ ERROR AL COPIAR {router_file} EN EL SERVIDOR \nREVISA QUÉ ESTÉ ENCENDIDO")

def remove_backup_file(branch_name,branch_ip,remove_command,router_file,config):
    try:
        data_remove = connect_router(branch_name,branch_ip,remove_command,config) #Enviamos el comando de eliminar al router
        if "no such item" in data_remove.lower() or "failure" in data_remove.lower():
            logging.info(f"\n *** ⚠️ ATENCIÓN: NO SE PUDO ELIMINAR {router_file} DEL ROUTER. REVISAR MANUALMENTE... CERRANDO CONEXIÓN...")
            send_notification(config,f"⚠️ ATENCIÓN: NO SE PUDO ELIMINAR {router_file} DEL ROUTER. \nREVISAR MANUALMENTE... \n")
        else:
            logging.info(f"\n🧹 \"{router_file}\" ELMINADO CORRECTAMENTE DEL ROUTER...\n")
    except Exception as error:
        logging.error(f"❌ ERROR ELIMINANDO {router_file} \n {error}")

def orchestration(config,bckps_dir):
    try:
        ahora = datetime.datetime.now() #Extraemos la fecha y la hor y después la formateamosbranch_ip
        time_format = ahora.strftime("%Y-%m-%d_%H-%M-%S")
        branches = load_branches(config)
        logging.info("=" * 100 + "\n\t\t\t\t\t\tGENERANDO RESPALDOS DE ROUTERS AGROCISA\n" + "=" * 130)
        for branch_name, branch_ip in branches.items():
            branch_dir = bckps_dir / str(branch_name) # Definir la ruta del Directorio de la Sucursal
            branch_dir.mkdir(parents=True, exist_ok=True) # Crear directorios si no existen
            logging.info("*" * 70 + "\n" + f"*** 📡 INTENTANDO CONEXIÓN A {branch_name.upper()} ({branch_ip}) .... " + "\n" + "*" * 100)
            command_export = "/export" #Comando de Mikrotik que nos extrae toda la configuración que se ejecuta actualmente
            get_src(branch_name,branch_ip,branch_dir,command_export,config,time_format) #Correr el backup de rsc
            router_file = f"{branch_name}_{time_format}.backup" #Definir el nombre que va a tener el Binario en el router qué se descargará al equipo
            command_backup = f"/system backup save name={router_file} dont-encrypt=yes" #Comando de Mikrotik para que nos genere el respaldo binario
            local_file = branch_dir / router_file #Establecer ruta de binarios resultantes
            get_backup(branch_name,branch_ip,command_backup,router_file,config)
            scp_connect(branch_ip,router_file,local_file,config) #Descargamos el backup del router por scp al directorio de destino
            remove_command = f"/file remove [find name={router_file}]" #Construir el comando para eliminar el archivo generado en el Router
            remove_backup_file(branch_name,branch_ip,remove_command,router_file,config)
            
        #send_notification(config,f"💾 LOS RESPALDOS DE LOS ROUTERS FUERON GENERADOS CON ÉXITO... ✅")
    except Exception as error:
        send_notification(config,f"❌ ERORR AL GENERAR LOS RESPALDOS DE LOS ROUTERS... \n{error}")