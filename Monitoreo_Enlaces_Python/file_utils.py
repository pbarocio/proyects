import json
import logging

def get_current_timestamp(flag,current_timestamp,empty_timestamp): #Función para saber el timestamp del Estado_Actual
    if "Is" in flag:
        return current_timestamp
    else:
        return empty_timestamp

def load_counter(counter_file):
    try:
        if counter_file.exists():
            with open(counter_file, "r") as file:
                counter = json.load(file)
            return counter
        else:
            with open(counter_file, "w", encoding="utf-8") as file:
                json.dump(int(1), file, indent=4, ensure_ascii=False)
            return 1
    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR CARGANDO EL ARCHIVO JSON ‼️ -> {error}\n", exc_info=True)
        
def load_json_file(file):
    try:
        with open(file, "r", encoding="utf-8") as load_file:
            recovery_data = json.load(load_file)
        return recovery_data
    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR CARGANDO EL ARCHIVO JSON ‼️ -> {error}\n", exc_info=True)
        
def load_previous_state(previous_state_file):
    try:
        if previous_state_file.exists():
            return load_json_file(previous_state_file)
        else:
            return []
    except Exception as error:
        logging.error(f"¡¡¡ERROR CARGANDO EL ESTADO PREVIO!!! {error}", exc_info=True)

def get_previous_state(previous_state,current_branch,current_link,current_flag,current_link_timestamp):
    try:
        if current_branch in previous_state and current_link in previous_state[current_branch] and not "BRANCHES-DOWN" in current_branch: #Validamos sí hay un registro de estado anterior de ése enlace
            previous_flag = previous_state[current_branch][current_link]["flag"]
            previous_timestamp = previous_state[current_branch][current_link]["timestamp"]
            notification = previous_state[current_branch][current_link]["notification"]
            if previous_flag is None:
                logging.critical(f"PREVIOUS_FLAG ERROR!!! ===> \"{previous_flag}\"")
                previous_flag = current_flag
            if previous_timestamp is None:
                logging.critical(f"PREVIOUS_TIMESTAMP ERROR!!! ===> \"{previous_timestamp}\"")
                previous_timestamp = current_link_timestamp
            if notification is None:
                logging.critical(f"NOTIFICATION ERROR!!! ===> \"{notification}\"")
                notification = True
            return previous_flag,previous_timestamp,notification #Regresamos los datos del estado anterior
        else: #Cómo no hay estado anterior dejamos los valores actuales y la notificación cómo vacía
            return current_flag, current_link_timestamp, True
    except Exception as error:
        logging.error(f"¡¡¡ERROR EXTRAYENDO EL ESTADO PREVIO!!! {error}", exc_info=True)

def write_historical_file(historical_file,date,hour,day,current_branch,current_link,current_flag,current_gateway,current_distance,counter): #Escribir registros en Archivo Histórico y encabezados sí no existen
    try:
        if not historical_file.exists(): #Validar sí Histórico existe, sí no existe escribir los encabezados
            with open(historical_file, "w") as file:
                line = ','.join(["Date","Hour","Day","Branch","Link","Flag","Gateway","Distance","Try"]) + "\n"
                file.write(line)
    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR ESCRIBIENDO LOS ENCABEZADOS ‼️ -> {error}\n", exc_info=True)

    try:
        with open(historical_file, "a") as file_historical:
            line = ','.join([date,hour,day,current_branch,current_link,current_flag,current_gateway,current_distance,counter]) + "\n"
            file_historical.write(line)
    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR ESCRIBIENDO EL ARCHIVO HISTÓRICO ‼️ -> {error}\n", exc_info=True)

def write_json_files(file,data):
    try:
        with open(file, "w", encoding="utf-8") as file_write:
           json.dump(data, file_write, indent=4, ensure_ascii=False)
    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR ESCRIBIENDO EL ARCHIVO JSON‼️ -> {error}\n", exc_info=True)

def get_elapsed_time(previous_timestamp,current_timestamp):
    try:
        elapsed_time = 0 #Inicializamos elapsed time por sí no hay un timestamp en estado previo
        if not "-" in previous_timestamp : #Validamos que Si hay un timestamp previo para calcular tiempo de recuperación
            elapsed_time = (int(current_timestamp) - int(previous_timestamp))
            return elapsed_time
        else:
            return 0
    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR EXTRAYENDO EL TIEMPO TRANSCURRIDO‼️ -> {error}\n", exc_info=True)