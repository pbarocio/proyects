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
        something_change = False
        write_time = False
        register_change = ""
        previous_state = f_u.load_previous_state(current_state_file) #Extraemos los valores anteriores del estado previo
        current_state = get_current_state(config,previous_state,branches,ssot,current_timestamp,empty_timestamp) #Cargamos el estado actual
        #Definimos los timestamps correctos para caídas y registros de escritura de archivos
        current_state_timestamps, something_change , write_time, previous_lastrecord, register_change = handle_timestamps(current_state, previous_state, current_timestamp)
        #Decidimos la escritura de los archivos
        handle_write_files(counter,counter_file,current_state_timestamps, current_state_file, historical_file, date, hour, day, something_change, write_time, previous_lastrecord, register_change, current_timestamp)
        
    except Exception as error:
        logging.critical(f"¡¡¡ERROR FATAL!!! \n{error}", exc_info=True)
        raise

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
            connection, command, error_msg = ssh.connect_router(config,branch,branch_ip)  #Intentamos la conexión al router
            if (connection):  #Sí la conexión se concreta Parseamos las rutas que resulten de la consulta del router
                current_state[branch] = parser.parse_router_output(command,current_timestamp,empty_timestamp)
                current_state["BRANCHES-DOWN"][branch] = True
            else:
                current_state[branch] = handle_branch_down(ssot,branch,current_timestamp) #Sí la conexión no funciona invocamos a la función que maneja los enlaces caídos con valores del SSOT
                notification = logg.print_out_site(branch,notification,error_msg) #Enviamos la alerta de Sítio caído por Telegram
                current_state["BRANCHES-DOWN"][branch] = notification
        return current_state #Enviamos el diccionario maestro de la conexión actual
    except Exception as error:
        logging.critical(f"\n\n ❌ ‼️ 🔴 ERROR EXTRAYENDO LOS REGISTROS de {branch} ‼️===> {error}", exc_info=True)

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

def handle_timestamps(current_state, previous_state, current_timestamp):
    try:
        something_change = False
        write_time = False
        previous_record = ""
        register_change = ""
        for current_branch, links in current_state.items(): #Iteramos sobre los enlaces de Cada Sucursal para acceder a los elementos y decidir los timestamps
                if(current_branch == "BRANCHES-DOWN"):
                    continue
                else:
                    print("\n" + "=" * 100)
                    print(f"  📡 ESTATUS SUCURSAL 🔌 A {current_branch:^11} 🏢🏬 ...")
                    print("=" * 100 + "\n")
                    for link, values in links.items():
                        current_link = link
                        current_flag = values.get("flag")
                        current_gateway = values.get("gateway")
                        current_distance = values.get("distance")
                        current_link_timestamp = values.get("timestamp")
                        current_link_lastrecord = values.get("lastrecord")
                        logging.info("=" * 210)
                        logging.info(f"Link Actual: [{current_branch}-{current_link}]")
                        previous_flag, previous_link_timestamp, notification, previous_link_lastrecord = "" , "" , True, "" #Inicializamos las variables
                        previous_flag, previous_link_timestamp, notification, previous_link_lastrecord = f_u.get_previous_state(previous_state, current_branch, current_link, current_flag,
                                                                                                                    current_link_timestamp, current_link_lastrecord) #Extraemos los valores útiles del Estado Anterior

                        logging.info(f"Previous_Flag => \"{previous_flag}\"")
                        logging.info(f"Current Flag => \"{current_flag}\"")
                        logging.info(f"Previous_link_timestamp => \"{previous_link_timestamp}\"")
                        logging.info(f"Current_Link_Timestamp => \"{current_link_timestamp}\"")
                        logging.info(f"Notification => \"{notification}\"")
                        logging.info(f"previous_link_lastrecord \"{previous_link_lastrecord}\"")
                        logging.info(f"Current_Link_Lastrecord \"{current_link_lastrecord}\"")
                        
                        logg.print_current_state(current_link, current_flag, current_gateway,current_distance) #Imprimimos en consola el estatus de los enlaces
                        write_timestamp, link_changed, event = "", False, "" #Inicializamos las variables de handle_link_change
                        notification, write_timestamp, link_changed, event = handle_link_change(previous_flag, current_flag, previous_link_timestamp, current_timestamp, notification, current_branch, current_link)
                        values["notification"] = notification
                        values["timestamp"] = write_timestamp
                        previous_record = previous_link_lastrecord
                        logging.info(f"handle_link_chage() | Notification => {notification} | Write_Timestamp => {write_timestamp} | Link_Changed => {link_changed} | Event => {event}")
                        
                        if (int(current_timestamp) - int(previous_link_lastrecord) > 600):
                            write_time = True
                        else:
                            values["lastrecord"] = previous_link_lastrecord
                        
                        if link_changed:
                            register_change = f"[\"{current_branch}-{current_link}\"] ↪️ (\"{previous_flag}\" <=> \"{current_flag}\")"
                            something_change = True

                        logging.info(f"El status de Something_Change => {something_change}")
                        logging.info(f"El status de Write_Time => {write_time}")
                        
        return current_state, something_change , write_time, previous_record, register_change
    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR VALIDANDO LOS TIMESTAMPS ‼️ -> {error}\n", exc_info=True)
        return [], [], [], [], []

