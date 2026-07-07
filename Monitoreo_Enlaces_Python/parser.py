import logging
import file_utils as f_u

def parse_router_output(registers,current_timestamp,empty_timestamp):
    try:
        route_list = {} #Diccionario que contendrá los enlaces con su estado
        link = "Desconocido" #Inicializamos la variable link para evitar errores
        for register in registers: #Iteramos la tabla de ruteo por líneas
            if not register: #Sí la línea a leer está vacía la ignoramos
                continue

            if register.startswith(";;;"): #Aquí sacamos el nombre de el enlace, siempre inicia con las ;;;
                parts = register.split() #Dividimos en campos el nombre del enlace
                link = parts[1].strip('+') #Extraemos el campo que tiene el nombre de el enlace
            else:
                parts = register.split() #Las líneas que no vienen con ;;; son las que tienen los datos de los enlaces
                if len(parts) >= 4: #Aquí validamos que tenga los 4 campos necesarios
                    flag = str(parts[1].strip('+'))
                    gateway = str(parts[3])
                    distance = str(parts[-1])
                    link_timestamp = str(f_u.get_current_timestamp(flag,current_timestamp,empty_timestamp))
                    route_list[link] = {
                            "flag": flag,
                            "gateway": gateway,
                            "distance": distance,
                            "timestamp": link_timestamp,
                            "notification": None,
                            "lastrecord": current_timestamp,
                        }
        return route_list
    
    except Exception as error:
        logging.error(f"{error}\n\n❌ ‼️ 🔴 ERROR PARSEANDO LOS REGISTROS de {registers} ===> {error} ‼️", exc_info=True)
        return None