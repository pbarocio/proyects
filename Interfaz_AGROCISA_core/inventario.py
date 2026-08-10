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
    """Guarda una notificación persistente en session_state y recarga."""
    st.session_state["mensaje_exito"] = mensaje
    st.rerun()

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
                cj.caja_opcion AS caja, ic.numero_serie, ic.mac_address, ic.observaciones, ic.id_modelo, ic.id_condicion, ic.id_cargador, ic.id_caja
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

def guardar_celular(imei, serie, mac, numero, id_modelo, id_condicion, id_cargador, id_caja, observaciones, id_estatus=3):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "INSERT INTO inventario_celulares (imei, numero_serie, mac_address, numero, id_modelo, id_condicion, id_cargador, id_caja, observaciones, id_estatus_celular) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (imei.strip(), serie.strip(), mac.strip(), numero.strip() or None, id_modelo, id_condicion, id_cargador, id_caja, observaciones.strip(), id_estatus))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar celular: {e}")
        return False

def actualizar_celular(imei, serie, mac, numero, id_modelo, id_condicion, id_cargador, id_caja, id_estatus, observaciones):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "UPDATE inventario_celulares SET numero_serie = %s, mac_address = %s, numero = %s, id_modelo = %s, id_condicion = %s, id_cargador = %s, id_caja = %s, id_estatus_celular = %s, observaciones = %s WHERE imei = %s"
        cursor.execute(query, (serie.strip(), mac.strip(), numero.strip() or None, id_modelo, id_condicion, id_cargador, id_caja, id_estatus, observaciones.strip(), imei))
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
                il.numero_serie, il.hostname, il.marca, il.modelo, il.procesador, il.memoria_ram,
                ht.hdd_opcion AS tipo_almacenamiento, il.almacenamiento, il.sistema_operativo,
                el.estatus_laptop AS estatus, il.id_estatus_laptops,
                COALESCE(CONCAT(emp.nombre, ' ', emp.apellido_paterno), 'VACANTE / SIN ASIGNAR') AS asignado_a,
                suc.nombre_sucursal AS sucursal, c.condicion_opcion AS condicion, il.observaciones,
                il.mac_address_lan, il.mac_address_wlan, il.id_hdd_tipo, il.id_condicion
            FROM inventario_laptops il
            LEFT JOIN estatus_laptops el ON il.id_estatus_laptops = el.id_estatus_laptops
            LEFT JOIN hdd_tipo ht ON il.id_hdd_tipo = ht.id_hdd_tipo
            LEFT JOIN empleados emp ON TRIM(LEADING '0' FROM CAST(il.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(emp.codigo AS CHAR))
            LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
            LEFT JOIN condicion c ON il.id_condicion = c.id_condicion
            ORDER BY il.numero_serie DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error Laptops: {e}")
        return pd.DataFrame()

def guardar_laptop(serie, hostname, marca, modelo, proc, ram, id_hdd_tipo, almac, so, mac_lan, mac_wlan, id_condicion, obs, id_estatus=3):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "INSERT INTO inventario_laptops (numero_serie, hostname, marca, modelo, procesador, memoria_ram, id_hdd_tipo, almacenamiento, sistema_operativo, mac_address_lan, mac_address_wlan, id_condicion, observaciones, id_estatus_laptops) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (serie.strip(), hostname.strip(), marca.strip(), modelo.strip(), proc.strip(), ram.strip(), id_hdd_tipo, almac.strip(), so.strip(), mac_lan.strip(), mac_wlan.strip(), id_condicion, obs.strip(), id_estatus))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar laptop: {e}")
        return False

def actualizar_laptop(serie, hostname, marca, modelo, proc, ram, id_hdd_tipo, almac, so, mac_lan, mac_wlan, id_condicion, id_estatus, obs):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "UPDATE inventario_laptops SET hostname=%s, marca=%s, modelo=%s, procesador=%s, memoria_ram=%s, id_hdd_tipo=%s, almacenamiento=%s, sistema_operativo=%s, mac_address_lan=%s, mac_address_wlan=%s, id_condicion=%s, id_estatus_laptops=%s, observaciones=%s WHERE numero_serie=%s"
        cursor.execute(query, (hostname.strip(), marca.strip(), modelo.strip(), proc.strip(), ram.strip(), id_hdd_tipo, almac.strip(), so.strip(), mac_lan.strip(), mac_wlan.strip(), id_condicion, id_estatus, obs.strip(), serie))
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
                ic.hostname, ic.numero_serie, ic.marca, ic.modelo, ic.procesador, ic.memoria_ram,
                ht.hdd_opcion AS tipo_almacenamiento, ic.almacenamiento, ic.sistema_operativo,
                ec.estatus_cpu AS estatus, ic.id_estatus_cpu,
                COALESCE(CONCAT(emp.nombre, ' ', emp.apellido_paterno), 'VACANTE / SIN ASIGNAR') AS asignado_a,
                suc.nombre_sucursal AS sucursal, c.condicion_opcion AS condicion, ic.observaciones,
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