def handle_link_change(previous_flag, current_flag, previous_link_timestamp, current_timestamp, notification, current_branch, current_link):
    try:
        empty_timestamp = "-"
        
        p_flag = "Is" if "Is" in previous_flag else previous_flag # Limíamos los String (ej. "Is " en lugar de "Is")
        c_flag = "Is" if "Is" in current_flag else current_flag

        match (p_flag, c_flag): # Evaluamos la tupla (Estado_Anterior, Estado_Actual)
            
            case ("As", "Is") | ("s", "Is"): #Enlace nuevo caído 8# 🚨 CAÍDA NUEVA: De estar arriba (Principal o Failover) a Caído)
                logging.info(f"El enlace cambia de (\"As\" => \"Is\") | (\"s\" => \"Is\")")
                logging.warning(f"⚠️ [{current_branch}-{current_link}] 🔴 ESTÁ FUERA 🚨")
                print(f"🔴 ESTÁ FUERA")
                logging.info(f"# Nueva Caída # | Notification => {notification} | Write_Timestamp => {current_timestamp} | Link_Changed => False | Event => NEW_LINK_OUT")
                return notification, current_timestamp, True, "NEW_LINK_OUT"

            case ("Is", "Is"): # ⏳ CAÍDA PREVIA: Sigue abajo, hay que calcular tiempo transcurrido
                logging.info(f"(\"Is\") => (\"Is\") # Caída Previa...#")
                if previous_link_timestamp != empty_timestamp:
                    logging.info(f"Previous_Timestamp no es un guión {previous_link_timestamp} ¡¡¡ES CORRECTO!!!")
                    elapsed_time = f_u.get_elapsed_time(previous_link_timestamp, current_timestamp)
                    logging.info(f"Elapsed time => ({elapsed_time})s ({int(elapsed_time / 60)}) min")
                    if elapsed_time == 0:
                        logging.warning(f"⚠️ [{current_branch}-{current_link}] 🔴 ESTÁ FUERA 🚨")
                        print(f"🔴 ESTÁ FUERA")
                        logging.info(f"# Caída Previa # | Notification => {notification} | Write_Timestamp => {current_timestamp} | Link_Changed => False | Event => NEW_LINK_OUT")
                        return notification, current_timestamp, False, "NEW_LINK_OUT"
                    else:
                        logging.info(f"*** AQUÍ DEBE ENVIAR LA NOTIFICACIÓN DE ENLACE CAÍDO A TELEGRAM (\"[{current_branch}-{current_link}\"] (\"{current_flag}\"), DEPENDIENDO DEL ESTADOO DE LA NOTIFICACIÓN ACTUAL (\"{notification}\") ***")
                        notification = logg.print_link_down_old(current_branch, current_link, elapsed_time, notification) # Alerta periódica de Telegram si aplica
                        logging.info(f"# Caída Previa # | Notification => {notification} | Write_Timestamp => {previous_link_timestamp} | Link_Changed => False | Event => LINK_OUT_PREVIOUS")
                        return notification, previous_link_timestamp, False, "LINK_OUT_PREVIOUS"
                logging.error(f"¡¡¡ERROR EN EL TIMESTAMP!!! Se regresa Notification => {notification} | Write_Timestamp => {current_timestamp} | Link_Changed => False | Event => PREVIOUS_TMESTAMP_ERROR")
                return notification, previous_link_timestamp, False, "PREVIOUS_TMESTAMP_ERROR"

            case ("Is", "As") | ("Is", "s"): # ✅ RECUPERACIÓN: Estaba abajo y revivió (ya sea en Principal o Failover)
                logging.info(f"✅ Cambio de (\"Is\" => \"As\") | (\"Is\" => \"s\") # Recuperación ... #")
                notification = True
                if previous_link_timestamp != empty_timestamp:
                    logging.info(f"Previous_Timestamp no es un guión {previous_link_timestamp} ¡¡¡ES CORRECTO!!!")
                    elapsed_time = f_u.get_elapsed_time(previous_link_timestamp, current_timestamp)
                    logging.info(f"Elapsed time => ({elapsed_time})s ({int(elapsed_time / 60)}) min")
                    logging.info(f"*** AQUÍ DEBE ENVIAR LA NOTIFICACIÓN DE ENLACE RECUPERADO (\"[{current_branch}-{current_flag}\"] A TELEGRAM ¡¡¡SÍ O SÍ!!! NOTIFICACIÓN => (\"{notification}\") ***")
                    logg.print_recovery_link(current_branch, current_link, elapsed_time)
                    logging.info(f"# Recuperación ... # | Notification => {notification} | Write_Timestamp => {empty_timestamp} | Link_Changed => True | Event => RECOVERY")
                    return notification, empty_timestamp, True, "RECOVERY"
                
                logging.error(f"¡¡¡ERROR EN EL TIMESTAMP!!! Se regresa Notification => {notification} | Write_Timestamp => {current_timestamp} | Link_Changed => False Event => PREVIOUS_TMESTAMP_ERROR")
                return notification, empty_timestamp, True, "PREVIOUS_TMESTAMP_ERROR"

            case ("As", "s"): # ⚠️ CAMBIO A FAILOVER: Sigue arriba pero se degradó
                print(f"↪️ CAMBIÓ DE \"As\" => \"s\"")
                logging.info(f"El enlace cambia de (\"As\" => \"s\") Failover ↪️")
                logging.warning(f"⚠️ [{current_branch}-{current_link}] CAMBIÓ A FAILOVER ↪️")
                logging.info(f"# Failover ... # | Notification => {notification} | Write_Timestamp => {empty_timestamp} | Link_Changed => True | Event => FAILOVER")
                return notification, empty_timestamp, True, "FAILOVER"

            case ("s", "As"): # 🚀 REGRESO A PRINCIPAL
                print(f"↪️ CAMBIÓ DE \"s\" => \"As\"")
                logging.info(f"El enlace cambia de (\"s\" => \"As\") ENLACE PRINCIPAL ... ↪️")
                logging.warning(f"⚠️ [{current_branch}-{current_link}] ES EL ENLACE PRINCIPAL AHORA ↪️")
                logging.info(f"# Enlace Principal ... # | Notification => {notification} | Write_Timestamp => {empty_timestamp} | Link_Changed => True | Event => PRIMARY_LINK")
                return notification, empty_timestamp, True, "PRIMARY_LINK"

            case _: # 🟢 SIN CAMBIOS (As -> As, o s -> s)
                print(f"🟢 SIN CAMBIOS")
                logging.info(f"🟢 \"{p_flag}\" \"{c_flag}\" # No hubo cambios #")
                logging.warning(f"⚠️ [{current_branch}-{current_link}] SIN CAMBIOS 🟢")
                logging.info(f" # No hubo cambios# | Notification => {notification} | Write_Timestamp => {empty_timestamp} | Link_Changed => False | Event => NO_CHANGE")
                return notification, empty_timestamp, False, "NO_CHANGE"
    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR VALIDANDO LOS CAMBIOS DE ESTADO ‼️ -> {error}\n", exc_info=True)
        return [], [], [], []
        
