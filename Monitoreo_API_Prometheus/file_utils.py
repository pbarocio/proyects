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

def get_previous_state(previous_state, current_branch, current_link, current_flag, current_link_timestamp, current_link_lastrecord):
    try:
        if (current_branch not in previous_state or 
            current_link not in previous_state[current_branch] or
            "BRANCHES-DOWN" in current_branch): #Sí no existen las llaves en el estado previo o es BRANCHES-DOWN retornamos los valores actuales
            return current_flag, current_link_timestamp, True, current_link_lastrecord
        
        link_state = previous_state[current_branch][current_link]
        
        previous_flag      = link_state.get("flag", current_flag)
        previous_link_timestamp = link_state.get("timestamp", current_link_timestamp)
        notification       = link_state.get("notification", True)
        previous_lastrecord         = link_state.get("lastrecord", current_link_lastrecord)
        
        return previous_flag, previous_link_timestamp, notification, previous_lastrecord
    except Exception as error:
        logging.error(f"¡¡¡ERROR EXTRAYENDO EL ESTADO PREVIO!!! {error}", exc_info=True)
        return current_flag, current_link_timestamp, True, current_link_lastrecord
    
def write_all_files(counter, counter_file, current_state_file, current_state, current_timestamp, historical_file, date, hour, day): #Función qué se ejecuta cuándo es la primera ejecución, algún enlace cambia o se cumple el tiempo de escritura
    for current_branch, links in current_state.items(): #Extraemos los datos qué se almacenarán en histórico
        if current_branch == "BRANCHES-DOWN":
            continue
        else:
            for link, values in links.items():
                current_link = link
                current_flag = values.get("flag")
                current_gateway = values.get("gateway")
                current_distance = values.get("distance")
                
                write_historical_file(historical_file, date, hour, day, current_branch, current_link, current_flag, current_gateway, current_distance) #Escribimos el archivo histórico de cada enlace
                values["lastrecord"] = current_timestamp #Actualizamos el timestamp de lastrecord por el actual en cada enlace por el timestamp actual   
    
    write_always_files(counter, counter_file, current_state_file, current_state) #Escribimos el Contador y el estado actual con lastrecord actualizado
        
def write_always_files(counter, counter_file, current_state_file, current_state):
    counter = counter + 1
    write_json_files(counter_file,counter)
    write_json_files(current_state_file,current_state)

def write_historical_file(historical_file, date, hour, day, current_branch, current_link, current_flag, current_gateway, current_distance): #Escribir registros en Archivo Histórico y encabezados sí no existen
    try:
        if not historical_file.exists(): #Validar sí Histórico existe, sí no existe escribir los encabezados
            with open(historical_file, "w") as file:
                line = ','.join(["Date","Hour","Day","Branch","Link","Flag","Gateway","Distance"]) + "\n"
                file.write(line)
    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR ESCRIBIENDO LOS ENCABEZADOS ‼️ -> {error}\n", exc_info=True)

    try:
        with open(historical_file, "a") as file_historical:
            line = ','.join([date,hour,day,current_branch,current_link,current_flag,current_gateway,current_distance]) + "\n"
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