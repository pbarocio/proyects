import logging
import datetime #Importar librería para manejar fecha y hora
import time #Libreria para poder usar sleep
from pathlib import Path #Librería para manejar directorios cómo objetos
import tempfile #Librería para usar archivos temporales
from config import get_config
import ssh_utils as ssh
import parser as parser
import file_utils as f_u
import topology as tp
import logger as logg              

def handle_branch_down(ssot,current_branch,current_timestamp):
    try:
        branch_status = {}
        for key, links in ssot.items():
            if current_branch in key:
                for link, data in links.items():
                    data["timestamp"] = current_timestamp
                    branch_status[link] = data
        return branch_status #Enviamos los enlaces del SSOT para escribirlos down en el Estado_Actual con sus nombres
        
    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR USANDO EL SSOT ‼️ -> {error}\n", exc_info=True)
        return []

def get_current_state(config,previous_state,branches,ssot,current_timestamp,empty_timestamp,): #Extraer el estado actual de todos los enlaces
    try:
        current_state = {} #Declaramos el diccionario maestro de los Estatus actuales
        current_state["BRANCHES-DOWN"] = {}
        notification = True
        for branch, branch_ip in branches.items(): #Iteramos las sucursales para extraer las tablas de los routers
            if "BRANCHES-DOWN" in previous_state and branch in previous_state["BRANCHES-DOWN"]:
                notification = previous_state["BRANCHES-DOWN"][branch]
            else:
                notification = True
            connection, command = ssh.connect_router(config,branch,branch_ip)  #Intentamos la conexión al router
            if (connection):  #Sí la conexión se concreta Parseamos las rutas que resulten de la consulta del router
                current_state[branch] = parser.parse_router_output(command,current_timestamp,empty_timestamp)
                current_state["BRANCHES-DOWN"][branch] = True
            else:
                current_state[branch] = handle_branch_down(ssot,branch,current_timestamp) #Sí la conexión no funciona invocamos a la función que maneja los enlaces caídos con valores del SSOT
                notification = logg.print_out_site(branch,notification) #Enviamos la alerta de Sítio caído por Telegram
                current_state["BRANCHES-DOWN"][branch] = notification
        return current_state #Enviamos el diccionario maestro de la conexión actual
    except Exception as error:
        logging.error(f"\n\n ❌ ‼️ 🔴 ERROR EXTRAYENDO LOS REGISTROS de {branch} ‼️===> {error}", exc_info=True)
        
