import io
import streamlit as st
import pandas as pd
from database import obtener_conexion

def aplicar_estilos_pantalla():
    st.markdown("""
        <style>
            .appview-container .main .block-container {
                max-width: 100% !important;
                padding-left: 2rem !important;
                padding-right: 2rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

def obtener_catalogo_dict(tabla, col_id, col_nombre):
    try:
        conn = obtener_conexion()
        query = f"SELECT {col_id}, {col_nombre} FROM {tabla} ORDER BY {col_nombre} ASC"
        df = pd.read_sql(query, conn)
        conn.close()
        return dict(zip(df[col_nombre], df[col_id]))
    except Exception as e:
        st.error(f"⚠️ Error al cargar catálogo {tabla}: {e}")
        return {}

def notificar_exito(mensaje):
    st.session_state["mensaje_exito"] = mensaje
    st.rerun()

def generar_excel_bytes(df_exportar, nombre_hoja="Inventario"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_exportar.to_excel(writer, index=False, sheet_name=nombre_hoja)
    buffer.seek(0)
    return buffer

# ==============================================================================
# 1. CELULARES
# ==============================================================================
def obtener_celulares_df():
    try:
        conn = obtener_conexion()
        query = """
            SELECT 
                ic.imei, ic.numero AS numero_linea, m.marca_modelo, e_cel.estatus_celular AS estatus,
                ic.id_estatus_celular, COALESCE(CONCAT(emp.nombre, ' ', emp.apellido_paterno), 'VACANTE / SIN ASIGNAR') AS asignado_a,
                suc.nombre_sucursal AS sucursal, c.condicion_opcion AS condicion, cg.cargador_opcion AS cargador,
                cj.caja_opcion AS caja, ic.numero_serie, ic.mac_address, ic.observaciones, ic.comentarios,
                ic.id_modelo, ic.id_condicion, ic.id_cargador, ic.id_caja
            FROM inventario_celulares ic
            LEFT JOIN modelos_celulares m ON ic.id_modelo = m.id_modelo
            LEFT JOIN estatus_celulares e_cel ON ic.id_estatus_celular = e_cel.id_estatus_celular
            LEFT JOIN empleados emp ON TRIM(LEADING '0' FROM CAST(ic.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(emp.codigo AS CHAR))
            LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
            LEFT JOIN condicion c ON ic.id_condicion = c.id_condicion
            LEFT JOIN cargadores cg ON ic.id_cargador = cg.id_cargador
            LEFT JOIN caja cj ON ic.id_caja = cj.id_caja
            ORDER BY ic.imei DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error Celulares: {e}")
        return pd.DataFrame()

def guardar_celular(imei, serie, mac, numero, id_modelo, id_condicion, id_cargador, id_caja, observaciones, comentarios="", id_estatus=4):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            INSERT INTO inventario_celulares 
            (imei, numero_serie, mac_address, numero, id_modelo, id_condicion, id_cargador, id_caja, observaciones, comentarios, id_estatus_celular) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (imei.strip(), serie.strip(), mac.strip(), numero.strip() or None, id_modelo, id_condicion, id_cargador, id_caja, observaciones.strip(), comentarios.strip(), id_estatus))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar celular: {e}")
        return False

def actualizar_celular(imei, serie, mac, numero, id_modelo, id_condicion, id_cargador, id_caja, id_estatus, observaciones, comentarios=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            UPDATE inventario_celulares 
            SET numero_serie = %s, mac_address = %s, numero = %s, id_modelo = %s, id_condicion = %s, 
                id_cargador = %s, id_caja = %s, id_estatus_celular = %s, observaciones = %s, comentarios = %s 
            WHERE imei = %s
        """
        cursor.execute(query, (serie.strip(), mac.strip(), numero.strip() or None, id_modelo, id_condicion, id_cargador, id_caja, id_estatus, observaciones.strip(), comentarios.strip(), imei))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al actualizar celular: {e}")
        return False

# ==============================================================================
# 2. LAPTOPS
# ==============================================================================
def obtener_laptops_df():
    try:
        conn = obtener_conexion()
        query = """
            SELECT 
                il.numero_serie, il.hostname, il.marca, il.modelo, il.procesador, il.memoria_ram, il.datos_memoria_ram,
                il.motherboard, ht.hdd_opcion AS tipo_almacenamiento, il.almacenamiento, il.datos_almacenamiento, il.sistema_operativo,
                il.mac_address_lan, il.mac_address_wlan, il.precio,
                el.estatus_laptop AS estatus, il.id_estatus_laptops,
                COALESCE(CONCAT(emp.nombre, ' ', emp.apellido_paterno), 'VACANTE / SIN ASIGNAR') AS asignado_a,
                suc.nombre_sucursal AS sucursal, c.condicion_opcion AS condicion, cg.cargador_opcion AS cargador,
                il.observaciones, il.comentarios, il.id_hdd_tipo, il.id_condicion, il.id_cargador, il.id_renovacion
            FROM inventario_laptops il
            LEFT JOIN estatus_laptops el ON il.id_estatus_laptops = el.id_estatus_laptops
            LEFT JOIN hdd_tipo ht ON il.id_hdd_tipo = ht.id_hdd_tipo
            LEFT JOIN empleados emp ON TRIM(LEADING '0' FROM CAST(il.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(emp.codigo AS CHAR))
            LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
            LEFT JOIN condicion c ON il.id_condicion = c.id_condicion
            LEFT JOIN cargadores cg ON il.id_cargador = cg.id_cargador
            ORDER BY il.numero_serie DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error Laptops: {e}")
        return pd.DataFrame()

def guardar_laptop(serie, hostname, marca, modelo, proc, ram, datos_ram, mobo, id_hdd_tipo, almac, datos_almac, so, mac_lan, mac_wlan, precio, id_condicion, id_cargador, id_renovacion, obs, com="", id_estatus=4):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            INSERT INTO inventario_laptops 
            (numero_serie, hostname, marca, modelo, procesador, memoria_ram, datos_memoria_ram, motherboard, id_hdd_tipo, almacenamiento, datos_almacenamiento, sistema_operativo, mac_address_lan, mac_address_wlan, precio, id_condicion, id_cargador, id_renovacion, observaciones, comentarios, id_estatus_laptops) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (serie.strip(), hostname.strip(), marca.strip(), modelo.strip(), proc.strip(), ram.strip(), datos_ram.strip() or None, mobo.strip() or None, id_hdd_tipo, almac.strip(), datos_almac.strip() or None, so.strip(), mac_lan.strip() or None, mac_wlan.strip() or None, precio, id_condicion, id_cargador, id_renovacion, obs.strip() or None, com.strip() or None, id_estatus))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar laptop: {e}")
        return False

def actualizar_laptop(serie, hostname, marca, modelo, proc, ram, datos_ram, mobo, id_hdd_tipo, almac, datos_almac, so, mac_lan, mac_wlan, precio, id_condicion, id_cargador, id_renovacion, id_estatus, obs, com=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            UPDATE inventario_laptops 
            SET hostname=%s, marca=%s, modelo=%s, procesador=%s, memoria_ram=%s, datos_memoria_ram=%s, motherboard=%s, 
                id_hdd_tipo=%s, almacenamiento=%s, datos_almacenamiento=%s, sistema_operativo=%s, mac_address_lan=%s, mac_address_wlan=%s, 
                precio=%s, id_condicion=%s, id_cargador=%s, id_renovacion=%s, id_estatus_laptops=%s, observaciones=%s, comentarios=%s 
            WHERE numero_serie=%s
        """
        cursor.execute(query, (hostname.strip(), marca.strip(), modelo.strip(), proc.strip(), ram.strip(), datos_ram.strip() or None, mobo.strip() or None, id_hdd_tipo, almac.strip(), datos_almac.strip() or None, so.strip(), mac_lan.strip() or None, mac_wlan.strip() or None, precio, id_condicion, id_cargador, id_renovacion, id_estatus, obs.strip() or None, com.strip() or None, serie))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al actualizar laptop: {e}")
        return False

# ==============================================================================
# 3. CPUS
# ==============================================================================
def obtener_cpus_df():
    try:
        conn = obtener_conexion()
        query = """
            SELECT 
                ic.hostname, ic.numero_serie, ic.marca, ic.modelo, ic.procesador, ic.memoria_ram, ic.datos_memoria_ram,
                ht.hdd_opcion AS tipo_almacenamiento, ic.almacenamiento, ic.datos_almacenamiento, ic.sistema_operativo,
                ec.estatus_cpu AS estatus, ic.id_estatus_cpu,
                COALESCE(CONCAT(emp.nombre, ' ', emp.apellido_paterno), 'VACANTE / SIN ASIGNAR') AS asignado_a,
                suc.nombre_sucursal AS sucursal, c.condicion_opcion AS condicion, ic.observaciones, ic.comentarios,
                ic.mac_address_lan, ic.mac_address_wlan, ic.id_hdd_tipo, ic.id_condicion
            FROM inventario_cpu ic
            LEFT JOIN estatus_cpu ec ON ic.id_estatus_cpu = ec.id_estatus_cpu
            LEFT JOIN hdd_tipo ht ON ic.id_hdd_tipo = ht.id_hdd_tipo
            LEFT JOIN empleados emp ON TRIM(LEADING '0' FROM CAST(ic.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(emp.codigo AS CHAR))
            LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
            LEFT JOIN condicion c ON ic.id_condicion = c.id_condicion
            ORDER BY ic.hostname DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error CPUs: {e}")
        return pd.DataFrame()

def guardar_cpu(hostname, serie, marca, modelo, proc, ram, datos_ram, id_hdd_tipo, almac, datos_almac, so, mac_lan, mac_wlan, id_condicion, obs, com="", id_estatus=4):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            INSERT INTO inventario_cpu 
            (hostname, numero_serie, marca, modelo, procesador, memoria_ram, datos_memoria_ram, id_hdd_tipo, almacenamiento, datos_almacenamiento, sistema_operativo, mac_address_lan, mac_address_wlan, id_condicion, observaciones, comentarios, id_estatus_cpu) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (hostname.strip(), serie.strip(), marca.strip(), modelo.strip(), proc.strip(), ram.strip(), datos_ram.strip() or None, id_hdd_tipo, almac.strip(), datos_almac.strip() or None, so.strip(), mac_lan.strip(), mac_wlan.strip(), id_condicion, obs.strip(), com.strip(), id_estatus))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar CPU: {e}")
        return False

def actualizar_cpu(hostname, serie, marca, modelo, proc, ram, datos_ram, id_hdd_tipo, almac, datos_almac, so, mac_lan, mac_wlan, id_condicion, id_estatus, obs, com=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            UPDATE inventario_cpu 
            SET numero_serie=%s, marca=%s, modelo=%s, procesador=%s, memoria_ram=%s, datos_memoria_ram=%s, id_hdd_tipo=%s, 
                almacenamiento=%s, datos_almacenamiento=%s, sistema_operativo=%s, mac_address_lan=%s, mac_address_wlan=%s, 
                id_condicion=%s, id_estatus_cpu=%s, observaciones=%s, comentarios=%s 
            WHERE hostname=%s
        """
        cursor.execute(query, (serie.strip(), marca.strip(), modelo.strip(), proc.strip(), ram.strip(), datos_ram.strip() or None, id_hdd_tipo, almac.strip(), datos_almac.strip() or None, so.strip(), mac_lan.strip(), mac_wlan.strip(), id_condicion, id_estatus, obs.strip(), com.strip(), hostname))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al actualizar CPU: {e}")
        return False

# ==============================================================================
# 4. MONITORES
# ==============================================================================
def obtener_monitores_df():
    try:
        conn = obtener_conexion()
        query = """
            SELECT 
                im.numero_serie, im.hostname, im.marca, im.modelo, im.resolucion,
                em.estatus_monitor AS estatus, im.id_estatus_monitor,
                COALESCE(CONCAT(emp.nombre, ' ', emp.apellido_paterno), 'VACANTE / SIN ASIGNAR') AS asignado_a,
                suc.nombre_sucursal AS sucursal, c.condicion_opcion AS condicion, im.observaciones, im.comentarios, im.id_condicion
            FROM inventario_monitores im
            LEFT JOIN estatus_monitores em ON im.id_estatus_monitor = em.id_estatus_monitor
            LEFT JOIN empleados emp ON TRIM(LEADING '0' FROM CAST(im.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(emp.codigo AS CHAR))
            LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
            LEFT JOIN condicion c ON im.id_condicion = c.id_condicion
            ORDER BY im.numero_serie DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error Monitores: {e}")
        return pd.DataFrame()

def guardar_monitor(serie, hostname, marca, modelo, resolucion, id_condicion, obs, com="", id_estatus=4):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            INSERT INTO inventario_monitores 
            (numero_serie, hostname, marca, modelo, resolucion, id_condicion, observaciones, comentarios, id_estatus_monitor) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (serie.strip(), hostname.strip(), marca.strip(), modelo.strip(), resolucion.strip(), id_condicion, obs.strip(), com.strip(), id_estatus))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar monitor: {e}")
        return False

def actualizar_monitor(serie, hostname, marca, modelo, resolucion, id_condicion, id_estatus, obs, com=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            UPDATE inventario_monitores 
            SET hostname=%s, marca=%s, modelo=%s, resolucion=%s, id_condicion=%s, id_estatus_monitor=%s, observaciones=%s, comentarios=%s 
            WHERE numero_serie=%s
        """
        cursor.execute(query, (hostname.strip(), marca.strip(), modelo.strip(), resolucion.strip(), id_condicion, id_estatus, obs.strip(), com.strip(), serie))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al actualizar monitor: {e}")
        return False

# ==============================================================================
# 5. TABLETS
# ==============================================================================
def obtener_tablets_df():
    try:
        conn = obtener_conexion()
        query = """
            SELECT 
                it.numero_serie, it.imei, it.marca, it.modelo, it.mac_address,
                et.estatus_tablet AS estatus, it.id_estatus_tablet,
                COALESCE(CONCAT(emp.nombre, ' ', emp.apellido_paterno), 'VACANTE / SIN ASIGNAR') AS asignado_a,
                suc.nombre_sucursal AS sucursal, c.condicion_opcion AS condicion, cg.cargador_opcion AS cargador,
                it.observaciones, it.comentarios, it.id_condicion, it.id_cargador
            FROM inventario_tablets it
            LEFT JOIN estatus_tablets et ON it.id_estatus_tablet = et.id_estatus_tablet
            LEFT JOIN empleados emp ON TRIM(LEADING '0' FROM CAST(it.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(emp.codigo AS CHAR))
            LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
            LEFT JOIN condicion c ON it.id_condicion = c.id_condicion
            LEFT JOIN cargadores cg ON it.id_cargador = cg.id_cargador
            ORDER BY it.numero_serie DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error Tablets: {e}")
        return pd.DataFrame()

def guardar_tablet(serie, imei, marca, modelo, mac, id_condicion, id_cargador, obs, com="", id_estatus=4):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            INSERT INTO inventario_tablets 
            (numero_serie, imei, marca, modelo, mac_address, id_condicion, id_cargador, observaciones, comentarios, id_estatus_tablet) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (serie.strip(), imei.strip(), marca.strip(), modelo.strip(), mac.strip(), id_condicion, id_cargador, obs.strip(), com.strip(), id_estatus))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar tablet: {e}")
        return False

def actualizar_tablet(serie, imei, marca, modelo, mac, id_condicion, id_cargador, id_estatus, obs, com=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            UPDATE inventario_tablets 
            SET imei=%s, marca=%s, modelo=%s, mac_address=%s, id_condicion=%s, id_cargador=%s, id_estatus_tablet=%s, observaciones=%s, comentarios=%s 
            WHERE numero_serie=%s
        """
        cursor.execute(query, (imei.strip(), marca.strip(), modelo.strip(), mac.strip(), id_condicion, id_cargador, id_estatus, obs.strip(), com.strip(), serie))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al actualizar tablet: {e}")
        return False

# ==============================================================================
# 6. DISPOSITIVOS DE RED
# ==============================================================================
def obtener_dispositivos_red_df():
    try:
        conn = obtener_conexion()
        query = """
            SELECT 
                dr.id_dispositivo, s.nombre_sucursal AS sucursal, dr.id_sucursal, dr.tipo, dr.marca, dr.modelo,
                dr.numero_serie, dr.mac_address_lan, dr.mac_address_wlan, dr.ubicacion_fisica,
                da.hostname, da.usuario_admin_default, da.password_admin_default, da.nuevo_usuario, da.password_nuevo, da.puerto_admin,
                dw.ssid, dw.modo_wpa, dw.password_wpa
            FROM dispositivos_red dr
            LEFT JOIN sucursales s ON dr.id_sucursal = s.id_sucursal
            LEFT JOIN dispositivos_accesos da ON dr.id_dispositivo = da.id_dispositivo
            LEFT JOIN dispositivos_wifi dw ON dr.id_dispositivo = dw.id_dispositivo
            ORDER BY dr.id_dispositivo ASC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error Dispositivos de Red: {e}")
        return pd.DataFrame()

def guardar_dispositivo_red(id_sucursal, tipo, marca, modelo, serie, mac_lan, mac_wlan, ubicacion, hostname="", user_def="", pass_def="", user_nuevo="", pass_nuevo="", puerto=80, ssid="", modo_wpa="WPA2-PSK", pass_wpa=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        q_red = "INSERT INTO dispositivos_red (id_sucursal, tipo, marca, modelo, numero_serie, mac_address_lan, mac_address_wlan, ubicacion_fisica) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(q_red, (id_sucursal, tipo.strip(), marca.strip(), modelo.strip(), serie.strip(), mac_lan.strip(), mac_wlan.strip() or None, ubicacion.strip()))
        id_disp = cursor.lastrowid

        if hostname.strip() or user_def.strip() or user_nuevo.strip():
            q_acc = "INSERT INTO dispositivos_accesos (id_dispositivo, hostname, usuario_admin_default, password_admin_default, nuevo_usuario, password_nuevo, puerto_admin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(q_acc, (id_disp, hostname.strip(), user_def.strip() or None, pass_def.strip() or None, user_nuevo.strip() or None, pass_nuevo.strip() or None, puerto))

        if ssid.strip():
            q_wifi = "INSERT INTO dispositivos_wifi (id_dispositivo, ssid, modo_wpa, password_wpa) VALUES (%s, %s, %s, %s)"
            cursor.execute(q_wifi, (id_disp, ssid.strip(), modo_wpa.strip(), pass_wpa.strip()))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar dispositivo de red: {e}")
        return False

def actualizar_dispositivo_red(id_dispositivo, id_sucursal, tipo, marca, modelo, serie, mac_lan, mac_wlan, ubicacion, hostname="", user_def="", pass_def="", user_nuevo="", pass_nuevo="", puerto=80, ssid="", modo_wpa="WPA2-PSK", pass_wpa=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        q_red = "UPDATE dispositivos_red SET id_sucursal = %s, tipo = %s, marca = %s, modelo = %s, numero_serie = %s, mac_address_lan = %s, mac_address_wlan = %s, ubicacion_fisica = %s WHERE id_dispositivo = %s"
        cursor.execute(q_red, (id_sucursal, tipo.strip(), marca.strip(), modelo.strip(), serie.strip(), mac_lan.strip(), mac_wlan.strip() or None, ubicacion.strip(), id_dispositivo))

        if hostname.strip() or user_def.strip() or user_nuevo.strip():
            q_acc = "INSERT INTO dispositivos_accesos (id_dispositivo, hostname, usuario_admin_default, password_admin_default, nuevo_usuario, password_nuevo, puerto_admin) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE hostname=VALUES(hostname), usuario_admin_default=VALUES(usuario_admin_default), password_admin_default=VALUES(password_admin_default), nuevo_usuario=VALUES(nuevo_usuario), password_nuevo=VALUES(password_nuevo), puerto_admin=VALUES(puerto_admin);"
            cursor.execute(q_acc, (id_dispositivo, hostname.strip(), user_def.strip() or None, pass_def.strip() or None, user_nuevo.strip() or None, pass_nuevo.strip() or None, puerto))

        if ssid.strip():
            q_wifi = "INSERT INTO dispositivos_wifi (id_dispositivo, ssid, modo_wpa, password_wpa) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE ssid=VALUES(ssid), modo_wpa=VALUES(modo_wpa), password_wpa=VALUES(password_wpa);"
            cursor.execute(q_wifi, (id_dispositivo, ssid.strip(), modo_wpa.strip(), pass_wpa.strip()))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al actualizar dispositivo de red: {e}")
        return False

# ==============================================================================
# RENDER PRINCIPAL
# ==============================================================================
def render():
    aplicar_estilos_pantalla()
    st.title("💻📱 Gestión de Inventario Unificado")

    if "mensaje_exito" in st.session_state:
        st.success(f"✅ {st.session_state['mensaje_exito']}")
        del st.session_state["mensaje_exito"]

    dict_condiciones = obtener_catalogo_dict("condicion", "id_condicion", "condicion_opcion")
    dict_cargadores = obtener_catalogo_dict("cargadores", "id_cargador", "cargador_opcion")
    dict_cajas = obtener_catalogo_dict("caja", "id_caja", "caja_opcion")
    dict_hdd_tipos = obtener_catalogo_dict("hdd_tipo", "id_hdd_tipo", "hdd_opcion")

    tab_cel, tab_lap, tab_cpu, tab_mon, tab_tab, tab_red = st.tabs([
        "📱 Celulares", "💻 Laptops", "🖥️ CPUs", "🖥️ Monitores", "📱 Tablets", "🌐 Dispositivos de Red"
    ])

    # --------------------------------------------------------------------------
    # 1. CELULARES
    # --------------------------------------------------------------------------
    with tab_cel:
        df_cel = obtener_celulares_df()
        dict_mod = obtener_catalogo_dict("modelos_celulares", "id_modelo", "marca_modelo")
        dict_est = obtener_catalogo_dict("estatus_celulares", "id_estatus_celular", "estatus_celular")
        
        t1, t2, t3 = st.tabs(["📋 Consulta General", "➕ Registrar Nuevo", "✏️ Editar / Modificar"])
        with t1:
            if not df_cel.empty:
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    txt_cel = st.text_input("🔍 Buscar en Celulares:", placeholder="Ej. Iphone, 35077..., Juan, La Barca", key="txt_f_cel")
                with c_f2:
                    opts_est_cel = ["Todos"] + list(dict_est.keys())
                    est_sel_cel = st.selectbox("Filtrar por Estatus:", opts_est_cel, key="est_f_cel")

                df_filt_cel = df_cel.copy()
                if est_sel_cel != "Todos":
                    df_filt_cel = df_filt_cel[df_filt_cel["estatus"] == est_sel_cel]

                if txt_cel.strip():
                    term = txt_cel.strip().lower()
                    df_filt_cel = df_filt_cel[
                        df_filt_cel["imei"].astype(str).str.lower().str.contains(term) |
                        df_filt_cel["numero_linea"].astype(str).str.lower().str.contains(term) |
                        df_filt_cel["marca_modelo"].astype(str).str.lower().str.contains(term) |
                        df_filt_cel["asignado_a"].astype(str).str.lower().str.contains(term) |
                        df_filt_cel["sucursal"].astype(str).str.lower().str.contains(term)
                    ]

                df_view = df_filt_cel[["imei", "numero_linea", "marca_modelo", "estatus", "asignado_a", "sucursal", "observaciones", "comentarios"]]
                st.dataframe(df_view, use_container_width=True, hide_index=True)
                
                c_inf, c_btn = st.columns([3, 1])
                with c_inf:
                    st.caption(f"Mostrando **{len(df_filt_cel)}** de **{len(df_cel)}** Celulares")
                with c_btn:
                    st.download_button(
                        label="📊 Exportar Celulares (.xlsx)",
                        data=generar_excel_bytes(df_view, "Celulares"),
                        file_name="Inventario_Celulares_AGROCISA.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True
                    )
        with t2:
            with st.form("form_add_cel"):
                c1, c2 = st.columns(2)
                imei = c1.text_input("IMEI*:")
                serie = c1.text_input("Número de Serie*:")
                mac = c1.text_input("MAC Wi-Fi:")
                numero = c1.text_input("Línea Asignada:")
                mod_sel = c2.selectbox("Modelo:", list(dict_mod.keys()))
                cond_sel = c2.selectbox("Condición:", list(dict_condiciones.keys()))
                carg_sel = c2.selectbox("Cargador:", list(dict_cargadores.keys()))
                caj_sel = c2.selectbox("Caja:", list(dict_cajas.keys()))
                obs = st.text_area("Observaciones (Diagnóstico/Baja):")
                com = st.text_area("Comentarios (Estatus físico - va al Word):")
                if st.form_submit_button("💾 Guardar Celular", type="primary"):
                    if imei and serie and guardar_celular(imei, serie, mac, numero, dict_mod[mod_sel], dict_condiciones[cond_sel], dict_cargadores[carg_sel], dict_cajas[caj_sel], obs, com):
                        notificar_exito(f"¡Celular IMEI {imei} dado de alta con éxito!")
        with t3:
            if not df_cel.empty:
                st.markdown("### 🔍 Filtrar Celular a Modificar")
                f1, f2 = st.columns(2)
                with f1:
                    busq_ed_cel = st.text_input("Buscar por IMEI, Modelo o Asignado:", placeholder="Ej. 35077..., Iphone, Juan", key="busq_ed_cel")
                with f2:
                    opts_ed_est_cel = ["Todos"] + list(dict_est.keys())
                    est_ed_sel_cel = st.selectbox("Filtrar por Estatus:", opts_ed_est_cel, key="est_ed_cel")

                df_ed_cel = df_cel.copy()
                if est_ed_sel_cel != "Todos":
                    df_ed_cel = df_ed_cel[df_ed_cel["estatus"] == est_ed_sel_cel]

                if busq_ed_cel.strip():
                    term_ed = busq_ed_cel.strip().lower()
                    df_ed_cel = df_ed_cel[
                        df_ed_cel["imei"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_cel["marca_modelo"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_cel["asignado_a"].astype(str).str.lower().str.contains(term_ed)
                    ]

                if df_ed_cel.empty:
                    st.warning("No se encontraron celulares con los filtros seleccionados.")
                else:
                    cel_sel = st.selectbox("Selecciona Celular:", [f"{r['imei']} - {r['marca_modelo']} ({r['estatus']}) -> {r['asignado_a']}" for _, r in df_ed_cel.iterrows()], key="sel_ed_cel")
                    imei_ed = cel_sel.split(" - ")[0]
                    r = df_ed_cel[df_ed_cel["imei"] == imei_ed].iloc[0]
                    
                    st.divider()
                    with st.form(f"form_ed_cel_{imei_ed}"):
                        c1, c2 = st.columns(2)
                        e_ser = c1.text_input("Número de Serie:", value=str(r["numero_serie"] or ""))
                        e_mac = c1.text_input("MAC Wi-Fi:", value=str(r["mac_address"] or ""))
                        e_num = c1.text_input("Línea:", value=str(r["numero_linea"] or ""))
                        e_est = c1.selectbox("Estatus:", list(dict_est.keys()), index=list(dict_est.keys()).index(r["estatus"]) if r["estatus"] in dict_est else 0)
                        e_mod = c2.selectbox("Modelo:", list(dict_mod.keys()), index=list(dict_mod.values()).index(r["id_modelo"]) if r["id_modelo"] in dict_mod.values() else 0)
                        e_cond = c2.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                        e_carg = c2.selectbox("Cargador:", list(dict_cargadores.keys()), index=list(dict_cargadores.values()).index(r["id_cargador"]) if r["id_cargador"] in dict_cargadores.values() else 0)
                        e_caj = c2.selectbox("Caja:", list(dict_cajas.keys()), index=list(dict_cajas.values()).index(r["id_caja"]) if r["id_caja"] in dict_cajas.values() else 0)
                        
                        e_obs = st.text_area("Observaciones (Diagnóstico/Baja):", value=str(r["observaciones"] or ""))
                        e_com = st.text_area("Comentarios (Estatus físico - va al Word):", value=str(r["comentarios"] or ""))
                        if st.form_submit_button("💾 Actualizar Celular", type="primary"):
                            if actualizar_celular(imei_ed, e_ser, e_mac, e_num, dict_mod[e_mod], dict_condiciones[e_cond], dict_cargadores[e_carg], dict_cajas[e_caj], dict_est[e_est], e_obs, e_com):
                                notificar_exito(f"¡Celular IMEI {imei_ed} actualizado correctamente!!")

    # --------------------------------------------------------------------------
    # 2. LAPTOPS
    # --------------------------------------------------------------------------
    with tab_lap:
        df_lap = obtener_laptops_df()
        dict_est_lap = obtener_catalogo_dict("estatus_laptops", "id_estatus_laptops", "estatus_laptop")
        t1, t2, t3 = st.tabs(["📋 Consulta General", "➕ Registrar Nuevo", "✏️ Editar / Modificar"])
        with t1:
            if not df_lap.empty:
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    txt_lap = st.text_input("🔍 Buscar en Laptops:", placeholder="Ej. Dell, Lenovo, Host, Juan, La Barca", key="txt_f_lap")
                with c_f2:
                    opts_est_lap = ["Todos"] + list(dict_est_lap.keys())
                    est_sel_lap = st.selectbox("Filtrar por Estatus:", opts_est_lap, key="est_f_lap")

                df_filt_lap = df_lap.copy()
                if est_sel_lap != "Todos":
                    df_filt_lap = df_filt_lap[df_filt_lap["estatus"] == est_sel_lap]

                if txt_lap.strip():
                    term = txt_lap.strip().lower()
                    df_filt_lap = df_filt_lap[
                        df_filt_lap["numero_serie"].astype(str).str.lower().str.contains(term) |
                        df_filt_lap["hostname"].astype(str).str.lower().str.contains(term) |
                        df_filt_lap["marca"].astype(str).str.lower().str.contains(term) |
                        df_filt_lap["modelo"].astype(str).str.lower().str.contains(term) |
                        df_filt_lap["asignado_a"].astype(str).str.lower().str.contains(term) |
                        df_filt_lap["sucursal"].astype(str).str.lower().str.contains(term)
                    ]

                df_view = df_filt_lap[["numero_serie", "hostname", "marca", "modelo", "procesador", "memoria_ram", "datos_memoria_ram", "motherboard", "tipo_almacenamiento", "almacenamiento", "datos_almacenamiento", "sistema_operativo", "mac_address_lan", "mac_address_wlan", "precio", "estatus", "asignado_a", "sucursal", "observaciones", "comentarios"]]
                st.dataframe(df_view, use_container_width=True, hide_index=True)
                
                c_inf, c_btn = st.columns([3, 1])
                with c_inf:
                    st.caption(f"Mostrando **{len(df_filt_lap)}** de **{len(df_lap)}** Laptops")
                with c_btn:
                    st.download_button(
                        label="📊 Exportar Laptops (.xlsx)",
                        data=generar_excel_bytes(df_view, "Laptops"),
                        file_name="Inventario_Laptops_AGROCISA.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True
                    )
        with t2:
            with st.form("form_add_lap"):
                c1, c2 = st.columns(2)
                serie = c1.text_input("Número de Serie*:")
                host = c1.text_input("Hostname*:")
                marca = c1.text_input("Marca*:")
                modelo = c1.text_input("Modelo*:")
                proc = c1.text_input("Procesador*:")
                ram = c1.text_input("RAM Resumen (ej. 16 GB)*:")
                datos_ram = c1.text_input("RAM Detalle Speccy (ej. 16.0GB Dual-Channel DDR4 @ 1330MHz):")
                mobo = c1.text_input("Motherboard (ej. Dell Inc. 04YVDP):")
                
                hdd_sel = c2.selectbox("Tipo Disco:", list(dict_hdd_tipos.keys()))
                almac = c2.text_input("Almacenamiento Resumen (ej. 512 GB)*:")
                datos_almac = c2.text_input("Almacenamiento Speccy (ej. 476GB KINGSTON OM8PCP4512Q-A0):")
                so = c2.text_input("Sistema Operativo*:", value="Windows 11 Pro 64-bit")
                mac_lan = c2.text_input("MAC LAN:")
                mac_wlan = c2.text_input("MAC Wi-Fi:")
                precio = c2.number_input("Precio Estimado ($):", min_value=0.0, value=0.0, step=500.0)
                
                c3, c4 = st.columns(2)
                cond_sel = c3.selectbox("Condición:", list(dict_condiciones.keys()))
                carg_sel = c3.selectbox("Cargador Incluido:", list(dict_cargadores.keys()))
                renov_sel = c4.number_input("Renovación ID (Opcional):", min_value=0, value=0)
                
                obs = st.text_area("Observaciones (Diagnósticos/Bajas):")
                com = st.text_area("Comentarios (Estatus físico - va al Word):")
                if st.form_submit_button("💾 Guardar Laptop", type="primary"):
                    if serie and host and guardar_laptop(serie, host, marca, modelo, proc, ram, datos_ram, mobo, dict_hdd_tipos[hdd_sel], almac, datos_almac, so, mac_lan, mac_wlan, precio, dict_condiciones[cond_sel], dict_cargadores[carg_sel], renov_sel or None, obs, com):
                        notificar_exito(f"¡Laptop Serie {serie} registrada con éxito!")
        with t3:
            if not df_lap.empty:
                st.markdown("### 🔍 Filtrar Laptop a Modificar")
                f1, f2 = st.columns(2)
                with f1:
                    busq_ed_lap = st.text_input("Buscar por Hostname, Serie, Modelo o Asignado:", placeholder="Ej. VENTAS-MORELIA, Dell, Juan", key="busq_ed_lap")
                with f2:
                    opts_ed_est_lap = ["Todos"] + list(dict_est_lap.keys())
                    est_ed_sel_lap = st.selectbox("Filtrar por Estatus:", opts_ed_est_lap, key="est_ed_lap")

                df_ed_lap = df_lap.copy()
                if est_ed_sel_lap != "Todos":
                    df_ed_lap = df_ed_lap[df_ed_lap["estatus"] == est_ed_sel_lap]

                if busq_ed_lap.strip():
                    term_ed = busq_ed_lap.strip().lower()
                    df_ed_lap = df_ed_lap[
                        df_ed_lap["numero_serie"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_lap["hostname"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_lap["marca"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_lap["modelo"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_lap["asignado_a"].astype(str).str.lower().str.contains(term_ed)
                    ]

                if df_ed_lap.empty:
                    st.warning("No se encontraron laptops con los filtros seleccionados.")
                else:
                    lap_sel = st.selectbox("Selecciona Laptop:", [f"{r['numero_serie']} - {r['hostname']} ({r['marca']} {r['modelo']}) [{r['estatus']}] -> {r['asignado_a']}" for _, r in df_ed_lap.iterrows()], key="sel_ed_lap")
                    serie_ed = lap_sel.split(" - ")[0]
                    r = df_ed_lap[df_ed_lap["numero_serie"] == serie_ed].iloc[0]
                    
                    st.divider()
                    with st.form(f"form_ed_lap_{serie_ed}"):
                        c1, c2 = st.columns(2)
                        e_host = c1.text_input("Hostname:", value=str(r["hostname"] or ""))
                        e_marca = c1.text_input("Marca:", value=str(r["marca"] or ""))
                        e_mod = c1.text_input("Modelo:", value=str(r["modelo"] or ""))
                        e_proc = c1.text_input("Procesador:", value=str(r["procesador"] or ""))
                        e_ram = c1.text_input("RAM Resumen:", value=str(r["memoria_ram"] or ""))
                        e_datos_ram = c1.text_input("Datos memoria RAM :", value=str(r["datos_memoria_ram"] or ""))
                        e_mobo = c1.text_input("Motherboard:", value=str(r["motherboard"] or ""))
                        
                        e_hdd = c2.selectbox("Tipo Disco:", list(dict_hdd_tipos.keys()), index=list(dict_hdd_tipos.values()).index(r["id_hdd_tipo"]) if r["id_hdd_tipo"] in dict_hdd_tipos.values() else 0)
                        e_almac = c2.text_input("Almacenamiento Resumen:", value=str(r["almacenamiento"] or ""))
                        e_datos_almac = c2.text_input("Almacenamiento (Datos del disco duro):", value=str(r["datos_almacenamiento"] or ""))
                        e_so = c2.text_input("S.O.:", value=str(r["sistema_operativo"] or ""))
                        e_maclan = c2.text_input("MAC LAN:", value=str(r["mac_address_lan"] or ""))
                        e_macwlan = c2.text_input("MAC Wi-Fi:", value=str(r["mac_address_wlan"] or ""))
                        e_precio = c2.number_input("Precio ($):", value=float(r["precio"] or 0.0), step=500.0)
                        
                        c3, c4 = st.columns(2)
                        e_cond = c3.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                        e_carg = c3.selectbox("Cargador:", list(dict_cargadores.keys()), index=list(dict_cargadores.values()).index(r["id_cargador"]) if r["id_cargador"] in dict_cargadores.values() else 0)
                        e_est = c4.selectbox("Estatus Laptop:", list(dict_est_lap.keys()), index=list(dict_est_lap.keys()).index(r["estatus"]) if r["estatus"] in dict_est_lap else 0)
                        e_renov = c4.number_input("Renovación ID:", value=int(r["id_renovacion"] or 0))

                        e_obs = st.text_area("Observaciones (Diagnósticos/Bajas):", value=str(r["observaciones"] or ""))
                        e_com = st.text_area("Comentarios (Estatus físico - va al Word):", value=str(r["comentarios"] or ""))
                        if st.form_submit_button("💾 Actualizar Laptop", type="primary"):
                            if actualizar_laptop(serie_ed, e_host, e_marca, e_mod, e_proc, e_ram, e_datos_ram, e_mobo, dict_hdd_tipos[e_hdd], e_almac, e_datos_almac, e_so, e_maclan, e_macwlan, e_precio, dict_condiciones[e_cond], dict_cargadores[e_carg], e_renov or None, dict_est_lap[e_est], e_obs, e_com):
                                notificar_exito(f"¡Laptop Serie {serie_ed} actualizada correctamente!!")

    # --------------------------------------------------------------------------
    # 3. CPUS
    # --------------------------------------------------------------------------
    with tab_cpu:
        df_cpu = obtener_cpus_df()
        dict_est_cpu = obtener_catalogo_dict("estatus_cpu", "id_estatus_cpu", "estatus_cpu")
        t1, t2, t3 = st.tabs(["📋 Consulta General", "➕ Registrar Nuevo", "✏️ Editar / Modificar"])
        with t1:
            if not df_cpu.empty:
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    txt_cpu = st.text_input("🔍 Buscar en CPUs:", placeholder="Ej. Hostname, Serie, Juan, Sahuayo", key="txt_f_cpu")
                with c_f2:
                    opts_est_cpu = ["Todos"] + list(dict_est_cpu.keys())
                    est_sel_cpu = st.selectbox("Filtrar por Estatus:", opts_est_cpu, key="est_f_cpu")

                df_filt_cpu = df_cpu.copy()
                if est_sel_cpu != "Todos":
                    df_filt_cpu = df_filt_cpu[df_filt_cpu["estatus"] == est_sel_cpu]

                if txt_cpu.strip():
                    term = txt_cpu.strip().lower()
                    df_filt_cpu = df_filt_cpu[
                        df_filt_cpu["hostname"].astype(str).str.lower().str.contains(term) |
                        df_filt_cpu["numero_serie"].astype(str).str.lower().str.contains(term) |
                        df_filt_cpu["marca"].astype(str).str.lower().str.contains(term) |
                        df_filt_cpu["modelo"].astype(str).str.lower().str.contains(term) |
                        df_filt_cpu["asignado_a"].astype(str).str.lower().str.contains(term) |
                        df_filt_cpu["sucursal"].astype(str).str.lower().str.contains(term)
                    ]

                df_view = df_filt_cpu[["hostname", "numero_serie", "marca", "modelo", "procesador", "memoria_ram", "datos_memoria_ram", "tipo_almacenamiento", "almacenamiento", "datos_almacenamiento", "sistema_operativo", "mac_address_lan", "mac_address_wlan", "estatus", "asignado_a", "sucursal", "observaciones", "comentarios"]]
                st.dataframe(df_view, use_container_width=True, hide_index=True)
                
                c_inf, c_btn = st.columns([3, 1])
                with c_inf:
                    st.caption(f"Mostrando **{len(df_filt_cpu)}** de **{len(df_cpu)}** CPUs")
                with c_btn:
                    st.download_button(
                        label="📊 Exportar CPUs (.xlsx)",
                        data=generar_excel_bytes(df_view, "CPUs"),
                        file_name="Inventario_CPUs_AGROCISA.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True
                    )
        with t2:
            with st.form("form_add_cpu"):
                c1, c2 = st.columns(2)
                host = c1.text_input("Hostname*:")
                serie = c1.text_input("Número de Serie*:")
                marca = c1.text_input("Marca*:")
                modelo = c1.text_input("Modelo*:")
                proc = c1.text_input("Procesador*:")
                ram = c1.text_input("RAM Resumen*:")
                datos_ram = c1.text_input("RAM Speccy:")
                hdd_sel = c2.selectbox("Tipo Disco:", list(dict_hdd_tipos.keys()))
                almac = c2.text_input("Almacenamiento Resumen*:")
                datos_almac = c2.text_input("Almacenamiento Speccy:")
                so = c2.text_input("S.O.*:", value="Windows 11 Pro")
                mac_lan = c2.text_input("MAC LAN:")
                mac_wlan = c2.text_input("MAC Wi-Fi:")
                cond_sel = c2.selectbox("Condición:", list(dict_condiciones.keys()))
                obs = st.text_area("Observaciones (Diagnóstico/Baja):")
                com = st.text_area("Comentarios (Estatus físico - va al Word):")
                if st.form_submit_button("💾 Guardar CPU", type="primary"):
                    if host and serie and guardar_cpu(host, serie, marca, modelo, proc, ram, datos_ram, dict_hdd_tipos[hdd_sel], almac, datos_almac, so, mac_lan, mac_wlan, dict_condiciones[cond_sel], obs, com):
                        notificar_exito(f"¡CPU Hostname {host} registrado con éxito!")
        with t3:
            if not df_cpu.empty:
                st.markdown("### 🔍 Filtrar CPU a Modificar")
                f1, f2 = st.columns(2)
                with f1:
                    busq_ed_cpu = st.text_input("Buscar por Hostname, Serie, Modelo o Asignado:", placeholder="Ej. CPU-RECEPCION, HP, Juan", key="busq_ed_cpu")
                with f2:
                    opts_ed_est_cpu = ["Todos"] + list(dict_est_cpu.keys())
                    est_ed_sel_cpu = st.selectbox("Filtrar por Estatus:", opts_ed_est_cpu, key="est_ed_cpu")

                df_ed_cpu = df_cpu.copy()
                if est_ed_sel_cpu != "Todos":
                    df_ed_cpu = df_ed_cpu[df_ed_cpu["estatus"] == est_ed_sel_cpu]

                if busq_ed_cpu.strip():
                    term_ed = busq_ed_cpu.strip().lower()
                    df_ed_cpu = df_ed_cpu[
                        df_ed_cpu["hostname"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_cpu["numero_serie"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_cpu["marca"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_cpu["modelo"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_cpu["asignado_a"].astype(str).str.lower().str.contains(term_ed)
                    ]

                if df_ed_cpu.empty:
                    st.warning("No se encontraron CPUs con los filtros seleccionados.")
                else:
                    cpu_sel = st.selectbox("Selecciona CPU:", [f"{r['hostname']} - {r['numero_serie']} ({r['marca']} {r['modelo']}) [{r['estatus']}] -> {r['asignado_a']}" for _, r in df_ed_cpu.iterrows()], key="sel_ed_cpu")
                    host_ed = cpu_sel.split(" - ")[0]
                    r = df_ed_cpu[df_ed_cpu["hostname"] == host_ed].iloc[0]
                    
                    st.divider()
                    with st.form(f"form_ed_cpu_{host_ed}"):
                        c1, c2 = st.columns(2)
                        e_ser = c1.text_input("Número de Serie:", value=str(r["numero_serie"] or ""))
                        e_marca = c1.text_input("Marca:", value=str(r["marca"] or ""))
                        e_mod = c1.text_input("Modelo:", value=str(r["modelo"] or ""))
                        e_proc = c1.text_input("Procesador:", value=str(r["procesador"] or ""))
                        e_ram = c1.text_input("RAM Resumen:", value=str(r["memoria_ram"] or ""))
                        e_datos_ram = c1.text_input("RAM Speccy:", value=str(r["datos_memoria_ram"] or ""))
                        
                        e_hdd = c2.selectbox("Tipo Disco:", list(dict_hdd_tipos.keys()), index=list(dict_hdd_tipos.values()).index(r["id_hdd_tipo"]) if r["id_hdd_tipo"] in dict_hdd_tipos.values() else 0)
                        e_almac = c2.text_input("Almacenamiento Resumen:", value=str(r["almacenamiento"] or ""))
                        e_datos_almac = c2.text_input("Almacenamiento Speccy:", value=str(r["datos_almacenamiento"] or ""))
                        e_so = c2.text_input("S.O.:", value=str(r["sistema_operativo"] or ""))
                        e_maclan = c2.text_input("MAC LAN:", value=str(r["mac_address_lan"] or ""))
                        e_macwlan = c2.text_input("MAC Wi-Fi:", value=str(r["mac_address_wlan"] or ""))
                        e_cond = c2.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                        e_est = c2.selectbox("Estatus CPU:", list(dict_est_cpu.keys()), index=list(dict_est_cpu.keys()).index(r["estatus"]) if r["estatus"] in dict_est_cpu else 0)
                        
                        e_obs = st.text_area("Observaciones (Diagnóstico/Baja):", value=str(r["observaciones"] or ""))
                        e_com = st.text_area("Comentarios (Estatus físico - va al Word):", value=str(r["comentarios"] or ""))
                        if st.form_submit_button("💾 Actualizar CPU", type="primary"):
                            if actualizar_cpu(host_ed, e_ser, e_marca, e_mod, e_proc, e_ram, e_datos_ram, dict_hdd_tipos[e_hdd], e_almac, e_datos_almac, e_so, e_maclan, e_macwlan, dict_condiciones[e_cond], dict_est_cpu[e_est], e_obs, e_com):
                                notificar_exito(f"¡CPU Hostname {host_ed} actualizado correctamente!!")

    # --------------------------------------------------------------------------
    # 4. MONITORES
    # --------------------------------------------------------------------------
    with tab_mon:
        df_mon = obtener_monitores_df()
        dict_est_mon = obtener_catalogo_dict("estatus_monitores", "id_estatus_monitor", "estatus_monitor")
        t1, t2, t3 = st.tabs(["📋 Consulta General", "➕ Registrar Nuevo", "✏️ Editar / Modificar"])
        with t1:
            if not df_mon.empty:
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    txt_mon = st.text_input("🔍 Buscar en Monitores:", placeholder="Ej. LG, HP, Serie, Host, Juan", key="txt_f_mon")
                with c_f2:
                    opts_est_mon = ["Todos"] + list(dict_est_mon.keys())
                    est_sel_mon = st.selectbox("Filtrar por Estatus:", opts_est_mon, key="est_f_mon")

                df_filt_mon = df_mon.copy()
                if est_sel_mon != "Todos":
                    df_filt_mon = df_filt_mon[df_filt_mon["estatus"] == est_sel_mon]

                if txt_mon.strip():
                    term = txt_mon.strip().lower()
                    df_filt_mon = df_filt_mon[
                        df_filt_mon["numero_serie"].astype(str).str.lower().str.contains(term) |
                        df_filt_mon["hostname"].astype(str).str.lower().str.contains(term) |
                        df_filt_mon["marca"].astype(str).str.lower().str.contains(term) |
                        df_filt_mon["modelo"].astype(str).str.lower().str.contains(term) |
                        df_filt_mon["asignado_a"].astype(str).str.lower().str.contains(term) |
                        df_filt_mon["sucursal"].astype(str).str.lower().str.contains(term)
                    ]

                df_view = df_filt_mon[["numero_serie", "hostname", "marca", "modelo", "resolucion", "estatus", "asignado_a", "sucursal", "observaciones", "comentarios"]]
                st.dataframe(df_view, use_container_width=True, hide_index=True)
                
                c_inf, c_btn = st.columns([3, 1])
                with c_inf:
                    st.caption(f"Mostrando **{len(df_filt_mon)}** de **{len(df_mon)}** Monitores")
                with c_btn:
                    st.download_button(
                        label="📊 Exportar Monitores (.xlsx)",
                        data=generar_excel_bytes(df_view, "Monitores"),
                        file_name="Inventario_Monitores_AGROCISA.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True
                    )
        with t2:
            with st.form("form_add_mon"):
                c1, c2 = st.columns(2)
                serie = c1.text_input("Número de Serie*:")
                host = c1.text_input("Hostname Asociado:")
                marca = c1.text_input("Marca*:")
                modelo = c2.text_input("Modelo*:")
                resol = c2.text_input("Resolución (ej. 1920x1080):")
                cond_sel = c2.selectbox("Condición:", list(dict_condiciones.keys()))
                obs = st.text_area("Observaciones (Diagnóstico/Baja):")
                com = st.text_area("Comentarios (Estatus físico - va al Word):")
                if st.form_submit_button("💾 Guardar Monitor", type="primary"):
                    if serie and guardar_monitor(serie, host, marca, modelo, resol, dict_condiciones[cond_sel], obs, com):
                        notificar_exito(f"¡Monitor Serie {serie} registrado con éxito!")
        with t3:
            if not df_mon.empty:
                st.markdown("### 🔍 Filtrar Monitor a Modificar")
                f1, f2 = st.columns(2)
                with f1:
                    busq_ed_mon = st.text_input("Buscar por Serie, Marca, Modelo o Asignado:", placeholder="Ej. LG, HP, Juan", key="busq_ed_mon")
                with f2:
                    opts_ed_est_mon = ["Todos"] + list(dict_est_mon.keys())
                    est_ed_sel_mon = st.selectbox("Filtrar por Estatus:", opts_ed_est_mon, key="est_ed_mon")

                df_ed_mon = df_mon.copy()
                if est_ed_sel_mon != "Todos":
                    df_ed_mon = df_ed_mon[df_ed_mon["estatus"] == est_ed_sel_mon]

                if busq_ed_mon.strip():
                    term_ed = busq_ed_mon.strip().lower()
                    df_ed_mon = df_ed_mon[
                        df_ed_mon["numero_serie"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_mon["hostname"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_mon["marca"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_mon["modelo"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_mon["asignado_a"].astype(str).str.lower().str.contains(term_ed)
                    ]

                if df_ed_mon.empty:
                    st.warning("No se encontraron monitores con los filtros seleccionados.")
                else:
                    mon_sel = st.selectbox("Selecciona Monitor:", [f"{r['numero_serie']} - {r['marca']} {r['modelo']} [{r['estatus']}] -> {r['asignado_a']}" for _, r in df_ed_mon.iterrows()], key="sel_ed_mon")
                    serie_ed = mon_sel.split(" - ")[0]
                    r = df_ed_mon[df_ed_mon["numero_serie"] == serie_ed].iloc[0]
                    
                    st.divider()
                    with st.form(f"form_ed_mon_{serie_ed}"):
                        c1, c2 = st.columns(2)
                        e_host = c1.text_input("Hostname:", value=str(r["hostname"] or ""))
                        e_marca = c1.text_input("Marca:", value=str(r["marca"] or ""))
                        e_mod = c2.text_input("Modelo:", value=str(r["modelo"] or ""))
                        e_resol = c2.text_input("Resolución:", value=str(r["resolucion"] or ""))
                        e_cond = c1.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                        e_est = c2.selectbox("Estatus Monitor:", list(dict_est_mon.keys()), index=list(dict_est_mon.keys()).index(r["estatus"]) if r["estatus"] in dict_est_mon else 0)
                        
                        e_obs = st.text_area("Observaciones (Diagnóstico/Baja):", value=str(r["observaciones"] or ""))
                        e_com = st.text_area("Comentarios (Estatus físico - va al Word):", value=str(r["comentarios"] or ""))
                        if st.form_submit_button("💾 Actualizar Monitor", type="primary"):
                            if actualizar_monitor(serie_ed, e_host, e_marca, e_mod, e_resol, dict_condiciones[e_cond], dict_est_mon[e_est], e_obs, e_com):
                                notificar_exito(f"¡Monitor Serie {serie_ed} actualizado correctamente!!")

    # --------------------------------------------------------------------------
    # 5. TABLETS
    # --------------------------------------------------------------------------
    with tab_tab:
        df_tab = obtener_tablets_df()
        dict_est_tab = obtener_catalogo_dict("estatus_tablets", "id_estatus_tablet", "estatus_tablet")
        t1, t2, t3 = st.tabs(["📋 Consulta General", "➕ Registrar Nuevo", "✏️ Editar / Modificar"])
        with t1:
            if not df_tab.empty:
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    txt_tab = st.text_input("🔍 Buscar en Tablets:", placeholder="Ej. Samsung, Serie, IMEI, Juan", key="txt_f_tab")
                with c_f2:
                    opts_est_tab = ["Todos"] + list(dict_est_tab.keys())
                    est_sel_tab = st.selectbox("Filtrar por Estatus:", opts_est_tab, key="est_f_tab")

                df_filt_tab = df_tab.copy()
                if est_sel_tab != "Todos":
                    df_filt_tab = df_filt_tab[df_filt_tab["estatus"] == est_sel_tab]

                if txt_tab.strip():
                    term = txt_tab.strip().lower()
                    df_filt_tab = df_filt_tab[
                        df_filt_tab["numero_serie"].astype(str).str.lower().str.contains(term) |
                        df_filt_tab["imei"].astype(str).str.lower().str.contains(term) |
                        df_filt_tab["marca"].astype(str).str.lower().str.contains(term) |
                        df_filt_tab["modelo"].astype(str).str.lower().str.contains(term) |
                        df_filt_tab["asignado_a"].astype(str).str.lower().str.contains(term) |
                        df_filt_tab["sucursal"].astype(str).str.lower().str.contains(term)
                    ]

                df_view = df_filt_tab[["numero_serie", "imei", "marca", "modelo", "mac_address", "estatus", "asignado_a", "sucursal", "observaciones", "comentarios"]]
                st.dataframe(df_view, use_container_width=True, hide_index=True)
                
                c_inf, c_btn = st.columns([3, 1])
                with c_inf:
                    st.caption(f"Mostrando **{len(df_filt_tab)}** de **{len(df_tab)}** Tablets")
                with c_btn:
                    st.download_button(
                        label="📊 Exportar Tablets (.xlsx)",
                        data=generar_excel_bytes(df_view, "Tablets"),
                        file_name="Inventario_Tablets_AGROCISA.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True
                    )
        with t2:
            with st.form("form_add_tab"):
                c1, c2 = st.columns(2)
                serie = c1.text_input("Número de Serie*:")
                imei = c1.text_input("IMEI:")
                marca = c1.text_input("Marca*:")
                modelo = c2.text_input("Modelo*:")
                mac = c2.text_input("MAC Wi-Fi:")
                cond_sel = c2.selectbox("Condición:", list(dict_condiciones.keys()))
                carg_sel = c2.selectbox("Cargador:", list(dict_cargadores.keys()))
                obs = st.text_area("Observaciones (Diagnóstico/Baja):")
                com = st.text_area("Comentarios (Estatus físico - va al Word):")
                if st.form_submit_button("💾 Guardar Tablet", type="primary"):
                    if serie and guardar_tablet(serie, imei, marca, modelo, mac, dict_condiciones[cond_sel], dict_cargadores[carg_sel], obs, com):
                        notificar_exito(f"¡Tablet Serie {serie} registrada con éxito!")
        with t3:
            if not df_tab.empty:
                st.markdown("### 🔍 Filtrar Tablet a Modificar")
                f1, f2 = st.columns(2)
                with f1:
                    busq_ed_tab = st.text_input("Buscar por Serie, IMEI, Modelo o Asignado:", placeholder="Ej. Samsung, Juan", key="busq_ed_tab")
                with f2:
                    opts_ed_est_tab = ["Todos"] + list(dict_est_tab.keys())
                    est_ed_sel_tab = st.selectbox("Filtrar por Estatus:", opts_ed_est_tab, key="est_ed_tab")

                df_ed_tab = df_tab.copy()
                if est_ed_sel_tab != "Todos":
                    df_ed_tab = df_ed_tab[df_ed_tab["estatus"] == est_ed_sel_tab]

                if busq_ed_tab.strip():
                    term_ed = busq_ed_tab.strip().lower()
                    df_ed_tab = df_ed_tab[
                        df_ed_tab["numero_serie"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_tab["imei"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_tab["marca"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_tab["modelo"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_tab["asignado_a"].astype(str).str.lower().str.contains(term_ed)
                    ]

                if df_ed_tab.empty:
                    st.warning("No se encontraron tablets con los filtros seleccionados.")
                else:
                    tab_sel = st.selectbox("Selecciona Tablet:", [f"{r['numero_serie']} - {r['marca']} {r['modelo']} [{r['estatus']}] -> {r['asignado_a']}" for _, r in df_ed_tab.iterrows()], key="sel_ed_tab")
                    serie_ed = tab_sel.split(" - ")[0]
                    r = df_ed_tab[df_ed_tab["numero_serie"] == serie_ed].iloc[0]
                    
                    st.divider()
                    with st.form(f"form_ed_tab_{serie_ed}"):
                        c1, c2 = st.columns(2)
                        e_imei = c1.text_input("IMEI:", value=str(r["imei"] or ""))
                        e_marca = c1.text_input("Marca:", value=str(r["marca"] or ""))
                        e_mod = c2.text_input("Modelo:", value=str(r["modelo"] or ""))
                        e_mac = c2.text_input("MAC Wi-Fi:", value=str(r["mac_address"] or ""))
                        e_cond = c1.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                        e_carg = c2.selectbox("Cargador:", list(dict_cargadores.keys()), index=list(dict_cargadores.values()).index(r["id_cargador"]) if r["id_cargador"] in dict_cargadores.values() else 0)
                        e_est = c2.selectbox("Estatus Tablet:", list(dict_est_tab.keys()), index=list(dict_est_tab.keys()).index(r["estatus"]) if r["estatus"] in dict_est_tab else 0)
                        
                        e_obs = st.text_area("Observaciones (Diagnóstico/Baja):", value=str(r["observaciones"] or ""))
                        e_com = st.text_area("Comentarios (Estatus físico - va al Word):", value=str(r["comentarios"] or ""))
                        if st.form_submit_button("💾 Actualizar Tablet", type="primary"):
                            if actualizar_tablet(serie_ed, e_imei, e_marca, e_mod, e_mac, dict_condiciones[e_cond], dict_cargadores[e_carg], dict_est_tab[e_est], e_obs, e_com):
                                notificar_exito(f"¡Tablet Serie {serie_ed} actualizada correctamente!!")

    # --------------------------------------------------------------------------
    # 6. DISPOSITIVOS DE RED
    # --------------------------------------------------------------------------
    with tab_red:
        df_red = obtener_dispositivos_red_df()
        dict_sucursales = obtener_catalogo_dict("sucursales", "id_sucursal", "nombre_sucursal")
        t1, t2, t3 = st.tabs(["📋 Consulta General", "➕ Registrar Nuevo", "✏️ Editar / Modificar"])
        with t1:
            if not df_red.empty:
                c_f1, c_f2 = st.columns(2)
                with c_f1:
                    txt_red = st.text_input("🔍 Buscar en Equipos de Red:", placeholder="Ej. Switch, Router, Ubiquiti, Hostname, La Barca", key="txt_f_red")
                with c_f2:
                    opts_suc_red = ["Todas"] + list(dict_sucursales.keys())
                    suc_sel_red = st.selectbox("Filtrar por Sucursal:", opts_suc_red, key="suc_f_red")

                df_filt_red = df_red.copy()
                if suc_sel_red != "Todas":
                    df_filt_red = df_filt_red[df_filt_red["sucursal"] == suc_sel_red]

                if txt_red.strip():
                    term = txt_red.strip().lower()
                    df_filt_red = df_filt_red[
                        df_filt_red["tipo"].astype(str).str.lower().str.contains(term) |
                        df_filt_red["marca"].astype(str).str.lower().str.contains(term) |
                        df_filt_red["modelo"].astype(str).str.lower().str.contains(term) |
                        df_filt_red["hostname"].astype(str).str.lower().str.contains(term) |
                        df_filt_red["numero_serie"].astype(str).str.lower().str.contains(term) |
                        df_filt_red["ubicacion_fisica"].astype(str).str.lower().str.contains(term)
                    ]

                df_view = df_filt_red[["id_dispositivo", "sucursal", "tipo", "marca", "modelo", "hostname", "ubicacion_fisica", "numero_serie", "nuevo_usuario", "password_nuevo", "ssid", "password_wpa"]]
                st.dataframe(df_view, use_container_width=True, hide_index=True)
                
                c_inf, c_btn = st.columns([3, 1])
                with c_inf:
                    st.caption(f"Mostrando **{len(df_filt_red)}** de **{len(df_red)}** Equipos de Red")
                with c_btn:
                    st.download_button(
                        label="📊 Exportar Equipos Red (.xlsx)",
                        data=generar_excel_bytes(df_view, "Dispositivos_Red"),
                        file_name="Inventario_Red_AGROCISA.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        type="primary",
                        use_container_width=True
                    )
        with t2:
            with st.form("form_add_red"):
                c1, c2 = st.columns(2)
                suc_sel = c1.selectbox("Sucursal*:", list(dict_sucursales.keys()))
                tipo = c1.text_input("Tipo (Switch, Router, AP, Cámara)*:")
                marca = c1.text_input("Marca*:")
                modelo = c1.text_input("Modelo*:")
                serie = c2.text_input("Número de Serie*:")
                mac_lan = c2.text_input("MAC LAN*:")
                mac_wlan = c2.text_input("MAC WLAN:")
                ubic = c2.text_input("Ubicación Física*:")
                st.markdown("---")
                c3, c4 = st.columns(2)
                host = c3.text_input("Hostname:")
                u_def = c3.text_input("User Def:", value="admin")
                p_def = c3.text_input("Pass Def:", type="password")
                u_nuev = c4.text_input("User Nuevo Admin:")
                p_nuev = c4.text_input("Pass Nuevo Admin:", type="password")
                puerto = c4.number_input("Puerto Admin:", value=80)
                st.markdown("---")
                c5, c6 = st.columns(2)
                ssid = c5.text_input("SSID Wi-Fi:")
                modo_wpa = c5.selectbox("Modo WPA:", ["WPA2-PSK", "WPA3-PSK", "OPEN"])
                pass_wpa = c6.text_input("Clave Wi-Fi:", type="password")
                if st.form_submit_button("💾 Guardar Equipo de Red", type="primary"):
                    if tipo and serie and mac_lan and guardar_dispositivo_red(dict_sucursales[suc_sel], tipo, marca, modelo, serie, mac_lan, mac_wlan, ubic, host, u_def, p_def, u_nuev, p_nuev, puerto, ssid, modo_wpa, pass_wpa):
                        notificar_exito(f"¡Equipo de Red {host or modelo} registrado con éxito!")
        with t3:
            if not df_red.empty:
                st.markdown("### 🔍 Filtrar Equipo de Red a Modificar")
                f1, f2 = st.columns(2)
                with f1:
                    busq_ed_red = st.text_input("Buscar por Hostname, Tipo, Marca o Serie:", placeholder="Ej. Switch, Mikrotik, La Barca", key="busq_ed_red")
                with f2:
                    opts_ed_suc_red = ["Todas"] + list(dict_sucursales.keys())
                    suc_ed_sel_red = st.selectbox("Filtrar por Sucursal:", opts_ed_suc_red, key="suc_ed_red")

                df_ed_red = df_red.copy()
                if suc_ed_sel_red != "Todas":
                    df_ed_red = df_ed_red[df_ed_red["sucursal"] == suc_ed_sel_red]

                if busq_ed_red.strip():
                    term_ed = busq_ed_red.strip().lower()
                    df_ed_red = df_ed_red[
                        df_ed_red["tipo"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_red["marca"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_red["modelo"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_red["hostname"].astype(str).str.lower().str.contains(term_ed) |
                        df_ed_red["numero_serie"].astype(str).str.lower().str.contains(term_ed)
                    ]

                if df_ed_red.empty:
                    st.warning("No se encontraron dispositivos de red con los filtros seleccionados.")
                else:
                    red_sel = st.selectbox("Selecciona Equipo de Red:", [f"{r['id_dispositivo']} - [{r['tipo']}] {r['marca']} {r['modelo']} ({r['sucursal']})" for _, r in df_ed_red.iterrows()], key="sel_ed_red")
                    id_red_ed = int(red_sel.split(" - ")[0])
                    r = df_ed_red[df_ed_red["id_dispositivo"] == id_red_ed].iloc[0]
                    
                    st.divider()
                    with st.form(f"form_ed_red_{id_red_ed}"):
                        c1, c2 = st.columns(2)
                        e_suc = c1.selectbox("Sucursal:", list(dict_sucursales.keys()), index=list(dict_sucursales.values()).index(r["id_sucursal"]) if r["id_sucursal"] in dict_sucursales.values() else 0)
                        e_tipo = c1.text_input("Tipo:", value=str(r["tipo"] or ""))
                        e_marca = c1.text_input("Marca:", value=str(r["marca"] or ""))
                        e_mod = c1.text_input("Modelo:", value=str(r["modelo"] or ""))
                        e_ser = c2.text_input("Serie:", value=str(r["numero_serie"] or ""))
                        e_maclan = c2.text_input("MAC LAN:", value=str(r["mac_address_lan"] or ""))
                        e_macwlan = c2.text_input("MAC WLAN:", value=str(r["mac_address_wlan"] or ""))
                        e_ubic = c2.text_input("Ubicación Física:", value=str(r["ubicacion_fisica"] or ""))
                        st.markdown("---")
                        c3, c4 = st.columns(2)
                        e_host = c3.text_input("Hostname:", value=str(r["hostname"] or ""))
                        e_udef = c3.text_input("User Def:", value=str(r["usuario_admin_default"] or ""))
                        e_pdef = c3.text_input("Pass Def:", value=str(r["password_admin_default"] or ""), type="password")
                        e_unuev = c4.text_input("User Admin Nuevo:", value=str(r["nuevo_usuario"] or ""))
                        e_pnuev = c4.text_input("Pass Admin Nuevo:", value=str(r["password_nuevo"] or ""), type="password")
                        e_puer = c4.number_input("Puerto Admin:", value=int(r["puerto_admin"] or 80))
                        st.markdown("---")
                        c5, c6 = st.columns(2)
                        e_ssid = c5.text_input("SSID Wi-Fi:", value=str(r["ssid"] or ""))
                        e_wpa = c5.selectbox("Modo WPA:", ["WPA2-PSK", "WPA3-PSK", "OPEN"], index=0)
                        e_pwpa = c6.text_input("Clave Wi-Fi:", value=str(r["password_wpa"] or ""), type="password")
                        if st.form_submit_button("💾 Actualizar Equipo de Red", type="primary"):
                            if actualizar_dispositivo_red(id_red_ed, dict_sucursales[e_suc], e_tipo, e_marca, e_mod, e_ser, e_maclan, e_macwlan, e_ubic, e_host, e_udef, e_pdef, e_unuev, e_pnuev, e_puer, e_ssid, e_wpa, e_pwpa):
                                notificar_exito(f"¡Dispositivo ID {id_red_ed} actualizado correctamente!!")