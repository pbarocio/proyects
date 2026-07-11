import logging
import datetime #Importar librería para manejar fecha y hora
import time
from pathlib import Path #Librería para manejar directorios cómo objetos
import subprocess #Librería para comandos de shell
from topology import load_branches
from ssh_manager import connect_router
from alert_manager import send_notification
from netmiko import FileTransfer
import paramiko

def get_src(branch_name,branch_dir,config,time_format,ssh_session):
    try:
        file_bckp_name = f"{branch_name}_{time_format}.rsc" #Definimos el nombre de los archivos rsc
        write_file = branch_dir / file_bckp_name #Ruta para escribir el resultado del comando /export
        command_export = "/export" #Comando de Mikrotik que nos extrae toda la configuración que se ejecuta actualmente
        data_export = ssh_session.send_command(command_export) #Enviamos el comando para su ejecución en el Router
        if data_export is not None:
            write_file.write_text(data_export) #Escribir con Path
            logging.info(f"✅ \"{file_bckp_name}\" GENERADO CORRECTAMENTE...")
        else:
            logging.error("¡¡¡ERROR!!! NO HAY ARCHIVO SRC QUÉ GENERAR!... ", exc_info=True)
            send_notification(config,f"❌ ¡ERROR! NO HAY CONFIGURACIONES EL EL ROUTER DE {branch_name}, NO HAY SRC QUÉ GENERAR")
    except Exception as error:
        logging.critical(f"❌ ERROR AL ESCRIBIR COMANDO EN {write_file} \n {error}", exc_info=True)
        send_notification(config,f"❌ ERROR AL GUARDAD COMANDO EN {write_file} \nREVISA EL SERVIDOR \n{error}")

def get_backup(branch_name, branch_dir, time_format, config, ssh_session):
    try:
        router_file = f"{branch_name}_{time_format}.backup" #Definir el nombre que va a tener el Binario en el router qué se descargará al equipo
        command_backup = f"/system backup save name={router_file} dont-encrypt=yes" #Comando de Mikrotik para que nos genere el respaldo binario
        local_file = branch_dir / router_file #Establecer ruta de binarios resultantes
        data_backup = ssh_session.send_command(command_backup)
        if "backup saved" in data_backup:
            logging.info(f"✅ \"{router_file}\" GENERADO CORRECTAMENTE...")
        else:
            logging.info(f"❌ ¡¡¡ERROR!!! {branch_name} NO PUDO GENERAR EL BINARIO: \"{router_file}\"... \"{data_backup}\"")
            #send_notification(config,f"❌¡¡ERROR!! {branch_name} NO PUDO GENERAR EL BINARIO: \n\"{router_file}\"...\n\"{data_backup}\"")
        return True, router_file, local_file
    except Exception as error:
        logging.error(f"❌ ERROR EJECUTANDO EL BACKUP {router_file} \n {error}")
        #send_notification(config,f"❌ ¡¡¡ERROR GENERANDO RESPALDO EN :{branch_name} \n NO SE PUDO EJECUTAR EL COMANDO \n{router_file}!")
        return False, router_file, local_file

def scp_connect_native(router_file, local_file, config, ssh_session):
    try:
        # ssh_port = config["port"]
        # key_path = config["key_path"]
        # user_router = config["username"]
        # scp_command = [
        #     "scp",
        #     "-P", str(ssh_port),
        #     "-i", key_path,
        #     f"{user_router}@{branch_ip}:{router_file}",
        #     str(local_file),
        # ]
        # subprocess.run(scp_command, check=True, capture_output=True, text=True)
        # scp_command = f"scp -P {ssh_port} -i {key_path} {user_router}@{branch_ip}:{router_file} {local_file}" # Construir el comando scp
        # subprocess.run(scp_command, shell=True, check=True, capture_output=True, text=True) #Ejecutar el comando SCP para copiar el archivo del router
        #paramiko_client = ssh_session.remote_conn
        
        # transport = ssh_session.remote_conn.transport
        # sftp = transport.open_sftp()
        
        # sftp = ssh_session.remote_conn.open_sftp()
        # sftp.get(router_file, str(local_file))
        # sftp.close()
        # with FileTransfer(ssh_conn=ssh_session, source_file=router_file, dest_file=local_file, direction='get') as scp_transfer:
        #     if scp_transfer.check_file_exist():
        #         logging.info("📍 El archivo existe en el MikroTik. Verificando tamaño...")
        #         logging.info(f"✅ \"{router_file}\" DESCARGADO CORRECTAMENTE...")
        
        transport = ssh_session.remote_conn.transport
        # 2. Crear un cliente SFTP directamente desde el Transport
        sftp = paramiko.SFTPClient.from_transport(transport)
        # 3. Descargar el archivo
        sftp.get(router_file, str(local_file))
        # 4. Cerrar el canal SFTP
        sftp.close()
        logging.info(f"✅ \"{local_file}\" DESCARGADO CORRECTAMENTE...")
        return True
    # except subprocess.CalledProcessError as e:
    #     logging.error(f"❌ SCP falló: {e.stderr}")
    #     return False
    except Exception as e:
        logging.error(f"❌ ERROR AL COPIAR {router_file} EN EL SERVIDOR REVISA QUÉ ESTÉ ENCENDIDO\n{e}", exc_info=True)
        return False
        #send_notification(config,f"❌ ERROR AL COPIAR {router_file} EN EL SERVIDOR \nREVISA QUÉ ESTÉ ENCENDIDO")