def control():
    try:
        now = datetime.datetime.now() #Extraer datos de fecha actual y hora
        date = now.strftime("%Y-%m-%d") #Dar formato a la fehca y hora para escribir el día en el archivo Histrórico
        year = now.strftime("%Y") #Extraer año para estructurar el nombre del Archivo Histórico
        month = now.strftime("%m") #Extraer el mes para estructurar el nombre del Archivo Histórico
        day = now.strftime("%A") #Extaemos el día para escribir el día en el archivo Histrórico
        hour = now.strftime("%H:%M:%S") #Extraemos la hora para escribir el día en el archivo Histrórico
        config = get_config()
        branches = tp.load_topology(config,"BRANCHES")
        ssot = tp.load_topology(config,"SSOT")
        tmp_dir = Path(tempfile.gettempdir()) #Expandir directorio temporal del SO
        counter_file = Path(tmp_dir / "counter.json") #Definimos la ruta del archivo que aloja el contador de ejecuciones
        counter = f_u.load_counter(counter_file) #Cargamos el # de ejecución
        log_dir = config["log_dir"] #DEfinimos el directorio de los archivos
        log_dir.mkdir(parents=True, exist_ok=True) #Crear el directorio de logs sí no existe
        current_state_file = log_dir / "Estado_Actual.json"
        historical_file = log_dir / f"Historical-{year}-{month}.csv" #Crear archivo Histórico.csv
        current_timestamp = str(int(datetime.datetime.now().timestamp())) #TimeStamp Actual
        empty_timestamp = "-" #Timestamp para enlaces activos
        previous_state = f_u.load_previous_state(current_state_file) #Extraemos los valores anteriores del estado previo
        current_state = get_current_state(config,previous_state,branches,ssot,current_timestamp,empty_timestamp) #Cargamos el estado actual
        for current_branch, links in current_state.items(): #Iteramos sobre los enlaces de Cada Sucursal para acceder a los elementos
            if(current_branch == "BRANCHES-DOWN"):
                continue
            else:
                print("\n" + "=" * 100)
                print(f"  📡 ESTATUS SUCURSAL 🔌 A {current_branch:^11} 🏢🏬 ...")
                print("=" * 100 + "\n")
                for link, values in links.items():
                    current_link = link
                    current_flag = values["flag"]
                    current_gateway = values["gateway"]
                    current_distance = values["distance"]
                    current_link_timestamp = values["timestamp"]
                    previous_flag = current_flag
                    previous_timestamp = current_link_timestamp
                    notification = 0
                    logg.print_current_state(current_link,current_flag,current_gateway,current_distance) #Mandamos a consola la impresión visual el enlace con su estado actual   
                    previous_flag, previous_timestamp, notification = f_u.get_previous_state(previous_state,current_branch,current_link,current_flag,current_link_timestamp) #Extraemos los valores útiles del Estado Anterior
                    logging.info("=" * 90)
                    logging.info(f"Current Branch => {current_branch} => Current link => {current_link} => Previous Flag => \"{previous_flag}\" => Current Flag => \"{current_flag}\" => Previous Timestamp => \"{previous_timestamp}\" => Current Timestamp => \"{current_timestamp}\"")
                    if "Is" in current_flag: #Validamos sí el enlace actual está caído
                        logging.info("Estado actual es \"Is\"")
                        notification, write_timestamp = handle_down_link(current_branch,current_link,current_flag,previous_flag,previous_timestamp,current_timestamp,notification) #Llamamos la función para hacer las validaciones de estado, sí había caída previa o es nueva caída, y recibimos el timestam correcto, sí es el previo o el actual
                        logging.info(f"¡Ésto queda después de Validar los enlaces caídos! (handle_down_link) | Notificación => \"{notification}\" y WriteTimestamp \"{write_timestamp}\"")
                        f_u.write_historical_file(historical_file,date,hour,day,current_branch,current_link,current_flag,current_gateway,current_distance,str(counter))#Escribimos archivos Estado_Actual e Histórico con el timestamp correspondiente
                        values["timestamp"] = write_timestamp
                        values["lastrecord"] = f"{date}_{hour}"
                        values["notification"] = notification
                    else: #El enlace está activo o en Failover -> Cambió el enlace principal o sigue sin cambios
                        logging.info("El Estado Actual Es Failover o Enlace Principal \"s\" o \"As\"")
                        notification, write_timestamp = handle_up_link(current_branch,current_link,current_flag,previous_flag,previous_timestamp,current_timestamp,empty_timestamp,notification) #Llamamos a la función que valida el estado actual cómo activo o en Failover para saber sí se recuperó un enlace o sí ya estaba activo previamente
                        f_u.write_historical_file(historical_file,date,hour,day,current_branch,current_link,current_flag,current_gateway,current_distance,str(counter)) #Escribimos archivos Estado_Actual e Histórico con el timestamp actual debido a qué el enlace está activo
                        logging.info(f"¡Ésto queda después de validar los Estados Activos! (handle_up_link) | Notificación => \"{notification}\" y WriteTimestamp \"{write_timestamp}\"")
                        values["timestamp"] = write_timestamp
                        values["lastrecord"] = f"{date}_{hour}"
                        values["notification"] = notification
            
        f_u.write_json_files(current_state_file,current_state)
        
        logging.info("\n" + "=" * 102 + f"\n 💡 ÉSTE SCRIPT SE HA EJECUTADO **{counter}** VECES 🏁 EL DÍA DE HOY, PUEDES VER LOS DETALLES EN EL LOG 📋...\n" + "=" * 102)
        counter = counter + 1
        f_u.write_json_files(counter_file,counter)
    except Exception as error:
        logging.critical("ERROR EJECUTANDO EL CONTROL DE FLUJO", exc_info=True)
        raise

def handle_down_link(current_branch,current_link,current_flag,previous_flag,previous_timestamp,current_timestamp,notification): #Manejamos los enlaces caídos vs los estados previos
    if not "Is" in previous_flag and "Is" in current_flag: #Validamos sí el estado previo era arriba y en el actual es abajo -> Se acaba de caer
        logging.info("Estado Previo no estaba caído \"As\" o \"s\" Y El Estado Actual Sí, o sea se acaba de caer")
        logging.warning(f"[{current_branch}-{current_link}] ⚠️ ESTÁ FUERA ⚠️‼️")
        print(f"⚠️ ESTÁ FUERA ⚠️‼️")
        return notification, current_timestamp #Devolvemos cómo timestamp el actual para preservar la hora de la caída
    else:
        if "Is" in previous_flag and "Is" in current_flag: #Validamos sí el estado previo del enlace y el actual -> down para saber sí el sitio ya estaba caído.
            logging.info("Estado Previo y Estado Actual son \"Is\"")
            if not "-" in previous_timestamp: #Sí no hay un guión quiere decir que sí se registró un timestamp previo
                logging.info(f"Previous Timestamp no tiene \"-\" es ({previous_timestamp}) éso es correcto")
                elapsed_time = f_u.get_elapsed_time(previous_timestamp,current_timestamp)
                logging.info(f"Elapsed Timestamp => ({elapsed_time})")
                if elapsed_time == 0:
                    logging.info("Elapsed Time es 0 - O sea se acaba de caer...")
                    logging.info(f"⚠️ ESTÁ FUERA ⚠️‼️")
                    logging.warning(f"[{current_branch}-{current_link}] ⚠️ ESTÁ FUERA ⚠️‼️")
                    logging.info(f"Notification => \"{notification}\"")
                    logging.info(f"Se quedó Previous_Timestamp aunque se haya acabado de caer => \"{previous_timestamp}\"")
                    return notification, previous_timestamp
                else:
                    logging.info(f"Elapsped time no es \"0\" es ({elapsed_time})")
                    logging.info("*** AQUÍ DEBE ENVIAR LA NOTIFICACIÓN ***")
                    notification = logg.print_link_down_old(current_branch,current_link,elapsed_time,notification) #Imprimimos la función que muestra los detalles de un enlace que ya estaba caído y enviamos el tiempo que ha transcurrido
                    logging.info(f"Notification => \"{notification}\"")
                    logging.info(f"Se queda Previous_Timestamp (La anterior) => \"{previous_timestamp}\"")
                    return notification,previous_timestamp #Regrsamos el timestamp previo porque ya tenía un timestamp activo... 
            else:
                logging.critical("ERROR EL TIMESTAMP ESTÁ CÓMO SÍ HAYA ESTADO ACTIVO, INCOHERENCIA PORQUE EL ESTADO ES \"Is\"") #Validamos en caso de error  en el timestamp...
                return notification,previous_timestamp #Enviamos el enlace timestamp vacío porque no es coherente

