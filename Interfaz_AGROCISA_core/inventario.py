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

def limpiar_str_null(val):
    if val is None or pd.isna(val):
        return None
    val_clean = str(val).strip()
    if val_clean.lower() in ["", "nan", "none", "null", "<na>"]:
        return None
    return val_clean

def limpiar_int(val, defecto=0):
    if val is None or pd.isna(val):
        return defecto
    try:
        return int(float(val))
    except Exception:
        return defecto

def obtener_catalogo_dict(tabla, col_id, col_nombre):
    try:
        conn = obtener_conexion()
        if not conn:
            return {}
        query = f"SELECT {col_id}, {col_nombre} FROM {tabla} ORDER BY {col_id} ASC"
        df = pd.read_sql(query, conn)
        conn.close()
        return dict(zip(df[col_nombre].astype(str), df[col_id].astype(int)))
    except Exception as e:
        st.error(f"⚠️ Error al cargar catálogo '{tabla}': {e}")
        return {}

def obtener_lista_lineas_telefonicas():
    """Obtiene todos los números de líneas telefónicas existentes para listas desplegables."""
    try:
        conn = obtener_conexion()
        if not conn:
            return []
        df = pd.read_sql("SELECT numero FROM lineas_telefonicas ORDER BY numero ASC", conn)
        conn.close()
        return [str(num).strip() for num in df["numero"].dropna().unique() if str(num).strip() != ""]
    except Exception:
        return []

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
                ic.id_estatus_celular, COALESCE(CONCAT_WS(' ', emp.nombre, emp.apellido_paterno, emp.apellido_materno), 'VACANTE / SIN ASIGNAR') AS asignado_a,
                COALESCE(suc.nombre_sucursal, 'SIN SUCURSAL') AS sucursal,
                COALESCE(dep.nombre_departamento, 'SIN DEPARTAMENTO') AS departamento,
                COALESCE(pue.nombre_puesto, 'SIN PUESTO') AS puesto,
                c.condicion_opcion AS condicion, cg.cargador_opcion AS cargador,
                cj.caja_opcion AS caja, ic.numero_serie, ic.mac_address, ic.observaciones, ic.comentarios,
                ic.id_modelo, ic.id_condicion, ic.id_cargador, ic.id_caja
            FROM inventario_celulares ic
            LEFT JOIN modelos_celulares m ON ic.id_modelo = m.id_modelo
            LEFT JOIN estatus_celulares e_cel ON ic.id_estatus_celular = e_cel.id_estatus_celular
            LEFT JOIN empleados emp ON TRIM(LEADING '0' FROM CAST(ic.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(emp.codigo AS CHAR))
            LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
            LEFT JOIN departamentos dep ON emp.id_departamento = dep.id_departamento
            LEFT JOIN puestos pue ON emp.id_puesto = pue.id_puesto
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

def existe_imei_celular(imei):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inventario_celulares WHERE imei = %s", (str(imei).strip(),))
        cnt = cursor.fetchone()[0]
        conn.close()
        return cnt > 0
    except Exception:
        return False

def guardar_celular(imei, serie, mac, numero, id_modelo, id_condicion, id_cargador, id_caja, observaciones, comentarios="", id_estatus=4):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        num_clean = limpiar_str_null(numero)
        query = """
            INSERT INTO inventario_celulares 
            (imei, numero_serie, mac_address, numero, id_modelo, id_condicion, id_cargador, id_caja, observaciones, comentarios, id_estatus_celular) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            imei.strip(), limpiar_str_null(serie), limpiar_str_null(mac), num_clean, 
            id_modelo, id_condicion, id_cargador, id_caja, 
            limpiar_str_null(observaciones), limpiar_str_null(comentarios), id_estatus
        ))
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def actualizar_celular(imei_viejo, imei_nuevo, serie, mac, numero, id_modelo, id_condicion, id_cargador, id_caja, id_estatus, observaciones, comentarios=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        num_clean = limpiar_str_null(numero)
        imei_v = str(imei_viejo).strip()
        imei_n = str(imei_nuevo).strip()

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        query = """
            UPDATE inventario_celulares 
            SET imei = %s, numero_serie = %s, mac_address = %s, numero = %s, id_modelo = %s, id_condicion = %s, 
                id_cargador = %s, id_caja = %s, id_estatus_celular = %s, observaciones = %s, comentarios = %s 
            WHERE imei = %s
        """
        cursor.execute(query, (
            imei_n, limpiar_str_null(serie), limpiar_str_null(mac), num_clean, id_modelo, id_condicion, 
            id_cargador, id_caja, id_estatus, limpiar_str_null(observaciones), limpiar_str_null(comentarios), imei_v
        ))

        if imei_v != imei_n:
            cursor.execute("UPDATE responsivas_celulares SET imei = %s WHERE imei = %s", (imei_n, imei_v))

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

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
                COALESCE(CONCAT_WS(' ', emp.nombre, emp.apellido_paterno, emp.apellido_materno), 'VACANTE / SIN ASIGNAR') AS asignado_a,
                COALESCE(suc.nombre_sucursal, 'SIN SUCURSAL') AS sucursal,
                COALESCE(dep.nombre_departamento, 'SIN DEPARTAMENTO') AS departamento,
                COALESCE(pue.nombre_puesto, 'SIN PUESTO') AS puesto,
                c.condicion_opcion AS condicion, cg.cargador_opcion AS cargador,
                r.renovacion_opcion AS renovacion,
                il.observaciones, il.comentarios, il.id_hdd_tipo, il.id_condicion, il.id_cargador, il.id_renovacion
            FROM inventario_laptops il
            LEFT JOIN estatus_laptops el ON il.id_estatus_laptops = el.id_estatus_laptops
            LEFT JOIN hdd_tipo ht ON il.id_hdd_tipo = ht.id_hdd_tipo
            LEFT JOIN empleados emp ON TRIM(LEADING '0' FROM CAST(il.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(emp.codigo AS CHAR))
            LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
            LEFT JOIN departamentos dep ON emp.id_departamento = dep.id_departamento
            LEFT JOIN puestos pue ON emp.id_puesto = pue.id_puesto
            LEFT JOIN condicion c ON il.id_condicion = c.id_condicion
            LEFT JOIN cargadores cg ON il.id_cargador = cg.id_cargador
            LEFT JOIN renovacion r ON il.id_renovacion = r.id_renovacion
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
        cursor.execute(query, (
            serie.strip(), hostname.strip(), marca.strip(), modelo.strip(), proc.strip(), ram.strip(), 
            limpiar_str_null(datos_ram), limpiar_str_null(mobo), id_hdd_tipo, almac.strip(), 
            limpiar_str_null(datos_almac), so.strip(), limpiar_str_null(mac_lan), limpiar_str_null(mac_wlan), 
            limpiar_int(precio, 0), id_condicion, id_cargador, id_renovacion, limpiar_str_null(obs), limpiar_str_null(com), id_estatus
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar laptop: {e}")
        return False

def actualizar_laptop(serie_vieja, serie_nueva, hostname, marca, modelo, proc, ram, datos_ram, mobo, id_hdd_tipo, almac, datos_almac, so, mac_lan, mac_wlan, precio, id_condicion, id_cargador, id_renovacion, id_estatus, obs, com=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        s_vieja = str(serie_vieja).strip()
        s_nueva = str(serie_nueva).strip()

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        query = """
            UPDATE inventario_laptops 
            SET numero_serie=%s, hostname=%s, marca=%s, modelo=%s, procesador=%s, memoria_ram=%s, datos_memoria_ram=%s, motherboard=%s, 
                id_hdd_tipo=%s, almacenamiento=%s, datos_almacenamiento=%s, sistema_operativo=%s, mac_address_lan=%s, mac_address_wlan=%s, 
                precio=%s, id_condicion=%s, id_cargador=%s, id_renovacion=%s, id_estatus_laptops=%s, observaciones=%s, comentarios=%s 
            WHERE numero_serie=%s
        """
        cursor.execute(query, (
            s_nueva, hostname.strip(), marca.strip(), modelo.strip(), proc.strip(), ram.strip(), 
            limpiar_str_null(datos_ram), limpiar_str_null(mobo), id_hdd_tipo, almac.strip(), 
            limpiar_str_null(datos_almac), so.strip(), limpiar_str_null(mac_lan), limpiar_str_null(mac_wlan), 
            limpiar_int(precio, 0), id_condicion, id_cargador, id_renovacion, id_estatus, limpiar_str_null(obs), limpiar_str_null(com), s_vieja
        ))

        if s_vieja != s_nueva:
            cursor.execute("UPDATE responsivas_laptops SET numero_serie = %s WHERE numero_serie = %s", (s_nueva, s_vieja))

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
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
                ic.id_cpu, ic.hostname, ic.numero_serie, ic.marca, ic.modelo, ic.procesador, ic.memoria_ram, ic.datos_memoria_ram,
                ic.motherboard, ht.hdd_opcion AS tipo_almacenamiento, ic.almacenamiento, ic.datos_almacenamiento, ic.sistema_operativo,
                ic.mac_address_lan, ic.mac_address_wlan, ic.precio,
                ec.estatus_cpu AS estatus, ic.id_estatus_cpu,
                COALESCE(CONCAT_WS(' ', emp.nombre, emp.apellido_paterno, emp.apellido_materno), 'VACANTE / SIN ASIGNAR') AS asignado_a,
                COALESCE(suc.nombre_sucursal, 'SIN SUCURSAL') AS sucursal,
                COALESCE(dep.nombre_departamento, 'SIN DEPARTAMENTO') AS departamento,
                COALESCE(pue.nombre_puesto, 'SIN PUESTO') AS puesto,
                c.condicion_opcion AS condicion, r.renovacion_opcion AS renovacion,
                ic.observaciones, ic.comentarios,
                ic.id_hdd_tipo, ic.id_condicion, ic.id_renovacion
            FROM inventario_cpu ic
            LEFT JOIN estatus_cpu ec ON ic.id_estatus_cpu = ec.id_estatus_cpu
            LEFT JOIN hdd_tipo ht ON ic.id_hdd_tipo = ht.id_hdd_tipo
            LEFT JOIN empleados emp ON TRIM(LEADING '0' FROM CAST(ic.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(emp.codigo AS CHAR))
            LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
            LEFT JOIN departamentos dep ON emp.id_departamento = dep.id_departamento
            LEFT JOIN puestos pue ON emp.id_puesto = pue.id_puesto
            LEFT JOIN condicion c ON ic.id_condicion = c.id_condicion
            LEFT JOIN renovacion r ON ic.id_renovacion = r.id_renovacion
            ORDER BY ic.id_cpu DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error CPUs: {e}")
        return pd.DataFrame()

def guardar_cpu(hostname, serie, marca, modelo, proc, ram, datos_ram, mobo, id_hdd_tipo, almac, datos_almac, so, mac_lan, mac_wlan, precio, id_condicion, id_renovacion, obs, com="", id_estatus=4):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            INSERT INTO inventario_cpu 
            (hostname, numero_serie, marca, modelo, procesador, memoria_ram, datos_memoria_ram, motherboard, id_hdd_tipo, almacenamiento, datos_almacenamiento, sistema_operativo, mac_address_lan, mac_address_wlan, precio, id_condicion, id_renovacion, observaciones, comentarios, id_estatus_cpu) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            hostname.strip(), limpiar_str_null(serie), marca.strip(), modelo.strip(), proc.strip(), ram.strip(), 
            limpiar_str_null(datos_ram), limpiar_str_null(mobo), id_hdd_tipo, almac.strip(), 
            limpiar_str_null(datos_almac), so.strip(), limpiar_str_null(mac_lan), limpiar_str_null(mac_wlan), 
            limpiar_int(precio, 0), id_condicion, id_renovacion, limpiar_str_null(obs), limpiar_str_null(com), id_estatus
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar CPU: {e}")
        return False

def actualizar_cpu(id_cpu, hostname, serie, marca, modelo, proc, ram, datos_ram, mobo, id_hdd_tipo, almac, datos_almac, so, mac_lan, mac_wlan, precio, id_condicion, id_renovacion, id_estatus, obs, com=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()

        query = """
            UPDATE inventario_cpu 
            SET hostname=%s, numero_serie=%s, marca=%s, modelo=%s, procesador=%s, memoria_ram=%s, datos_memoria_ram=%s, motherboard=%s, 
                id_hdd_tipo=%s, almacenamiento=%s, datos_almacenamiento=%s, sistema_operativo=%s, mac_address_lan=%s, mac_address_wlan=%s, 
                precio=%s, id_condicion=%s, id_renovacion=%s, id_estatus_cpu=%s, observaciones=%s, comentarios=%s 
            WHERE id_cpu=%s
        """
        cursor.execute(query, (
            hostname.strip(), limpiar_str_null(serie), marca.strip(), modelo.strip(), proc.strip(), ram.strip(), 
            limpiar_str_null(datos_ram), limpiar_str_null(mobo), id_hdd_tipo, almac.strip(), 
            limpiar_str_null(datos_almac), so.strip(), limpiar_str_null(mac_lan), limpiar_str_null(mac_wlan), 
            limpiar_int(precio, 0), id_condicion, id_renovacion, id_estatus, limpiar_str_null(obs), limpiar_str_null(com), int(id_cpu)
        ))

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
                im.numero_serie, im.hostname, im.marca, im.modelo, im.resolucion, im.precio,
                em.estatus_monitor AS estatus, im.id_estatus_monitor,
                COALESCE(CONCAT_WS(' ', emp.nombre, emp.apellido_paterno, emp.apellido_materno), 'VACANTE / SIN ASIGNAR') AS asignado_a,
                COALESCE(suc.nombre_sucursal, 'SIN SUCURSAL') AS sucursal,
                COALESCE(dep.nombre_departamento, 'SIN DEPARTAMENTO') AS departamento,
                COALESCE(pue.nombre_puesto, 'SIN PUESTO') AS puesto,
                c.condicion_opcion AS condicion, r.renovacion_opcion AS renovacion,
                im.observaciones, im.comentarios, im.id_condicion, im.id_renovacion
            FROM inventario_monitores im
            LEFT JOIN estatus_monitores em ON im.id_estatus_monitor = em.id_estatus_monitor
            LEFT JOIN empleados emp ON TRIM(LEADING '0' FROM CAST(im.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(emp.codigo AS CHAR))
            LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
            LEFT JOIN departamentos dep ON emp.id_departamento = dep.id_departamento
            LEFT JOIN puestos pue ON emp.id_puesto = pue.id_puesto
            LEFT JOIN condicion c ON im.id_condicion = c.id_condicion
            LEFT JOIN renovacion r ON im.id_renovacion = r.id_renovacion
            ORDER BY im.numero_serie DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error Monitores: {e}")
        return pd.DataFrame()

def guardar_monitor(serie, hostname, marca, modelo, resolucion, precio, id_condicion, id_renovacion, obs, com="", id_estatus=4):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            INSERT INTO inventario_monitores 
            (numero_serie, hostname, marca, modelo, resolucion, precio, id_condicion, id_renovacion, observaciones, comentarios, id_estatus_monitor) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            serie.strip(), limpiar_str_null(hostname), marca.strip(), modelo.strip(), 
            limpiar_str_null(resolucion), limpiar_int(precio, 0), id_condicion, id_renovacion, 
            limpiar_str_null(obs), limpiar_str_null(com), id_estatus
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar monitor: {e}")
        return False

def actualizar_monitor(serie_vieja, serie_nueva, hostname, marca, modelo, resolucion, precio, id_condicion, id_renovacion, id_estatus, obs, com=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        s_vieja = str(serie_vieja).strip()
        s_nueva = str(serie_nueva).strip()

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        query = """
            UPDATE inventario_monitores 
            SET numero_serie=%s, hostname=%s, marca=%s, modelo=%s, resolucion=%s, precio=%s, id_condicion=%s, id_renovacion=%s, id_estatus_monitor=%s, observaciones=%s, comentarios=%s 
            WHERE numero_serie=%s
        """
        cursor.execute(query, (
            s_nueva, limpiar_str_null(hostname), marca.strip(), modelo.strip(), limpiar_str_null(resolucion), 
            limpiar_int(precio, 0), id_condicion, id_renovacion, id_estatus, limpiar_str_null(obs), limpiar_str_null(com), s_vieja
        ))

        if s_vieja != s_nueva:
            cursor.execute("UPDATE responsivas_monitores SET numero_serie = %s WHERE numero_serie = %s", (s_nueva, s_vieja))

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
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
                it.numero_serie, it.imei, it.marca, it.modelo, it.mac_address, it.precio,
                et.estatus_tablet AS estatus, it.id_estatus_tablet,
                COALESCE(CONCAT_WS(' ', emp.nombre, emp.apellido_paterno, emp.apellido_materno), 'VACANTE / SIN ASIGNAR') AS asignado_a,
                COALESCE(suc.nombre_sucursal, 'SIN SUCURSAL') AS sucursal,
                COALESCE(dep.nombre_departamento, 'SIN DEPARTAMENTO') AS departamento,
                COALESCE(pue.nombre_puesto, 'SIN PUESTO') AS puesto,
                c.condicion_opcion AS condicion, cg.cargador_opcion AS cargador,
                it.observaciones, it.comentarios, it.id_condicion, it.id_cargador
            FROM inventario_tablets it
            LEFT JOIN estatus_tablets et ON it.id_estatus_tablet = et.id_estatus_tablet
            LEFT JOIN empleados emp ON TRIM(LEADING '0' FROM CAST(it.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(emp.codigo AS CHAR))
            LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
            LEFT JOIN departamentos dep ON emp.id_departamento = dep.id_departamento
            LEFT JOIN puestos pue ON emp.id_puesto = pue.id_puesto
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

def guardar_tablet(serie, imei, marca, modelo, mac, precio, id_condicion, id_cargador, obs, com="", id_estatus=4):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            INSERT INTO inventario_tablets 
            (numero_serie, imei, marca, modelo, mac_address, precio, id_condicion, id_cargador, observaciones, comentarios, id_estatus_tablet) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            serie.strip(), limpiar_str_null(imei), marca.strip(), modelo.strip(), 
            limpiar_str_null(mac), limpiar_int(precio, 0), id_condicion, id_cargador, 
            limpiar_str_null(obs), limpiar_str_null(com), id_estatus
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar tablet: {e}")
        return False

def actualizar_tablet(serie_vieja, serie_nueva, imei, marca, modelo, mac, precio, id_condicion, id_cargador, id_estatus, obs, com=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        s_vieja = str(serie_vieja).strip()
        s_nueva = str(serie_nueva).strip()

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        query = """
            UPDATE inventario_tablets 
            SET numero_serie=%s, imei=%s, marca=%s, modelo=%s, mac_address=%s, precio=%s, id_condicion=%s, id_cargador=%s, id_estatus_tablet=%s, observaciones=%s, comentarios=%s 
            WHERE numero_serie=%s
        """
        cursor.execute(query, (
            s_nueva, limpiar_str_null(imei), marca.strip(), modelo.strip(), limpiar_str_null(mac), 
            limpiar_int(precio, 0), id_condicion, id_cargador, id_estatus, limpiar_str_null(obs), limpiar_str_null(com), s_vieja
        ))

        if s_vieja != s_nueva:
            cursor.execute("UPDATE responsivas_tablets SET numero_serie = %s WHERE numero_serie = %s", (s_nueva, s_vieja))

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
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
        cursor.execute(q_red, (id_sucursal, tipo.strip(), marca.strip(), modelo.strip(), serie.strip(), mac_lan.strip(), limpiar_str_null(mac_wlan), ubicacion.strip()))
        id_disp = cursor.lastrowid

        if hostname.strip() or user_def.strip() or user_nuevo.strip():
            q_acc = "INSERT INTO dispositivos_accesos (id_dispositivo, hostname, usuario_admin_default, password_admin_default, nuevo_usuario, password_nuevo, puerto_admin) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(q_acc, (id_disp, hostname.strip(), user_def.strip() or None, pass_def.strip() or None, user_nuevo.strip() or None, pass_nuevo.strip() or None, str(puerto)))

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
        cursor.execute(q_red, (id_sucursal, tipo.strip(), marca.strip(), modelo.strip(), serie.strip(), mac_lan.strip(), limpiar_str_null(mac_wlan), ubicacion.strip(), id_dispositivo))

        if hostname.strip() or user_def.strip() or user_nuevo.strip():
            q_acc = "INSERT INTO dispositivos_accesos (id_dispositivo, hostname, usuario_admin_default, password_admin_default, nuevo_usuario, password_nuevo, puerto_admin) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE hostname=VALUES(hostname), usuario_admin_default=VALUES(usuario_admin_default), password_admin_default=VALUES(password_admin_default), nuevo_usuario=VALUES(nuevo_usuario), password_nuevo=VALUES(password_nuevo), puerto_admin=VALUES(puerto_admin);"
            cursor.execute(q_acc, (id_dispositivo, hostname.strip(), user_def.strip() or None, pass_def.strip() or None, user_nuevo.strip() or None, pass_nuevo.strip() or None, str(puerto)))

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
# AYUDANTE DE FILTRADO DINÁMICO
# ==============================================================================
def render_filtros_inventario(df_origen, key_prefix):
    col_id_unic = "imei" if "imei" in df_origen.columns else ("numero_serie" if "numero_serie" in df_origen.columns else ("hostname" if "hostname" in df_origen.columns else "id_dispositivo"))
    
    opts_autocompletar = [
        f"{r[col_id_unic]} | {r.get('marca_modelo', r.get('modelo', ''))} | {r.get('asignado_a', '')}"
        for _, r in df_origen.iterrows()
        if pd.notna(r[col_id_unic]) and str(r[col_id_unic]).strip() != ''
    ]

    c_auto, c_est = st.columns([2, 1])
    with c_auto:
        sel_auto = st.selectbox(
            f"🔍 Autocompletar por {'IMEI' if col_id_unic == 'imei' else ('Serie' if col_id_unic == 'numero_serie' else 'Hostname')}:",
            opts_autocompletar,
            index=None,
            placeholder=f"Teclea aquí para autocompletar...",
            key=f"auto_{key_prefix}"
        )
    with c_est:
        opts_est = ["Todos"] + sorted(list(df_origen["estatus"].dropna().unique()))
        est_sel = st.selectbox("Filtrar por Estatus:", opts_est, key=f"est_{key_prefix}")

    c_busq, f1, f2, f3 = st.columns([1.5, 1, 1, 1])
    with c_busq:
        txt_busq = st.text_input("Búsqueda libre:", placeholder="Ej. Juan, Morelia...", key=f"txt_{key_prefix}")
    with f1:
        opts_suc = ["Todas"] + sorted(list(df_origen["sucursal"].dropna().unique()))
        suc_sel = st.selectbox("Sucursal:", opts_suc, key=f"suc_{key_prefix}")
    with f2:
        opts_dep = ["Todos"] + sorted(list(df_origen["departamento"].dropna().unique()))
        dep_sel = st.selectbox("Departamento:", opts_dep, key=f"dep_{key_prefix}")
    with f3:
        opts_pue = ["Todos"] + sorted(list(df_origen["puesto"].dropna().unique()))
        pue_sel = st.selectbox("Puesto:", opts_pue, key=f"pue_{key_prefix}")

    df_filt = df_origen.copy()

    if sel_auto:
        id_buscado = sel_auto.split(" | ")[0].strip()
        df_filt = df_filt[df_filt[col_id_unic].astype(str).str.strip() == id_buscado]
        return df_filt

    if est_sel != "Todos":
        df_filt = df_filt[df_filt["estatus"] == est_sel]
    if suc_sel != "Todas":
        df_filt = df_filt[df_filt["sucursal"] == suc_sel]
    if dep_sel != "Todos":
        df_filt = df_filt[df_filt["departamento"] == dep_sel]
    if pue_sel != "Todos":
        df_filt = df_filt[df_filt["puesto"] == pue_sel]

    if txt_busq.strip():
        term = txt_busq.strip().lower()
        cols_a_buscar = [c for c in df_filt.columns if df_filt[c].dtype == object]
        mascara = pd.Series(False, index=df_filt.index)
        for col in cols_a_buscar:
            mascara |= df_filt[col].astype(str).str.lower().str.contains(term, na=False)
        df_filt = df_filt[mascara]

    return df_filt

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
    dict_renovaciones = obtener_catalogo_dict("renovacion", "id_renovacion", "renovacion_opcion")
    lista_lineas_disponibles = obtener_lista_lineas_telefonicas()

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
                df_filt_cel = render_filtros_inventario(df_cel, "cel_cg")
                df_view = df_filt_cel[["imei", "numero_linea", "marca_modelo", "estatus", "asignado_a", "sucursal", "departamento", "puesto", "observaciones", "comentarios"]]
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
                imei = c1.text_input("IMEI*:", placeholder="Ej. 863736063211028")
                serie = c1.text_input("Número de Serie (Opcional):", placeholder="Ej. 5RK0123456")
                mac = c1.text_input("MAC Wi-Fi (Opcional):", placeholder="Ej. 08:BF:B8:A6:F0:B6")
                
                # Desplegable de líneas telefónicas
                opciones_lineas_add = ["-- Sin Línea (Sin Asignar) --"] + lista_lineas_disponibles
                num_linea_sel = c1.selectbox("Línea Telefónica Asignada:", opciones_lineas_add, index=0)

                mod_sel = c2.selectbox("Modelo:", list(dict_mod.keys()))
                cond_sel = c2.selectbox("Condición:", list(dict_condiciones.keys()))
                carg_sel = c2.selectbox("Cargador:", list(dict_cargadores.keys()))
                caj_sel = c2.selectbox("Caja:", list(dict_cajas.keys()))
                obs = st.text_area("Observaciones (Diagnóstico/Baja):", placeholder="Ej. Teléfono de renovación anterior")
                com = st.text_area("Comentarios (Estatus físico - va al Word):", placeholder="Ej. Estética 9/10, sin rayones")

                if st.form_submit_button("💾 Guardar Celular", type="primary"):
                    val_imei = imei.strip()
                    if not val_imei:
                        st.warning("⚠️ El campo IMEI es obligatorio.")
                    elif existe_imei_celular(val_imei):
                        st.error(f"⛔ El IMEI `{val_imei}` ya existe en el inventario.")
                    else:
                        num_final = None if num_linea_sel == "-- Sin Línea (Sin Asignar) --" else num_linea_sel
                        ok, err_msg = guardar_celular(
                            imei=val_imei,
                            serie=serie,
                            mac=mac,
                            numero=num_final,
                            id_modelo=dict_mod[mod_sel],
                            id_condicion=dict_condiciones[cond_sel],
                            id_cargador=dict_cargadores[carg_sel],
                            id_caja=dict_cajas[caj_sel],
                            observaciones=obs,
                            comentarios=com
                        )
                        if ok:
                            notificar_exito(f"¡Celular IMEI {val_imei} dado de alta con éxito!")
                        else:
                            st.error(f"⛔ Error al guardar en base de datos: {err_msg}")

        with t3:
            if not df_cel.empty:
                opts_cel_ed = [
                    f"{r['imei']} | {r['marca_modelo']} | [{r['estatus']}] | {r['asignado_a']} ({r['sucursal']})"
                    for _, r in df_cel.iterrows()
                ]

                cel_sel = st.selectbox(
                    "Selecciona o teclea para buscar:",
                    opts_cel_ed,
                    index=None,
                    placeholder="🔍 Teclea aquí IMEI, Modelo, Empleado o Sucursal...",
                    key="sel_ed_cel_auto"
                )

                if cel_sel:
                    imei_ed = cel_sel.split(" | ")[0]
                    r = df_cel[df_cel["imei"] == imei_ed].iloc[0]
                    
                    st.divider()
                    with st.form(f"form_ed_cel_{imei_ed}"):
                        c1, c2 = st.columns(2)
                        e_imei_edit = c1.text_input("IMEI (Identificador):", value=str(r["imei"]))
                        e_ser = c1.text_input("Número de Serie:", value=limpiar_str_null(r["numero_serie"]) or "")
                        e_mac = c1.text_input("MAC Wi-Fi:", value=limpiar_str_null(r["mac_address"]) or "")

                        # Desplegable de líneas en edición
                        num_actual = limpiar_str_null(r["numero_linea"])
                        opciones_lineas_edit = ["-- Sin Línea (Sin Asignar) --"] + lista_lineas_disponibles
                        idx_linea_def = 0
                        if num_actual and num_actual in opciones_lineas_edit:
                            idx_linea_def = opciones_lineas_edit.index(num_actual)
                        elif num_actual:
                            opciones_lineas_edit.append(num_actual)
                            idx_linea_def = len(opciones_lineas_edit) - 1

                        e_num_sel = c1.selectbox("Línea Asignada:", opciones_lineas_edit, index=idx_linea_def)

                        e_est = c1.selectbox("Estatus:", list(dict_est.keys()), index=list(dict_est.keys()).index(r["estatus"]) if r["estatus"] in dict_est else 0)
                        e_mod = c2.selectbox("Modelo:", list(dict_mod.keys()), index=list(dict_mod.values()).index(r["id_modelo"]) if r["id_modelo"] in dict_mod.values() else 0)
                        e_cond = c2.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                        e_carg = c2.selectbox("Cargador:", list(dict_cargadores.keys()), index=list(dict_cargadores.values()).index(r["id_cargador"]) if r["id_cargador"] in dict_cargadores.values() else 0)
                        e_caj = c2.selectbox("Caja:", list(dict_cajas.keys()), index=list(dict_cajas.values()).index(r["id_caja"]) if r["id_caja"] in dict_cajas.values() else 0)
                        
                        e_obs = st.text_area("Observaciones (Diagnóstico/Baja):", value=limpiar_str_null(r["observaciones"]) or "")
                        e_com = st.text_area("Comentarios (Estatus físico - va al Word):", value=limpiar_str_null(r["comentarios"]) or "")
                        if st.form_submit_button("💾 Actualizar Celular", type="primary"):
                            val_imei_edit = e_imei_edit.strip()
                            if not val_imei_edit:
                                st.warning("⚠️ El IMEI no puede quedar vacío.")
                            else:
                                num_final_edit = None if e_num_sel == "-- Sin Línea (Sin Asignar) --" else e_num_sel
                                ok, err_up = actualizar_celular(
                                    imei_viejo=imei_ed,
                                    imei_nuevo=val_imei_edit,
                                    serie=e_ser,
                                    mac=e_mac,
                                    numero=num_final_edit,
                                    id_modelo=dict_mod[e_mod],
                                    id_condicion=dict_condiciones[e_cond],
                                    id_cargador=dict_cargadores[e_carg],
                                    id_caja=dict_cajas[e_caj],
                                    id_estatus=dict_est[e_est],
                                    observaciones=e_obs,
                                    comentarios=e_com
                                )
                                if ok:
                                    notificar_exito(f"¡Celular IMEI {val_imei_edit} actualizado correctamente!")
                                else:
                                    st.error(f"⛔ Error al actualizar: {err_up}")

    # --------------------------------------------------------------------------
    # 2. LAPTOPS
    # --------------------------------------------------------------------------
    with tab_lap:
        df_lap = obtener_laptops_df()
        dict_est_lap = obtener_catalogo_dict("estatus_laptops", "id_estatus_laptops", "estatus_laptop")
        t1, t2, t3 = st.tabs(["📋 Consulta General", "➕ Registrar Nuevo", "✏️ Editar / Modificar"])
        with t1:
            if not df_lap.empty:
                df_filt_lap = render_filtros_inventario(df_lap, "lap_cg")
                df_view = df_filt_lap[["numero_serie", "hostname", "marca", "modelo", "procesador", "memoria_ram", "datos_memoria_ram", "motherboard", "tipo_almacenamiento", "almacenamiento", "datos_almacenamiento", "sistema_operativo", "mac_address_lan", "mac_address_wlan", "precio", "estatus", "asignado_a", "sucursal", "departamento", "puesto", "observaciones", "comentarios"]]
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
                precio = c2.number_input("Precio Estimado ($):", min_value=0, value=0, step=500)
                
                c3, c4 = st.columns(2)
                cond_sel = c3.selectbox("Condición*:", list(dict_condiciones.keys()))
                carg_sel = c3.selectbox("Cargador Incluido*:", list(dict_cargadores.keys()))
                renov_sel_nom = c4.selectbox("¿Se debe renovar?", list(dict_renovaciones.keys()), index=0)
                
                obs = st.text_area("Observaciones (Diagnósticos/Bajas):")
                com = st.text_area("Comentarios (Estatus físico - va al Word):")
                if st.form_submit_button("💾 Guardar Laptop", type="primary"):
                    id_renov_val = dict_renovaciones[renov_sel_nom]
                    if serie and host and guardar_laptop(serie, host, marca, modelo, proc, ram, datos_ram, mobo, dict_hdd_tipos[hdd_sel], almac, datos_almac, so, mac_lan, mac_wlan, precio, dict_condiciones[cond_sel], dict_cargadores[carg_sel], id_renov_val, obs, com):
                        notificar_exito(f"¡Laptop Serie {serie} registrada con éxito!")
        with t3:
            if not df_lap.empty:
                opts_lap_ed = [
                    f"{r['numero_serie']} | {r['hostname']} ({r['marca']} {r['modelo']}) | [{r['estatus']}] | {r['asignado_a']} ({r['sucursal']})"
                    for _, r in df_lap.iterrows()
                ]

                lap_sel = st.selectbox(
                    "Selecciona o teclea para buscar:",
                    opts_lap_ed,
                    index=None,
                    placeholder="🔍 Teclea aquí Serie, Hostname, Marca, Empleado...",
                    key="sel_ed_lap_auto"
                )

                if lap_sel:
                    serie_ed = lap_sel.split(" | ")[0]
                    r = df_lap[df_lap["numero_serie"] == serie_ed].iloc[0]
                    
                    st.divider()
                    with st.form(f"form_ed_lap_{serie_ed}"):
                        c1, c2 = st.columns(2)
                        e_serie_edit = c1.text_input("Número de Serie (Identificador):", value=str(r["numero_serie"]))
                        e_host = c1.text_input("Hostname:", value=limpiar_str_null(r["hostname"]) or "")
                        e_marca = c1.text_input("Marca:", value=limpiar_str_null(r["marca"]) or "")
                        e_mod = c1.text_input("Modelo:", value=limpiar_str_null(r["modelo"]) or "")
                        e_proc = c1.text_input("Procesador:", value=limpiar_str_null(r["procesador"]) or "")
                        e_ram = c1.text_input("RAM Resumen:", value=limpiar_str_null(r["memoria_ram"]) or "")
                        e_datos_ram = c1.text_input("RAM Speccy:", value=limpiar_str_null(r["datos_memoria_ram"]) or "")
                        e_mobo = c1.text_input("Motherboard:", value=limpiar_str_null(r["motherboard"]) or "")
                        
                        e_hdd = c2.selectbox("Tipo Disco:", list(dict_hdd_tipos.keys()), index=list(dict_hdd_tipos.values()).index(r["id_hdd_tipo"]) if r["id_hdd_tipo"] in dict_hdd_tipos.values() else 0)
                        e_almac = c2.text_input("Almacenamiento Resumen:", value=limpiar_str_null(r["almacenamiento"]) or "")
                        e_datos_almac = c2.text_input("Almacenamiento Speccy:", value=limpiar_str_null(r["datos_almacenamiento"]) or "")
                        e_so = c2.text_input("S.O.:", value=limpiar_str_null(r["sistema_operativo"]) or "")
                        e_maclan = c2.text_input("MAC LAN:", value=limpiar_str_null(r["mac_address_lan"]) or "")
                        e_macwlan = c2.text_input("MAC Wi-Fi:", value=limpiar_str_null(r["mac_address_wlan"]) or "")
                        e_precio = c2.number_input("Precio ($):", value=limpiar_int(r["precio"], 0), step=500)
                        
                        c3, c4 = st.columns(2)
                        e_cond = c3.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                        e_carg = c3.selectbox("Cargador:", list(dict_cargadores.keys()), index=list(dict_cargadores.values()).index(r["id_cargador"]) if r["id_cargador"] in dict_cargadores.values() else 0)
                        e_est = c4.selectbox("Estatus Laptop:", list(dict_est_lap.keys()), index=list(dict_est_lap.keys()).index(r["estatus"]) if r["estatus"] in dict_est_lap else 0)
                        
                        idx_renov = list(dict_renovaciones.values()).index(r["id_renovacion"]) if r["id_renovacion"] in dict_renovaciones.values() else 0
                        e_renov_nom = c4.selectbox("¿Se debe renovar?", list(dict_renovaciones.keys()), index=idx_renov)

                        e_obs = st.text_area("Observaciones (Diagnósticos/Bajas):", value=limpiar_str_null(r["observaciones"]) or "")
                        e_com = st.text_area("Comentarios (Estatus físico - va al Word):", value=limpiar_str_null(r["comentarios"]) or "")
                        if st.form_submit_button("💾 Actualizar Laptop", type="primary"):
                            id_renov_edit_val = dict_renovaciones[e_renov_nom]
                            if actualizar_laptop(serie_ed, e_serie_edit, e_host, e_marca, e_mod, e_proc, e_ram, e_datos_ram, e_mobo, dict_hdd_tipos[e_hdd], e_almac, e_datos_almac, e_so, e_maclan, e_macwlan, e_precio, dict_condiciones[e_cond], dict_cargadores[e_carg], id_renov_edit_val, dict_est_lap[e_est], e_obs, e_com):
                                notificar_exito(f"¡Laptop Serie {e_serie_edit} actualizada correctamente!")

    # --------------------------------------------------------------------------
    # 3. CPUS
    # --------------------------------------------------------------------------
    with tab_cpu:
        df_cpu = obtener_cpus_df()
        dict_est_cpu = obtener_catalogo_dict("estatus_cpu", "id_estatus_cpu", "estatus_cpu")
        t1, t2, t3 = st.tabs(["📋 Consulta General", "➕ Registrar Nuevo", "✏️ Editar / Modificar"])
        with t1:
            if not df_cpu.empty:
                df_filt_cpu = render_filtros_inventario(df_cpu, "cpu_cg")
                df_view = df_filt_cpu[["id_cpu", "hostname", "numero_serie", "marca", "modelo", "procesador", "memoria_ram", "motherboard", "tipo_almacenamiento", "almacenamiento", "sistema_operativo", "precio", "estatus", "asignado_a", "sucursal", "departamento", "puesto", "observaciones", "comentarios"]]
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
                serie = c1.text_input("Número de Serie (Opcional):")
                marca = c1.text_input("Marca*:")
                modelo = c1.text_input("Modelo*:")
                proc = c1.text_input("Procesador*:")
                ram = c1.text_input("RAM Resumen (ej. 8 GB)*:")
                datos_ram = c1.text_input("RAM Speccy:")
                mobo = c1.text_input("Motherboard (ej. Asus Prime H110M):")

                hdd_sel = c2.selectbox("Tipo Disco:", list(dict_hdd_tipos.keys()))
                almac = c2.text_input("Almacenamiento Resumen (ej. 240 GB)*:")
                datos_almac = c2.text_input("Almacenamiento Speccy:")
                so = c2.text_input("S.O.*:", value="Windows 11 Pro")
                mac_lan = c2.text_input("MAC LAN:")
                mac_wlan = c2.text_input("MAC Wi-Fi:")
                precio = c2.number_input("Precio Estimado ($):", min_value=0, value=0, step=500)

                c3, c4 = st.columns(2)
                cond_sel = c3.selectbox("Condición:", list(dict_condiciones.keys()))
                renov_sel_nom = c4.selectbox("¿Se debe renovar?", list(dict_renovaciones.keys()), index=0)

                obs = st.text_area("Observaciones (Diagnóstico/Baja):")
                com = st.text_area("Comentarios (Estatus físico - va al Word):")
                if st.form_submit_button("💾 Guardar CPU", type="primary"):
                    id_renov_val = dict_renovaciones[renov_sel_nom]
                    if host and guardar_cpu(host, serie, marca, modelo, proc, ram, datos_ram, mobo, dict_hdd_tipos[hdd_sel], almac, datos_almac, so, mac_lan, mac_wlan, precio, dict_condiciones[cond_sel], id_renov_val, obs, com):
                        notificar_exito(f"¡CPU Hostname {host} registrado con éxito!")
        with t3:
            if not df_cpu.empty:
                opts_cpu_ed = [
                    f"ID: {r['id_cpu']} | {r['hostname']} ({r['marca']} {r['modelo']}) | [{r['estatus']}] | {r['asignado_a']} ({r['sucursal']})"
                    for _, r in df_cpu.iterrows()
                ]

                cpu_sel = st.selectbox(
                    "Selecciona o teclea para buscar:",
                    opts_cpu_ed,
                    index=None,
                    placeholder="🔍 Teclea aquí Hostname, Serie, Empleado...",
                    key="sel_ed_cpu_auto"
                )

                if cpu_sel:
                    id_cpu_ed = int(cpu_sel.split(" | ")[0].replace("ID: ", ""))
                    r = df_cpu[df_cpu["id_cpu"] == id_cpu_ed].iloc[0]
                    
                    st.divider()
                    with st.form(f"form_ed_cpu_{id_cpu_ed}"):
                        c1, c2 = st.columns(2)
                        e_host = c1.text_input("Hostname:", value=limpiar_str_null(r["hostname"]) or "")
                        e_ser = c1.text_input("Número de Serie:", value=limpiar_str_null(r["numero_serie"]) or "")
                        e_marca = c1.text_input("Marca:", value=limpiar_str_null(r["marca"]) or "")
                        e_mod = c1.text_input("Modelo:", value=limpiar_str_null(r["modelo"]) or "")
                        e_proc = c1.text_input("Procesador:", value=limpiar_str_null(r["procesador"]) or "")
                        e_ram = c1.text_input("RAM Resumen:", value=limpiar_str_null(r["memoria_ram"]) or "")
                        e_datos_ram = c1.text_input("RAM Speccy:", value=limpiar_str_null(r["datos_memoria_ram"]) or "")
                        e_mobo = c1.text_input("Motherboard:", value=limpiar_str_null(r["motherboard"]) or "")
                        
                        e_hdd = c2.selectbox("Tipo Disco:", list(dict_hdd_tipos.keys()), index=list(dict_hdd_tipos.values()).index(r["id_hdd_tipo"]) if r["id_hdd_tipo"] in dict_hdd_tipos.values() else 0)
                        e_almac = c2.text_input("Almacenamiento Resumen:", value=limpiar_str_null(r["almacenamiento"]) or "")
                        e_datos_almac = c2.text_input("Almacenamiento Speccy:", value=limpiar_str_null(r["datos_almacenamiento"]) or "")
                        e_so = c2.text_input("S.O.:", value=limpiar_str_null(r["sistema_operativo"]) or "")
                        e_maclan = c2.text_input("MAC LAN:", value=limpiar_str_null(r["mac_address_lan"]) or "")
                        e_macwlan = c2.text_input("MAC Wi-Fi:", value=limpiar_str_null(r["mac_address_wlan"]) or "")
                        e_precio = c2.number_input("Precio ($):", value=limpiar_int(r["precio"], 0), step=500)
                        
                        c3, c4 = st.columns(2)
                        e_cond = c3.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                        idx_renov_cpu = list(dict_renovaciones.values()).index(r["id_renovacion"]) if r["id_renovacion"] in dict_renovaciones.values() else 0
                        e_renov_nom = c3.selectbox("¿Se debe renovar?", list(dict_renovaciones.keys()), index=idx_renov_cpu)
                        e_est = c4.selectbox("Estatus CPU:", list(dict_est_cpu.keys()), index=list(dict_est_cpu.keys()).index(r["estatus"]) if r["estatus"] in dict_est_cpu else 0)
                        
                        e_obs = st.text_area("Observaciones (Diagnóstico/Baja):", value=limpiar_str_null(r["observaciones"]) or "")
                        e_com = st.text_area("Comentarios (Estatus físico - va al Word):", value=limpiar_str_null(r["comentarios"]) or "")
                        if st.form_submit_button("💾 Actualizar CPU", type="primary"):
                            id_renov_edit_val = dict_renovaciones[e_renov_nom]
                            if actualizar_cpu(id_cpu_ed, e_host, e_ser, e_marca, e_mod, e_proc, e_ram, e_datos_ram, e_mobo, dict_hdd_tipos[e_hdd], e_almac, e_datos_almac, e_so, e_maclan, e_macwlan, e_precio, dict_condiciones[e_cond], id_renov_edit_val, dict_est_cpu[e_est], e_obs, e_com):
                                notificar_exito(f"¡CPU Hostname {e_host} (ID {id_cpu_ed}) actualizado correctamente!")

    # --------------------------------------------------------------------------
    # 4. MONITORES
    # --------------------------------------------------------------------------
    with tab_mon:
        df_mon = obtener_monitores_df()
        dict_est_mon = obtener_catalogo_dict("estatus_monitores", "id_estatus_monitor", "estatus_monitor")
        t1, t2, t3 = st.tabs(["📋 Consulta General", "➕ Registrar Nuevo", "✏️ Editar / Modificar"])
        with t1:
            if not df_mon.empty:
                df_filt_mon = render_filtros_inventario(df_mon, "mon_cg")
                df_view = df_filt_mon[["numero_serie", "hostname", "marca", "modelo", "resolucion", "precio", "estatus", "asignado_a", "sucursal", "departamento", "puesto", "observaciones", "comentarios"]]
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
                precio = c2.number_input("Precio Estimado ($):", min_value=0, value=0, step=200)

                c3, c4 = st.columns(2)
                cond_sel = c3.selectbox("Condición:", list(dict_condiciones.keys()))
                renov_sel_nom = c4.selectbox("¿Se debe renovar?", list(dict_renovaciones.keys()), index=0)

                obs = st.text_area("Observaciones (Diagnóstico/Baja):")
                com = st.text_area("Comentarios (Estatus físico - va al Word):")
                if st.form_submit_button("💾 Guardar Monitor", type="primary"):
                    id_renov_val = dict_renovaciones[renov_sel_nom]
                    if serie and guardar_monitor(serie, host, marca, modelo, resol, precio, dict_condiciones[cond_sel], id_renov_val, obs, com):
                        notificar_exito(f"¡Monitor Serie {serie} registrado con éxito!")
        with t3:
            if not df_mon.empty:
                opts_mon_ed = [
                    f"{r['numero_serie']} | {r['marca']} {r['modelo']} | [{r['estatus']}] | {r['asignado_a']} ({r['sucursal']})"
                    for _, r in df_mon.iterrows()
                ]

                mon_sel = st.selectbox(
                    "Selecciona o teclea para buscar:",
                    opts_mon_ed,
                    index=None,
                    placeholder="🔍 Teclea aquí Serie, Marca, Empleado...",
                    key="sel_ed_mon_auto"
                )

                if mon_sel:
                    serie_ed = mon_sel.split(" | ")[0]
                    r = df_mon[df_mon["numero_serie"] == serie_ed].iloc[0]
                    
                    st.divider()
                    with st.form(f"form_ed_mon_{serie_ed}"):
                        c1, c2 = st.columns(2)
                        e_serie_edit = c1.text_input("Número de Serie (Identificador):", value=str(r["numero_serie"]))
                        e_host = c1.text_input("Hostname:", value=limpiar_str_null(r["hostname"]) or "")
                        e_marca = c1.text_input("Marca:", value=limpiar_str_null(r["marca"]) or "")
                        e_mod = c2.text_input("Modelo:", value=limpiar_str_null(r["modelo"]) or "")
                        e_resol = c2.text_input("Resolución:", value=limpiar_str_null(r["resolucion"]) or "")
                        e_precio = c2.number_input("Precio ($):", value=limpiar_int(r["precio"], 0), step=200)

                        c3, c4 = st.columns(2)
                        e_cond = c3.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                        idx_renov_mon = list(dict_renovaciones.values()).index(r["id_renovacion"]) if r["id_renovacion"] in dict_renovaciones.values() else 0
                        e_renov_nom = c3.selectbox("¿Se debe renovar?", list(dict_renovaciones.keys()), index=idx_renov_mon)
                        e_est = c4.selectbox("Estatus Monitor:", list(dict_est_mon.keys()), index=list(dict_est_mon.keys()).index(r["estatus"]) if r["estatus"] in dict_est_mon else 0)
                        
                        e_obs = st.text_area("Observaciones (Diagnóstico/Baja):", value=limpiar_str_null(r["observaciones"]) or "")
                        e_com = st.text_area("Comentarios (Estatus físico - va al Word):", value=limpiar_str_null(r["comentarios"]) or "")
                        if st.form_submit_button("💾 Actualizar Monitor", type="primary"):
                            id_renov_edit_val = dict_renovaciones[e_renov_nom]
                            if actualizar_monitor(serie_ed, e_serie_edit, e_host, e_marca, e_mod, e_resol, e_precio, dict_condiciones[e_cond], id_renov_edit_val, dict_est_mon[e_est], e_obs, e_com):
                                notificar_exito(f"¡Monitor Serie {e_serie_edit} actualizado correctamente!")

    # --------------------------------------------------------------------------
    # 5. TABLETS
    # --------------------------------------------------------------------------
    with tab_tab:
        df_tab = obtener_tablets_df()
        dict_est_tab = obtener_catalogo_dict("estatus_tablets", "id_estatus_tablet", "estatus_tablet")
        t1, t2, t3 = st.tabs(["📋 Consulta General", "➕ Registrar Nuevo", "✏️ Editar / Modificar"])
        with t1:
            if not df_tab.empty:
                df_filt_tab = render_filtros_inventario(df_tab, "tab_cg")
                df_view = df_filt_tab[["numero_serie", "imei", "marca", "modelo", "mac_address", "precio", "estatus", "asignado_a", "sucursal", "departamento", "puesto", "observaciones", "comentarios"]]
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
                precio = c2.number_input("Precio Estimado ($):", min_value=0, value=0, step=300)

                c3, c4 = st.columns(2)
                cond_sel = c3.selectbox("Condición:", list(dict_condiciones.keys()))
                carg_sel = c4.selectbox("Cargador:", list(dict_cargadores.keys()))

                obs = st.text_area("Observaciones (Diagnóstico/Baja):")
                com = st.text_area("Comentarios (Estatus físico - va al Word):")
                if st.form_submit_button("💾 Guardar Tablet", type="primary"):
                    if serie and guardar_tablet(serie, imei, marca, modelo, mac, precio, dict_condiciones[cond_sel], dict_cargadores[carg_sel], obs, com):
                        notificar_exito(f"¡Tablet Serie {serie} registrada con éxito!")
        with t3:
            if not df_tab.empty:
                opts_tab_ed = [
                    f"{r['numero_serie']} | IMEI: {r['imei'] or 'S/I'} ({r['marca']} {r['modelo']}) | [{r['estatus']}] | {r['asignado_a']} ({r['sucursal']})"
                    for _, r in df_tab.iterrows()
                ]

                tab_sel = st.selectbox(
                    "Selecciona o teclea para buscar:",
                    opts_tab_ed,
                    index=None,
                    placeholder="🔍 Teclea aquí Serie, IMEI, Marca, Empleado...",
                    key="sel_ed_tab_auto"
                )

                if tab_sel:
                    serie_ed = tab_sel.split(" | ")[0]
                    r = df_tab[df_tab["numero_serie"] == serie_ed].iloc[0]
                    
                    st.divider()
                    with st.form(f"form_ed_tab_{serie_ed}"):
                        c1, c2 = st.columns(2)
                        e_serie_edit = c1.text_input("Número de Serie (Identificador):", value=str(r["numero_serie"]))
                        e_imei = c1.text_input("IMEI:", value=limpiar_str_null(r["imei"]) or "")
                        e_marca = c1.text_input("Marca:", value=limpiar_str_null(r["marca"]) or "")
                        e_mod = c2.text_input("Modelo:", value=limpiar_str_null(r["modelo"]) or "")
                        e_mac = c2.text_input("MAC Wi-Fi:", value=limpiar_str_null(r["mac_address"]) or "")
                        e_precio = c2.number_input("Precio ($):", value=limpiar_int(r["precio"], 0), step=300)

                        c3, c4 = st.columns(2)
                        e_cond = c3.selectbox("Condición:", list(dict_condiciones.keys()), index=list(dict_condiciones.values()).index(r["id_condicion"]) if r["id_condicion"] in dict_condiciones.values() else 0)
                        e_carg = c4.selectbox("Cargador:", list(dict_cargadores.keys()), index=list(dict_cargadores.values()).index(r["id_cargador"]) if r["id_cargador"] in dict_cargadores.values() else 0)
                        e_est = c4.selectbox("Estatus Tablet:", list(dict_est_tab.keys()), index=list(dict_est_tab.keys()).index(r["estatus"]) if r["estatus"] in dict_est_tab else 0)
                        
                        e_obs = st.text_area("Observaciones (Diagnóstico/Baja):", value=limpiar_str_null(r["observaciones"]) or "")
                        e_com = st.text_area("Comentarios (Estatus físico - va al Word):", value=limpiar_str_null(r["comentarios"]) or "")
                        if st.form_submit_button("💾 Actualizar Tablet", type="primary"):
                            if actualizar_tablet(serie_ed, e_serie_edit, e_imei, e_marca, e_mod, e_mac, e_precio, dict_condiciones[e_cond], dict_cargadores[e_carg], dict_est_tab[e_est], e_obs, e_com):
                                notificar_exito(f"¡Tablet Serie {e_serie_edit} actualizada correctamente!")

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
                opts_red_ed = [
                    f"{r['id_dispositivo']} | [{r['tipo']}] {r['marca']} {r['modelo']} (Host: {r['hostname'] or 'S/H'}) | {r['sucursal']}"
                    for _, r in df_red.iterrows()
                ]

                red_sel = st.selectbox(
                    "Selecciona o teclea para buscar:",
                    opts_red_ed,
                    index=None,
                    placeholder="🔍 Teclea aquí Hostname, Tipo, Marca, Sucursal...",
                    key="sel_ed_red_auto"
                )

                if red_sel:
                    id_red_ed = int(red_sel.split(" | ")[0])
                    r = df_red[df_red["id_dispositivo"] == id_red_ed].iloc[0]
                    
                    st.divider()
                    with st.form(f"form_ed_red_{id_red_ed}"):
                        c1, c2 = st.columns(2)
                        e_suc = c1.selectbox("Sucursal:", list(dict_sucursales.keys()), index=list(dict_sucursales.values()).index(r["id_sucursal"]) if r["id_sucursal"] in dict_sucursales.values() else 0)
                        e_tipo = c1.text_input("Tipo:", value=limpiar_str_null(r["tipo"]) or "")
                        e_marca = c1.text_input("Marca:", value=limpiar_str_null(r["marca"]) or "")
                        e_mod = c1.text_input("Modelo:", value=limpiar_str_null(r["modelo"]) or "")
                        e_ser = c2.text_input("Serie:", value=limpiar_str_null(r["numero_serie"]) or "")
                        e_maclan = c2.text_input("MAC LAN:", value=limpiar_str_null(r["mac_address_lan"]) or "")
                        e_macwlan = c2.text_input("MAC WLAN:", value=limpiar_str_null(r["mac_address_wlan"]) or "")
                        e_ubic = c2.text_input("Ubicación Física:", value=limpiar_str_null(r["ubicacion_fisica"]) or "")
                        st.markdown("---")
                        c3, c4 = st.columns(2)
                        e_host = c3.text_input("Hostname:", value=limpiar_str_null(r["hostname"]) or "")
                        e_udef = c3.text_input("User Def:", value=limpiar_str_null(r["usuario_admin_default"]) or "")
                        e_pdef = c3.text_input("Pass Def:", value=limpiar_str_null(r["password_admin_default"]) or "", type="password")
                        e_unuev = c4.text_input("User Admin Nuevo:", value=limpiar_str_null(r["nuevo_usuario"]) or "")
                        e_pnuev = c4.text_input("Pass Admin Nuevo:", value=limpiar_str_null(r["password_nuevo"]) or "", type="password")
                        e_puer = c4.number_input("Puerto Admin:", value=int(r["puerto_admin"] or 80))
                        st.markdown("---")
                        c5, c6 = st.columns(2)
                        e_ssid = c5.text_input("SSID Wi-Fi:", value=limpiar_str_null(r["ssid"]) or "")
                        e_wpa = c5.selectbox("Modo WPA:", ["WPA2-PSK", "WPA3-PSK", "OPEN"], index=0)
                        e_pwpa = c6.text_input("Clave Wi-Fi:", value=limpiar_str_null(r["password_wpa"]) or "", type="password")
                        if st.form_submit_button("💾 Actualizar Equipo de Red", type="primary"):
                            if actualizar_dispositivo_red(id_red_ed, dict_sucursales[e_suc], e_tipo, e_marca, e_mod, e_ser, e_maclan, e_macwlan, e_ubic, e_host, e_udef, e_pdef, e_unuev, e_pnuev, e_puer, e_ssid, e_wpa, e_pwpa):
                                notificar_exito(f"¡Dispositivo ID {id_red_ed} actualizado correctamente!")

render_inventario = render