def remove_backup_file(router_file, config, ssh_session):
    try:
        remove_command = f"/file remove [find name={router_file}]" #Construir el comando para eliminar el archivo generado en el Router
        data_remove = ssh_session.send_command(remove_command) #Enviamos el comando de eliminar al router
        if "no such item" in data_remove.lower() or "failure" in data_remove.lower():
            logging.info(f"\n *** ⚠️ ATENCIÓN: NO SE PUDO ELIMINAR {router_file} DEL ROUTER. REVISAR MANUALMENTE... \n CERRANDO CONEXIÓN...  \n")
            send_notification(config,f"⚠️ ATENCIÓN: NO SE PUDO ELIMINAR {router_file} DEL ROUTER. \nREVISAR MANUALMENTE... \n")
        else:
            logging.info(f"🧹 \"{router_file}\" ELMINADO CORRECTAMENTE DEL ROUTER...")
    except Exception as error:
        logging.error(f"❌ ERROR ELIMINANDO {router_file} \n {error}")

def orchestration(config,bckps_dir):
    try:
        ahora = datetime.datetime.now() #Extraemos la fecha y la hor y después la formateamosbranch_ip
        time_format = ahora.strftime("%Y-%m-%d_%H-%M-%S")
        branches = load_branches(config)
        logging.info("=" * 100 + "\n\t\t\t\t\t\tGENERANDO RESPALDOS DE ROUTERS AGROCISA\n" + "=" * 130)
        for branch_name, branch_ip in branches.items():
            try:
                branch_dir = bckps_dir / str(branch_name) # Definir la ruta del Directorio de la Sucursal
                branch_dir.mkdir(parents=True, exist_ok=True) # Crear directorios si no existen
                logging.info("*" * 70) 
                logging.info(f"*** 📡 INTENTANDO CONEXIÓN A {branch_name.upper()} ({branch_ip}) .... ")
                logging.info("*" * 100)
                ssh_session = connect_router(branch_name, branch_ip, config)
                get_src(branch_name, branch_dir, config, time_format, ssh_session) #Correr el backup de rsc
                success, router_file, local_file = get_backup(branch_name,branch_dir,time_format,config,ssh_session)
                if success: #Sí la ejecución del backup se hace con éxito
                    success_scp = scp_connect_native(router_file, local_file, config, ssh_session) #Descargamos el backup del router por scp al directorio de destino
                    remove_backup_file(router_file,config,ssh_session) #Eliminamos el archivo del router
            except Exception as error:
                logging.error(f"❌ Flujo interrumpido en {branch_name} debido a un fallo: {error}", exc_info=True)
            finally:
                    ssh_session.disconnect()
                    logging.info(f"*** SE CERRÓ LA SESIÓN SSH CON \"{branch_name.upper()}\" 🔓...")
            
        send_notification(config,f"💾 LOS RESPALDOS DE LOS ROUTERS FUERON GENERADOS CON ÉXITO... ✅")
    except Exception as error:
        logging.info(f"❌ ERORR AL GENERAR LOS RESPALDOS DE LOS ROUTERS... \n{error}", exc_info=True)
        send_notification(config,f"❌ ERORR AL GENERAR LOS RESPALDOS DE LOS ROUTERS... \n{error}")