def handle_up_link(current_branch,current_link,current_flag,previous_flag,previous_timestamp,current_timestamp,empty_timestamp,notification): #Validamos que el estado anterior haya estado en down y el actual esté activo o en Failover 
    if "Is" in previous_flag and not "Is" in current_flag: #Sí el status del estado previo es caído y el actual es activo o Failover quiere decir que el enlace se recuperó
        logging.info("Estado Previo era \"Is\" y Estado Actual es \"Is\" o \"s\"")
        if not "-" in previous_timestamp: #Sí no hay un guión quiere decir que el previous_state es correcto debe tener un timestamp
            logging.info("Sí ves ésto es porque No es guión Previous TimeStamp \"-\"")
            elapsed_time = f_u.get_elapsed_time(previous_timestamp,current_timestamp)
            logging.info("*** AQUÍ DEBE ENVIAR LA NOTIFICACIÓN ***")
            notification = logg.print_back_online_link(current_branch,current_link,elapsed_time,notification) #Se imprime en pantalla la alerta de recuperación de enlace
            logging.info("Regresa:")
            logging.info(f"Notification => {notification}")
            logging.info(f"Cómo el enlace está activo Empty_Timestamp => {empty_timestamp}")
            return notification, empty_timestamp #Enviamos el timestamp en blanco porque el enlace está activo
        else:
            logging.critical("ERROR EL TIMESTAMP ESTÁ CÓMO SÍ HAYA ESTADO ACTIVO, INCOHERENCIA PORQUE EL ESTADO PREVIO ES ES \"Is\"") #Sí hay un guión quiere decir que hubo un error guardando el timestamp de la caída
            return notification, empty_timestamp #Enviamos el enlace timestamp vacío porque no es coherente
    elif "As" in previous_flag and current_flag == "s": #Validar sí el enlace cambio a Failover
        logging.info("Sí ves ésto es porque Estado Previo es: \"As\" Y el Actual es \"s\"")
        logging.warning(f"[{current_branch}-{current_link}] CAMBIÓ A FAILOVER")
        logging.info("Regresa:")
        logging.info(f"Notification => {notification}")
        logging.info(f"Cómo el enlace está activo actualmente Empty_Timestamp => {empty_timestamp}")
        return notification, empty_timestamp #Se regresa el timestamp vacío porque el enlace está activo
    elif previous_flag == "s" and "As" in current_flag: #Validar sí cambió a Enlace Principal
        logging.info("Sí ves ésto es porque Estado Previo es \"s\" y el Estado Actual es \"As\"")
        logging.warning(f"[{current_branch}-{current_link}] ES EL ENLACE PRINCIPAL AHORA")
        logging.info("Regresa:")
        logging.info(f"Notification => {notification}")
        logging.info(f"Cómo el enlace está activo actualmente Empty_Timestamp => {empty_timestamp}")
        return notification,empty_timestamp #Se regresa el timestamp vacío porque el enlace está activo
    elif previous_flag == current_flag: #El enlace no cambió
        logging.info("Sí ves ésto es porque Estado Previo y Estado actual son iguales")
        logging.info(f"[{current_branch}-{current_link}] SIN CAMBIOS")
        logging.info("Regresa:")
        logging.info(f"Notification => {notification}")
        logging.info(f"Cómo el enlace está activo actualmente Empty_Timestamp => {empty_timestamp}")
        return notification,empty_timestamp #Se regresa el timestamp vacío porque el enlace está activo