def guardar_cpu(hostname, serie, marca, modelo, proc, ram, id_hdd_tipo, almac, so, mac_lan, mac_wlan, id_condicion, obs, id_estatus=3):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "INSERT INTO inventario_cpu (hostname, numero_serie, marca, modelo, procesador, memoria_ram, id_hdd_tipo, almacenamiento, sistema_operativo, mac_address_lan, mac_address_wlan, id_condicion, observaciones, id_estatus_cpu) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (hostname.strip(), serie.strip(), marca.strip(), modelo.strip(), proc.strip(), ram.strip(), id_hdd_tipo, almac.strip(), so.strip(), mac_lan.strip(), mac_wlan.strip(), id_condicion, obs.strip(), id_estatus))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar CPU: {e}")
        return False

def actualizar_cpu(hostname, serie, marca, modelo, proc, ram, id_hdd_tipo, almac, so, mac_lan, mac_wlan, id_condicion, id_estatus, obs):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "UPDATE inventario_cpu SET numero_serie=%s, marca=%s, modelo=%s, procesador=%s, memoria_ram=%s, id_hdd_tipo=%s, almacenamiento=%s, sistema_operativo=%s, mac_address_lan=%s, mac_address_wlan=%s, id_condicion=%s, id_estatus_cpu=%s, observaciones=%s WHERE hostname=%s"
        cursor.execute(query, (serie.strip(), marca.strip(), modelo.strip(), proc.strip(), ram.strip(), id_hdd_tipo, almac.strip(), so.strip(), mac_lan.strip(), mac_wlan.strip(), id_condicion, id_estatus, obs.strip(), hostname))
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
                suc.nombre_sucursal AS sucursal, c.condicion_opcion AS condicion, im.observaciones, im.id_condicion
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

def guardar_monitor(serie, hostname, marca, modelo, resolucion, id_condicion, obs, id_estatus=3):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "INSERT INTO inventario_monitores (numero_serie, hostname, marca, modelo, resolucion, id_condicion, observaciones, id_estatus_monitor) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (serie.strip(), hostname.strip(), marca.strip(), modelo.strip(), resolucion.strip(), id_condicion, obs.strip(), id_estatus))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar monitor: {e}")
        return False

def actualizar_monitor(serie, hostname, marca, modelo, resolucion, id_condicion, id_estatus, obs):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "UPDATE inventario_monitores SET hostname=%s, marca=%s, modelo=%s, resolucion=%s, id_condicion=%s, id_estatus_monitor=%s, observaciones=%s WHERE numero_serie=%s"
        cursor.execute(query, (hostname.strip(), marca.strip(), modelo.strip(), resolucion.strip(), id_condicion, id_estatus, obs.strip(), serie))
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
                suc.nombre_sucursal AS sucursal, c.condicion_opcion AS condicion, it.observaciones, it.id_condicion
            FROM inventario_tablets it
            LEFT JOIN estatus_tablets et ON it.id_estatus_tablet = et.id_estatus_tablet
            LEFT JOIN empleados emp ON TRIM(LEADING '0' FROM CAST(it.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(emp.codigo AS CHAR))
            LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
            LEFT JOIN condicion c ON it.id_condicion = c.id_condicion
            ORDER BY it.numero_serie DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error Tablets: {e}")
        return pd.DataFrame()

def guardar_tablet(serie, imei, marca, modelo, mac, id_condicion, obs, id_estatus=3):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "INSERT INTO inventario_tablets (numero_serie, imei, marca, modelo, mac_address, id_condicion, observaciones, id_estatus_tablet) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (serie.strip(), imei.strip(), marca.strip(), modelo.strip(), mac.strip(), id_condicion, obs.strip(), id_estatus))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar tablet: {e}")
        return False

