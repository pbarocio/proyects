import logging
import datetime
import alert_manager as am

def print_out_site(branch_name,notification):
    try:
        if notification:
            logging.warning(f"ALERTA DE TELEGRAM!!! --- ⚠️ ALERTA ⚠️‼️ 🔴 {branch_name} ESTÁ FUERA‼️") #Enviamos alerta de Telegram con ése texto
            am.send_notification(f"⚠️ ALERTA ⚠️ \n‼️ 🔴 {branch_name} ESTÁ FUERA‼️") #Enviamos alerta de Telegram con ése texto
        return False
        
    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR AL MOSTRAR ALERTA DE SUCURSAL CAÍDA‼️ -> {error}\n",exc_info=True)   

def print_current_state(link,flag,gateway,distance): #Imprimir en consola los estados de las sucursales
    try:        
        link_show = "Enlace" #Salidas print en la consola para acomodarlas en el espacio en consola
        flag_show = "Estado"
        gateway_show = "Gateway"
        distance_show = "Distancia"
        print("-" * 24)
        print(f"{link_show:^10} | {link:^10} |") #^sirve para centrar el texto en en un número de campos en la consola y conservar un tamaño uniforme, < los alinea a la izquierda
        print("-" * 24)
        if flag == "As":
            emoji ="🟢"
            print(f"{flag_show:^10} | {emoji:^3}{flag:<7} |")
        elif flag == "s":
            emoji = "🟡"
            print(f"{flag_show:^10} | {emoji:^3}{flag:<6} |")
        else:
            emoji = "🔴"
            print(f"{flag_show:^10} | {emoji:^2}{flag:<7} |")
        print(f"{gateway_show:^10} | {gateway:^10} |")
        print(f"{distance_show:^10} | {distance:^10} |")
        print("-" * 24)
    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR AL MOSTRAR EL STATUS DE LOS ENLACES ‼️ -> {error}\n", exc_info=True)

def print_link_down_old(branch_name,link,elapsed_time,notification): #Funcion qué imprime el tiempo que lleva caído un enlace
    try:
        transcurrido = datetime.timedelta(seconds=elapsed_time)
        print(f"TIEMPO FUERA: {transcurrido} ⌛")
        logging.warning(f"[{branch_name}-{link}] TIEMPO FUERA: {transcurrido} ⌛")
        if elapsed_time >= 1320 and notification: #Calculamos la ventana de la alerta de 20 a 22 minutos #and elapsed_time <= 1400
            logging.warning(f"ALERTA DE TELEGRAM!!! --- ⚠️ ALERTA⚠️ ‼️🔴[{branch_name}-{link}]‼️ \nTIEMPO FUERA: ⌛ {transcurrido}")
            am.send_notification(f"⚠️ ALERTA⚠️ \n‼️🔴[{branch_name}-{link}]‼️ \nTIEMPO FUERA: ⌛ {transcurrido}") #Enviamos alerta de Telegram con ése texto
            return False
        return notification
    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR AL MOSTRAR LA CAÍDA PREVIA‼️ -> {error}\n", exc_info=True)

def print_back_online_link(branch_name,link,elapsed_time,notification):
    try:
        transcurrido = datetime.timedelta(seconds=elapsed_time)
        print(f"ENLACE DE NUEVO ACTIVO, ESTUVO FUERA POR ⌛ {transcurrido}\n")
        print(f"[{branch_name}-{link}] ENLACE DE NUEVO ACTIVO, ESTUVO FUERA POR ⌛ {transcurrido}\n")
        if notification:
            logging.warning(f"ALERTA DE TELEGRAM!!! --- 📢 ALERTA 📢❕ ✅ 🟢 [{branch_name}-{link}] 📶 🆙❕ESTUVO FUERA POR ⌛ {transcurrido}")
            am.send_notification(f"📢 ALERTA 📢 \n❕ ✅ 🟢 [{branch_name}-{link}] 📶 🆙❕\nESTUVO FUERA POR ⌛ {transcurrido}") #Enviamos alerta de Telegram con el texto
            return True
        return notification

    except Exception as error:
        logging.error(f"\n❌ ‼️ 🔴 ERROR AL MOSTRAR TIEMPO DE RECUPERACIÓN ‼️ -> {error}\n", exc_info=True)