def handle_write_files(counter, counter_file, current_state, current_state_file, historical_file, date, hour, day, something_change, write_time, previous_lastrecord, register_change, current_timestamp):
    try:
        logging.info("=" * 210)
        if counter == 1 or something_change or write_time: #Sí alguna condición se cumple escribimos el Histórico
            if counter == 1:
                logging.info(f"✅ Es la primera ejecución ⚙️ después del reinicio")
            if write_time:
                logging.info(f"✅ Han transcurrido más 10 minutos ⌛ => ({int((int(current_timestamp) - int(previous_lastrecord)) / 60)})min/({int(current_timestamp) - int(previous_lastrecord)})s")
            if something_change:
                logging.info(f"✅ Hubo cambio en {register_change}")
            logging.info(f"💾 Se escribirán todos los archivos (Contador ⏱️ => \"{counter}\", Estado Actual 📝 => \"{current_state_file}\", y Arhivo Histórico 🗃️ => \"{historical_file}\")")
            f_u.write_all_files(counter, counter_file, current_state_file, current_state, current_timestamp, historical_file, date, hour, day)
        else:
            logging.info(f"🚫 No han pasado los 10 minutos o 600s para escribir Historical_File, el tiempo transcurrido es ⌛ ({int((int(current_timestamp) - int(previous_lastrecord)) / 60)})min/({int(current_timestamp) - int(previous_lastrecord)})s, se escribió Previous_lastrecord ({previous_lastrecord}) en lugar del Current_link_lastrecord ({current_timestamp})")
            f_u.write_always_files(counter, counter_file, current_state_file, current_state)
        
        logging.info("\n" + "=" * 102 + f"\n 💡 ÉSTE SCRIPT SE HA EJECUTADO **{counter}** VECES 🏁 EL DÍA DE HOY, PUEDES VER LOS DETALLES EN EL LOG 📋...\n" + "=" * 102)
    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR EN LA VALIDACIÓN DE ESCRITURA ‼️ -> {error}\n", exc_info=True)
        return []