def actualizar_tablet(serie, imei, marca, modelo, mac, id_condicion, id_estatus, obs):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = "UPDATE inventario_tablets SET imei=%s, marca=%s, modelo=%s, mac_address=%s, id_condicion=%s, id_estatus_tablet=%s, observaciones=%s WHERE numero_serie=%s"
        cursor.execute(query, (imei.strip(), marca.strip(), modelo.strip(), mac.strip(), id_condicion, id_estatus, obs.strip(), serie))
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

    # ALERTA DE ÉXITO PERSISTENTE TRAS EL REFRESH
    if "mensaje_exito" in st.session_state:
        st.success(f"✅ {st.session_state['mensaje_exito']}")
        del st.session_state["mensaje_exito"]

    # Carga de catálogos compartidos
    dict_condiciones = obtener_catalogo_dict("condicion", "id_condicion", "condicion_opcion")
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
        dict_carg = obtener_catalogo_dict("cargadores", "id_cargador", "cargador_opcion")
        dict_caj = obtener_catalogo_dict("caja", "id_caja", "caja_opcion")
        dict_est = obtener_catalogo_dict("estatus_celulares", "id_estatus_celular", "estatus_celular")
        
        t1, t2, t3 = st.tabs(["📋 Consulta General", "➕ Registrar Nuevo", "✏️ Editar / Modificar"])
        with t1:
            if not df_cel.empty:
                st.dataframe(df_cel[["imei", "numero_linea", "marca_modelo", "estatus", "asignado_a", "sucursal", "observaciones"]], use_container_width=True, hide_index=True)
        with t2:
            with st.form("form_add_cel"):
                c1, c2 = st.columns(2)
                imei = c1.text_input("IMEI*:")
                serie = c1.text_input("Número de Serie*:")
                mac = c1.text_input("MAC Wi-Fi:")
                numero = c1.text_input("Línea Asignada:")
                mod_sel = c2.selectbox("Modelo:", list(dict_mod.keys()))
                cond_sel = c2.selectbox("Condición:", list(dict_condiciones.keys()))
                carg_sel = c2.selectbox("Cargador:", list(dict_carg.keys()))
                caj_sel = c2.selectbox("Caja:", list(dict_caj.keys()))
                obs = st.text_area("Observaciones:")
                if st.form_submit_button("💾 Guardar Celular", type="primary"):
                    if imei and serie and guardar_celular(imei, serie, mac, numero, dict_mod[mod_sel], dict_condiciones[cond_sel], dict_carg[carg_sel], dict_caj[caj_sel], obs):
                        notificar_exito(f"¡Celular IMEI {imei} dado de alta con éxito!")
        with t3:
            if not df_cel.empty:
                cel_sel = st.selectbox("Selecciona Celular:", [f"{r['imei']} - {r['marca_modelo']}" for _, r in df_cel.iterrows()])
                imei_ed = cel_sel.split(" - ")[0]
                r = df_cel[df_cel["imei"] == imei_ed].iloc[0]
                with st.form(f"form_ed_cel_{imei_ed}"):
                    c1, c2 = st.columns(2)
                    e_ser = c1.text_input("Número de Serie:", value=str(r["numero_serie"] or ""))
                    e_mac = c1.text_input("MAC Wi-Fi:", value=str(r["mac_address"] or ""))
                    e_num = c1.text_input("Línea:", value=str(r["numero_linea"] or ""))
                    e_est = c1.selectbox("Estatus:", list(dict_est.keys()), index=list(dict_est.keys()).index(r["estatus"]) if r["estatus"] in dict_est else 0)
                    e_mod = c2.selectbox("Modelo:", list(dict_mod.keys()), index=list(dict_mod.values()).index(r["id_modelo"]) if r["id_modelo"] in dict_mod.values() else 0)
                    e_cond = c2.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                    e_carg = c2.selectbox("Cargador:", list(dict_carg.keys()), index=list(dict_carg.values()).index(r["id_cargador"]) if r["id_cargador"] in dict_carg.values() else 0)
                    e_caj = c2.selectbox("Caja:", list(dict_caj.keys()), index=list(dict_caj.values()).index(r["id_caja"]) if r["id_caja"] in dict_caj.values() else 0)
                    e_obs = st.text_area("Observaciones:", value=str(r["observaciones"] or ""))
                    if st.form_submit_button("💾 Actualizar Celular", type="primary"):
                        if actualizar_celular(imei_ed, e_ser, e_mac, e_num, dict_mod[e_mod], dict_condiciones[e_cond], dict_carg[e_carg], dict_caj[e_caj], dict_est[e_est], e_obs):
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
                st.dataframe(df_lap[["numero_serie", "hostname", "marca", "modelo", "procesador", "memoria_ram", "estatus", "asignado_a", "sucursal", "observaciones"]], use_container_width=True, hide_index=True)
        with t2:
            with st.form("form_add_lap"):
                c1, c2 = st.columns(2)
                serie = c1.text_input("Número de Serie*:")
                host = c1.text_input("Hostname*:")
                marca = c1.text_input("Marca*:")
                modelo = c1.text_input("Modelo*:")
                proc = c1.text_input("Procesador*:")
                ram = c1.text_input("RAM (ej. 16GB)*:")
                hdd_sel = c2.selectbox("Tipo Disco:", list(dict_hdd_tipos.keys()))
                almac = c2.text_input("Almacenamiento (ej. 512GB)*:")
                so = c2.text_input("Sistema Operativo*:", value="Windows 11 Pro")
                mac_lan = c2.text_input("MAC LAN:")
                mac_wlan = c2.text_input("MAC Wi-Fi:")
                cond_sel = c2.selectbox("Condición:", list(dict_condiciones.keys()))
                obs = st.text_area("Observaciones:")
                if st.form_submit_button("💾 Guardar Laptop", type="primary"):
                    if serie and host and guardar_laptop(serie, host, marca, modelo, proc, ram, dict_hdd_tipos[hdd_sel], almac, so, mac_lan, mac_wlan, dict_condiciones[cond_sel], obs):
                        notificar_exito(f"¡Laptop Serie {serie} registrada con éxito!")
        with t3:
            if not df_lap.empty:
                lap_sel = st.selectbox("Selecciona Laptop:", [f"{r['numero_serie']} - {r['hostname']} ({r['marca']} {r['modelo']})" for _, r in df_lap.iterrows()])
                serie_ed = lap_sel.split(" - ")[0]
                r = df_lap[df_lap["numero_serie"] == serie_ed].iloc[0]
                with st.form(f"form_ed_lap_{serie_ed}"):
                    c1, c2 = st.columns(2)
                    e_host = c1.text_input("Hostname:", value=str(r["hostname"] or ""))
                    e_marca = c1.text_input("Marca:", value=str(r["marca"] or ""))
                    e_mod = c1.text_input("Modelo:", value=str(r["modelo"] or ""))
                    e_proc = c1.text_input("Procesador:", value=str(r["procesador"] or ""))
                    e_ram = c1.text_input("RAM:", value=str(r["memoria_ram"] or ""))
                    e_hdd = c2.selectbox("Tipo Disco:", list(dict_hdd_tipos.keys()), index=list(dict_hdd_tipos.values()).index(r["id_hdd_tipo"]) if r["id_hdd_tipo"] in dict_hdd_tipos.values() else 0)
                    e_almac = c2.text_input("Almacenamiento:", value=str(r["almacenamiento"] or ""))
                    e_so = c2.text_input("S.O.:", value=str(r["sistema_operativo"] or ""))
                    e_maclan = c2.text_input("MAC LAN:", value=str(r["mac_address_lan"] or ""))
                    e_macwlan = c2.text_input("MAC Wi-Fi:", value=str(r["mac_address_wlan"] or ""))
                    e_cond = c2.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                    e_est = c2.selectbox("Estatus Laptop:", list(dict_est_lap.keys()), index=list(dict_est_lap.keys()).index(r["estatus"]) if r["estatus"] in dict_est_lap else 0)
                    e_obs = st.text_area("Observaciones:", value=str(r["observaciones"] or ""))
                    if st.form_submit_button("💾 Actualizar Laptop", type="primary"):
                        if actualizar_laptop(serie_ed, e_host, e_marca, e_mod, e_proc, e_ram, dict_hdd_tipos[e_hdd], e_almac, e_so, e_maclan, e_macwlan, dict_condiciones[e_cond], dict_est_lap[e_est], e_obs):
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
                st.dataframe(df_cpu[["hostname", "numero_serie", "marca", "modelo", "procesador", "memoria_ram", "estatus", "asignado_a", "sucursal", "observaciones"]], use_container_width=True, hide_index=True)
        with t2:
            with st.form("form_add_cpu"):
                c1, c2 = st.columns(2)
                host = c1.text_input("Hostname*:")
                serie = c1.text_input("Número de Serie*:")
                marca = c1.text_input("Marca*:")
                modelo = c1.text_input("Modelo*:")
                proc = c1.text_input("Procesador*:")
                ram = c1.text_input("RAM*:")
                hdd_sel = c2.selectbox("Tipo Disco:", list(dict_hdd_tipos.keys()))
                almac = c2.text_input("Almacenamiento*:")
                so = c2.text_input("S.O.*:", value="Windows 11 Pro")
                mac_lan = c2.text_input("MAC LAN:")
                mac_wlan = c2.text_input("MAC Wi-Fi:")
                cond_sel = c2.selectbox("Condición:", list(dict_condiciones.keys()))
                obs = st.text_area("Observaciones:")
                if st.form_submit_button("💾 Guardar CPU", type="primary"):
                    if host and serie and guardar_cpu(host, serie, marca, modelo, proc, ram, dict_hdd_tipos[hdd_sel], almac, so, mac_lan, mac_wlan, dict_condiciones[cond_sel], obs):
                        notificar_exito(f"¡CPU Hostname {host} registrado con éxito!")
        with t3:
            if not df_cpu.empty:
                cpu_sel = st.selectbox("Selecciona CPU:", [f"{r['hostname']} - {r['numero_serie']} ({r['marca']} {r['modelo']})" for _, r in df_cpu.iterrows()])
                host_ed = cpu_sel.split(" - ")[0]
                r = df_cpu[df_cpu["hostname"] == host_ed].iloc[0]
                with st.form(f"form_ed_cpu_{host_ed}"):
                    c1, c2 = st.columns(2)
                    e_ser = c1.text_input("Número de Serie:", value=str(r["numero_serie"] or ""))
                    e_marca = c1.text_input("Marca:", value=str(r["marca"] or ""))
                    e_mod = c1.text_input("Modelo:", value=str(r["modelo"] or ""))
                    e_proc = c1.text_input("Procesador:", value=str(r["procesador"] or ""))
                    e_ram = c1.text_input("RAM:", value=str(r["memoria_ram"] or ""))
                    e_hdd = c2.selectbox("Tipo Disco:", list(dict_hdd_tipos.keys()), index=list(dict_hdd_tipos.values()).index(r["id_hdd_tipo"]) if r["id_hdd_tipo"] in dict_hdd_tipos.values() else 0)
                    e_almac = c2.text_input("Almacenamiento:", value=str(r["almacenamiento"] or ""))
                    e_so = c2.text_input("S.O.:", value=str(r["sistema_operativo"] or ""))
                    e_maclan = c2.text_input("MAC LAN:", value=str(r["mac_address_lan"] or ""))
                    e_macwlan = c2.text_input("MAC Wi-Fi:", value=str(r["mac_address_wlan"] or ""))
                    e_cond = c2.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                    e_est = c2.selectbox("Estatus CPU:", list(dict_est_cpu.keys()), index=list(dict_est_cpu.keys()).index(r["estatus"]) if r["estatus"] in dict_est_cpu else 0)
                    e_obs = st.text_area("Observaciones:", value=str(r["observaciones"] or ""))
                    if st.form_submit_button("💾 Actualizar CPU", type="primary"):
                        if actualizar_cpu(host_ed, e_ser, e_marca, e_mod, e_proc, e_ram, dict_hdd_tipos[e_hdd], e_almac, e_so, e_maclan, e_macwlan, dict_condiciones[e_cond], dict_est_cpu[e_est], e_obs):
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
                st.dataframe(df_mon[["numero_serie", "hostname", "marca", "modelo", "resolucion", "estatus", "asignado_a", "sucursal", "observaciones"]], use_container_width=True, hide_index=True)
        with t2:
            with st.form("form_add_mon"):
                c1, c2 = st.columns(2)
                serie = c1.text_input("Número de Serie*:")
                host = c1.text_input("Hostname Asociado:")
                marca = c1.text_input("Marca*:")
                modelo = c2.text_input("Modelo*:")
                resol = c2.text_input("Resolución (ej. 1920x1080):")
                cond_sel = c2.selectbox("Condición:", list(dict_condiciones.keys()))
                obs = st.text_area("Observaciones:")
                if st.form_submit_button("💾 Guardar Monitor", type="primary"):
                    if serie and guardar_monitor(serie, host, marca, modelo, resol, dict_condiciones[cond_sel], obs):
                        notificar_exito(f"¡Monitor Serie {serie} registrado con éxito!")
        with t3:
            if not df_mon.empty:
                mon_sel = st.selectbox("Selecciona Monitor:", [f"{r['numero_serie']} - {r['marca']} {r['modelo']}" for _, r in df_mon.iterrows()])
                serie_ed = mon_sel.split(" - ")[0]
                r = df_mon[df_mon["numero_serie"] == serie_ed].iloc[0]
                with st.form(f"form_ed_mon_{serie_ed}"):
                    c1, c2 = st.columns(2)
                    e_host = c1.text_input("Hostname:", value=str(r["hostname"] or ""))
                    e_marca = c1.text_input("Marca:", value=str(r["marca"] or ""))
                    e_mod = c2.text_input("Modelo:", value=str(r["modelo"] or ""))
                    e_resol = c2.text_input("Resolución:", value=str(r["resolucion"] or ""))
                    e_cond = c1.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                    e_est = c2.selectbox("Estatus Monitor:", list(dict_est_mon.keys()), index=list(dict_est_mon.keys()).index(r["estatus"]) if r["estatus"] in dict_est_mon else 0)
                    e_obs = st.text_area("Observaciones:", value=str(r["observaciones"] or ""))
                    if st.form_submit_button("💾 Actualizar Monitor", type="primary"):
                        if actualizar_monitor(serie_ed, e_host, e_marca, e_mod, e_resol, dict_condiciones[e_cond], dict_est_mon[e_est], e_obs):
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
                st.dataframe(df_tab[["numero_serie", "imei", "marca", "modelo", "estatus", "asignado_a", "sucursal", "observaciones"]], use_container_width=True, hide_index=True)
        with t2:
            with st.form("form_add_tab"):
                c1, c2 = st.columns(2)
                serie = c1.text_input("Número de Serie*:")
                imei = c1.text_input("IMEI:")
                marca = c1.text_input("Marca*:")
                modelo = c2.text_input("Modelo*:")
                mac = c2.text_input("MAC Wi-Fi:")
                cond_sel = c2.selectbox("Condición:", list(dict_condiciones.keys()))
                obs = st.text_area("Observaciones:")
                if st.form_submit_button("💾 Guardar Tablet", type="primary"):
                    if serie and guardar_tablet(serie, imei, marca, modelo, mac, dict_condiciones[cond_sel], obs):
                        notificar_exito(f"¡Tablet Serie {serie} registrada con éxito!")
        with t3:
            if not df_tab.empty:
                tab_sel = st.selectbox("Selecciona Tablet:", [f"{r['numero_serie']} - {r['marca']} {r['modelo']}" for _, r in df_tab.iterrows()])
                serie_ed = tab_sel.split(" - ")[0]
                r = df_tab[df_tab["numero_serie"] == serie_ed].iloc[0]
                with st.form(f"form_ed_tab_{serie_ed}"):
                    c1, c2 = st.columns(2)
                    e_imei = c1.text_input("IMEI:", value=str(r["imei"] or ""))
                    e_marca = c1.text_input("Marca:", value=str(r["marca"] or ""))
                    e_mod = c2.text_input("Modelo:", value=str(r["modelo"] or ""))
                    e_mac = c2.text_input("MAC Wi-Fi:", value=str(r["mac_address"] or ""))
                    e_cond = c1.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                    e_est = c2.selectbox("Estatus Tablet:", list(dict_est_tab.keys()), index=list(dict_est_tab.keys()).index(r["estatus"]) if r["estatus"] in dict_est_tab else 0)
                    e_obs = st.text_area("Observaciones:", value=str(r["observaciones"] or ""))
                    if st.form_submit_button("💾 Actualizar Tablet", type="primary"):
                        if actualizar_tablet(serie_ed, e_imei, e_marca, e_mod, e_mac, dict_condiciones[e_cond], dict_est_tab[e_est], e_obs):
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
                st.dataframe(df_red[["id_dispositivo", "sucursal", "tipo", "marca", "modelo", "hostname", "ubicacion_fisica", "numero_serie", "nuevo_usuario", "password_nuevo", "ssid", "password_wpa"]], use_container_width=True, hide_index=True)
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
                red_sel = st.selectbox("Selecciona Equipo de Red:", [f"{r['id_dispositivo']} - [{r['tipo']}] {r['marca']} {r['modelo']} ({r['sucursal']})" for _, r in df_red.iterrows()])
                id_red_ed = int(red_sel.split(" - ")[0])
                r = df_red[df_red["id_dispositivo"] == id_red_ed].iloc[0]
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