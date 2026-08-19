import io
import os
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from docxtpl import DocxTemplate
from num2words import num2words
from database import obtener_conexion

# Cargar variables de entorno para las rutas de plantillas
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

DIR_PLANTILLAS = Path(os.getenv("DIR_PLANTILLAS", "."))

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

# ==============================================================================
# 1. FUNCIONES DE FORMATEO Y AYUDANTES
# ==============================================================================
def limpiar_str(val, defecto=""):
    """Elimina valores NaN, None o cadenas 'nan' de Pandas antes de enviarlos a Word o a la UI."""
    if val is None or pd.isna(val):
        return defecto
    v_str = str(val).strip()
    if v_str.lower() in ["", "nan", "none", "null", "<na>"]:
        return defecto
    return v_str

def format_fecha(fecha_raw):
    if isinstance(fecha_raw, str):
        try:
            fecha_raw = pd.to_datetime(fecha_raw)
        except:
            return "Sin fecha"
    if pd.isna(fecha_raw) or fecha_raw is None:
        fecha_raw = datetime.now()
        
    DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", 
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    
    nombre_dia = DIAS[fecha_raw.weekday()]
    nombre_mes = MESES[fecha_raw.month - 1]
    return f"{nombre_dia} {fecha_raw.day} de {nombre_mes} de {fecha_raw.year}".capitalize()

def formatear_precio(precio_raw):
    if pd.isna(precio_raw) or precio_raw is None:
        return "0"
    try:
        precio_entero = int(float(precio_raw))
        return f"{precio_entero:,}"
    except:
        return "0"

def precio_a_letras(precio_raw):
    if pd.isna(precio_raw) or precio_raw is None:
        return "CERO PESOS 00/100 M.N."
    try:
        precio_entero = int(float(precio_raw))
        letras = num2words(precio_entero, lang='es')
        return f"{letras} pesos 00/100 m.n.".upper()
    except:
        return "CERO PESOS 00/100 M.N."

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

# ==============================================================================
# 2. CONSULTAS DE DATOS DE BDD
# ==============================================================================
def obtener_empleados_activos_df():
    try:
        conn = obtener_conexion()
        query = """
            SELECT 
                e.codigo,
                CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS nombre_completo,
                COALESCE(s.nombre_sucursal, 'SIN SUCURSAL') AS sucursal,
                COALESCE(d.nombre_departamento, 'SIN DEPARTAMENTO') AS departamento,
                COALESCE(p.nombre_puesto, 'SIN PUESTO') AS puesto,
                ce.correo_gmail,
                ce.correo_corporativo
            FROM empleados e
            LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
            LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento
            LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
            LEFT JOIN (
                SELECT 
                    TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) AS cod_clean,
                    MAX(CASE WHEN id_tipo_correo = 2 THEN direccion_correo END) AS correo_gmail,
                    MAX(CASE WHEN id_tipo_correo = 1 THEN direccion_correo END) AS correo_corporativo
                FROM correos_electronicos
                WHERE id_estatus_correo = 1
                GROUP BY cod_clean
            ) ce ON TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR)) = ce.cod_clean
            WHERE e.id_estatus_empleado = 1
            ORDER BY nombre_completo ASC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        df["codigo_str"] = df["codigo"].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"⚠️ Error al cargar empleados: {e}")
        return pd.DataFrame()

def obtener_equipos_disponibles():
    equipos = {"celulares": [], "laptops": [], "cpus": [], "monitores": [], "tablets": []}
    conn = obtener_conexion()
    if not conn:
        return equipos

    try:
        # 1. Celulares
        df_cel = pd.read_sql("""
            SELECT ic.imei, ic.numero, ic.numero_serie, m.marca_modelo AS equipo, COALESCE(m.precio, 0) AS precio, 
                   ic.id_condicion, c.condicion_opcion AS condicion, 
                   ic.id_cargador, ca.cargador_opcion AS cargador, 
                   ic.id_caja, caja.caja_opcion AS caja,
                   ic.id_estatus_celular, 
                   COALESCE(lt.gb_promocion_2026, lt.gb_2026, '') AS gb, 
                   COALESCE(ic.observaciones, '') AS observaciones, 
                   COALESCE(ic.comentarios, '') AS comentarios
            FROM inventario_celulares ic
            LEFT JOIN modelos_celulares m ON ic.id_modelo = m.id_modelo
            LEFT JOIN condicion c ON ic.id_condicion = c.id_condicion
            LEFT JOIN cargadores ca ON ic.id_cargador = ca.id_cargador
            LEFT JOIN caja ON ic.id_caja = caja.id_caja
            LEFT JOIN lineas_telefonicas lt ON ic.numero = lt.numero
            WHERE ic.id_estatus_celular = 4 
              AND (lt.id_estatus_linea IS NULL OR lt.id_estatus_linea != 5)
        """, conn)
        for _, r in df_cel.iterrows():
            obs_clean = limpiar_str(r['observaciones'])
            obs_txt = f" | Obs: {obs_clean}" if obs_clean else ""
            num_clean = limpiar_str(r['numero']) or 'S/N'
            lbl = f"IMEI: {r['imei']} - {r['equipo']} (Línea: {num_clean}){obs_txt}"
            equipos["celulares"].append({"id": r['imei'], "label": lbl, "data": r.to_dict()})

        # 2. Laptops
        df_lap = pd.read_sql("""
            SELECT il.numero_serie, il.marca, il.modelo, il.hostname, 
                   il.procesador, il.memoria_ram, ht.hdd_opcion AS tipo_hdd, il.almacenamiento,
                   COALESCE(il.observaciones, '') AS observaciones, 
                   COALESCE(il.comentarios, '') AS comentarios, 
                   il.id_condicion, con.condicion_opcion AS condicion_lap, 
                   il.id_cargador, car.cargador_opcion AS cargador, 
                   il.id_estatus_laptops, COALESCE(il.precio, 0) AS precio
            FROM inventario_laptops il
            LEFT JOIN hdd_tipo ht ON il.id_hdd_tipo = ht.id_hdd_tipo
            LEFT JOIN condicion con ON il.id_condicion = con.id_condicion
            LEFT JOIN cargadores car ON il.id_cargador = car.id_cargador
            WHERE il.id_estatus_laptops = 4
        """, conn)
        for _, r in df_lap.iterrows():
            obs_clean = limpiar_str(r['observaciones'])
            obs_txt = f" | Obs: {obs_clean}" if obs_clean else ""
            lbl = f"Serie: {r['numero_serie']} - {r['marca']} {r['modelo']} [{r['hostname']}]{obs_txt}"
            equipos["laptops"].append({"id": r['numero_serie'], "label": lbl, "data": r.to_dict()})

        # 3. CPUs
        df_cpu = pd.read_sql("""
            SELECT icp.id_cpu, icp.hostname, icp.marca, icp.modelo, icp.numero_serie, icp.procesador, icp.memoria_ram, icp.almacenamiento, 
                   thd.hdd_opcion AS tipo_hdd, icp.id_condicion, con.condicion_opcion AS condicion, 
                   icp.id_estatus_cpu, 
                   COALESCE(icp.observaciones, '') AS observaciones, 
                   COALESCE(icp.comentarios, '') AS comentarios, 
                   COALESCE(icp.precio, 0) AS precio
            FROM inventario_cpu icp
            LEFT JOIN hdd_tipo thd ON icp.id_hdd_tipo = thd.id_hdd_tipo
            LEFT JOIN condicion con ON icp.id_condicion = con.id_condicion
            WHERE icp.id_estatus_cpu = 4
        """, conn)
        for _, r in df_cpu.iterrows():
            obs_clean = limpiar_str(r['observaciones'])
            obs_txt = f" | Obs: {obs_clean}" if obs_clean else ""
            lbl = f"ID: {r['id_cpu']} | Host: {r['hostname']} ({r['marca']} {r['modelo']}){obs_txt}"
            equipos["cpus"].append({"id": r['id_cpu'], "label": lbl, "data": r.to_dict()})

        # 4. Monitores
        df_mon = pd.read_sql("""
            SELECT imon.numero_serie, imon.marca, imon.modelo, imon.id_condicion, con.condicion_opcion AS condicion,
                   imon.id_estatus_monitor, 
                   COALESCE(imon.observaciones, '') AS observaciones, 
                   COALESCE(imon.comentarios, '') AS comentarios, 
                   COALESCE(imon.precio, 0) AS precio
            FROM inventario_monitores imon
            LEFT JOIN condicion con ON imon.id_condicion = con.id_condicion
            WHERE imon.id_estatus_monitor = 4
        """, conn)
        for _, r in df_mon.iterrows():
            obs_clean = limpiar_str(r['observaciones'])
            obs_txt = f" | Obs: {obs_clean}" if obs_clean else ""
            lbl = f"Serie: {r['numero_serie']} - {r['marca']} {r['modelo']}{obs_txt}"
            equipos["monitores"].append({"id": r['numero_serie'], "label": lbl, "data": r.to_dict()})

        # 5. Tablets
        df_tab = pd.read_sql("""
            SELECT itab.numero_serie, itab.imei, itab.marca, itab.modelo, 
                   itab.id_condicion, con.condicion_opcion AS condicion, 
                   itab.id_cargador, car.cargador_opcion AS cargador, 
                   itab.id_estatus_tablet, 
                   COALESCE(itab.observaciones, '') AS observaciones, 
                   COALESCE(itab.comentarios, '') AS comentarios, 
                   COALESCE(itab.precio, 0) AS precio
            FROM inventario_tablets itab
            LEFT JOIN condicion con ON itab.id_condicion = con.id_condicion
            LEFT JOIN cargadores car ON itab.id_cargador = car.id_cargador
            WHERE itab.id_estatus_tablet = 4
        """, conn)
        for _, r in df_tab.iterrows():
            obs_clean = limpiar_str(r['observaciones'])
            obs_txt = f" | Obs: {obs_clean}" if obs_clean else ""
            lbl = f"Serie: {r['numero_serie']} - {r['marca']} {r['modelo']}{obs_txt}"
            equipos["tablets"].append({"id": r['numero_serie'], "label": lbl, "data": r.to_dict()})

    except Exception as e:
        st.error(f"⚠️ Error al consultar inventario: {e}")
    finally:
        conn.close()

    return equipos

def obtener_hardware_asignado_desvinculacion_df():
    """Consulta modularmente los equipos asignados para evitar errores de colación en MariaDB."""
    conn = obtener_conexion()
    if not conn:
        return pd.DataFrame()

    try:
        q_cel = """
            SELECT 'celular' AS tipo, ic.imei AS id, ic.numero_serie, CONCAT(COALESCE(m.marca_modelo, 'Celular'), ' (IMEI: ', ic.imei, ')') AS descripcion, 
                   CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS asignado_a, ic.codigo_empleado
            FROM inventario_celulares ic
            JOIN empleados e ON TRIM(LEADING '0' FROM CAST(ic.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR))
            LEFT JOIN modelos_celulares m ON ic.id_modelo = m.id_modelo
            WHERE ic.id_estatus_celular = 3
        """
        q_lap = """
            SELECT 'laptop' AS tipo, il.numero_serie AS id, il.numero_serie, CONCAT(COALESCE(il.marca, ''), ' ', COALESCE(il.modelo, ''), ' [', COALESCE(il.hostname, ''), ']') AS descripcion, 
                   CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS asignado_a, il.codigo_empleado
            FROM inventario_laptops il
            JOIN empleados e ON TRIM(LEADING '0' FROM CAST(il.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR))
            WHERE il.id_estatus_laptops = 3
        """
        q_cpu = """
            SELECT 'cpu' AS tipo, CAST(icp.id_cpu AS CHAR) AS id, icp.numero_serie, CONCAT('CPU ', COALESCE(icp.marca, ''), ' ', COALESCE(icp.modelo, ''), ' [', COALESCE(icp.hostname, ''), ']') AS descripcion, 
                   CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS asignado_a, icp.codigo_empleado
            FROM inventario_cpu icp
            JOIN empleados e ON TRIM(LEADING '0' FROM CAST(icp.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR))
            WHERE icp.id_estatus_cpu = 3
        """
        q_mon = """
            SELECT 'monitor' AS tipo, im.numero_serie AS id, im.numero_serie, CONCAT('Monitor ', COALESCE(im.marca, ''), ' ', COALESCE(im.modelo, ''), ' (S/N: ', COALESCE(im.numero_serie, ''), ')') AS descripcion, 
                   CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS asignado_a, im.codigo_empleado
            FROM inventario_monitores im
            JOIN empleados e ON TRIM(LEADING '0' FROM CAST(im.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR))
            WHERE im.id_estatus_monitor = 3
        """
        q_tab = """
            SELECT 'tablet' AS tipo, it.numero_serie AS id, it.numero_serie, CONCAT('Tablet ', COALESCE(it.marca, ''), ' ', COALESCE(it.modelo, ''), ' (S/N: ', COALESCE(it.numero_serie, ''), ')') AS descripcion, 
                   CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS asignado_a, it.codigo_empleado
            FROM inventario_tablets it
            JOIN empleados e ON TRIM(LEADING '0' FROM CAST(it.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR))
            WHERE it.id_estatus_tablet = 3
        """

        dfs = []
        for q in [q_cel, q_lap, q_cpu, q_mon, q_tab]:
            df_p = pd.read_sql(q, conn)
            if not df_p.empty:
                dfs.append(df_p)

        conn.close()

        if dfs:
            return pd.concat(dfs, ignore_index=True)
        return pd.DataFrame()

    except Exception as e:
        conn.close()
        st.error(f"⚠️ Error al obtener equipos asignados: {e}")
        return pd.DataFrame()

# ==============================================================================
# 3. TRANSACCIONES: ASIGNACIÓN Y DESVINCULACIÓN
# ==============================================================================
def procesar_asignacion_responsiva(codigo_empleado, cel_sel, lap_sel, cpu_sel, mon_sel, tab_sel):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        f_hoy = datetime.now().strftime('%Y-%m-%d')
        codigo_emp_exacto = str(codigo_empleado).strip().zfill(5)

        # 1. Celular
        if cel_sel:
            d = cel_sel['data']
            num_final = limpiar_str(d.get('num_edit')) or None

            cursor.execute("UPDATE responsivas_celulares SET id_status = 2 WHERE imei = %s AND id_status = 1", (d['imei'],))

            if num_final:
                cursor.execute("UPDATE responsivas_celulares SET id_status = 2 WHERE numero = %s AND id_status = 1", (num_final,))
                cursor.execute("UPDATE inventario_celulares SET numero = NULL WHERE numero = %s AND imei != %s", (num_final, d['imei']))
                cursor.execute("UPDATE lineas_telefonicas SET id_estatus_linea = 3, codigo_empleado = %s WHERE numero = %s", (codigo_emp_exacto, num_final))

            cursor.execute("""
                UPDATE inventario_celulares 
                SET id_estatus_celular = %s, codigo_empleado = %s, numero = %s, 
                    id_condicion = %s, id_cargador = %s, id_caja = %s, 
                    observaciones = %s, comentarios = %s 
                WHERE imei = %s
            """, (
                d.get('estatus_edit', 3), 
                codigo_emp_exacto, 
                num_final, 
                d.get('cond_edit'), 
                d.get('carg_edit'), 
                d.get('caja_edit'), 
                limpiar_str(d.get('obs_edit')) or None, 
                limpiar_str(d.get('com_edit')) or None, 
                d['imei']
            ))

            cursor.execute("""
                INSERT INTO responsivas_celulares (fecha_entrega, codigo_empleado, numero, imei, id_status)
                VALUES (%s, %s, %s, %s, 1)
            """, (f_hoy, codigo_emp_exacto, num_final, d['imei']))

        # 2. Laptop
        if lap_sel:
            d = lap_sel['data']
            cursor.execute("UPDATE responsivas_laptops SET id_status = 2 WHERE numero_serie = %s AND id_status = 1", (d['numero_serie'],))
            
            cursor.execute("""
                UPDATE inventario_laptops 
                SET id_estatus_laptops = %s, codigo_empleado = %s, 
                    id_condicion = %s, id_cargador = %s, 
                    observaciones = %s, comentarios = %s 
                WHERE numero_serie = %s
            """, (
                d.get('estatus_edit', 3), 
                codigo_emp_exacto, 
                d.get('cond_edit'), 
                d.get('carg_edit'), 
                limpiar_str(d.get('obs_edit')) or None, 
                limpiar_str(d.get('com_edit')) or None, 
                d['numero_serie']
            ))
            
            cursor.execute("""
                INSERT INTO responsivas_laptops (fecha_entrega, codigo_empleado, numero_serie, id_status)
                VALUES (%s, %s, %s, 1)
            """, (f_hoy, codigo_emp_exacto, d['numero_serie']))

        # 3. CPU
        if cpu_sel:
            d = cpu_sel['data']
            id_cpu_val = int(d['id_cpu'])
            cursor.execute("UPDATE responsivas_cpu SET id_status = 2 WHERE id_cpu = %s AND id_status = 1", (id_cpu_val,))
            
            cursor.execute("""
                UPDATE inventario_cpu 
                SET id_estatus_cpu = %s, codigo_empleado = %s, 
                    id_condicion = %s, observaciones = %s, comentarios = %s 
                WHERE id_cpu = %s
            """, (
                d.get('estatus_edit', 3), 
                codigo_emp_exacto, 
                d.get('cond_edit'), 
                limpiar_str(d.get('obs_edit')) or None, 
                limpiar_str(d.get('com_edit')) or None, 
                id_cpu_val
            ))
            
            cursor.execute("""
                INSERT INTO responsivas_cpu (id_cpu, fecha_entrega, codigo_empleado, id_status)
                VALUES (%s, %s, %s, 1)
            """, (id_cpu_val, f_hoy, codigo_emp_exacto))

        # 4. Monitor
        if mon_sel:
            d = mon_sel['data']
            cursor.execute("UPDATE responsivas_monitores SET id_status = 2 WHERE numero_serie = %s AND id_status = 1", (d['numero_serie'],))
            
            cursor.execute("""
                UPDATE inventario_monitores 
                SET id_estatus_monitor = %s, codigo_empleado = %s, 
                    id_condicion = %s, observaciones = %s, comentarios = %s 
                WHERE numero_serie = %s
            """, (
                d.get('estatus_edit', 3), 
                codigo_emp_exacto, 
                d.get('cond_edit'), 
                limpiar_str(d.get('obs_edit')) or None, 
                limpiar_str(d.get('com_edit')) or None, 
                d['numero_serie']
            ))
            
            cursor.execute("""
                INSERT INTO responsivas_monitores (fecha_entrega, codigo_empleado, numero_serie, id_status)
                VALUES (%s, %s, %s, 1)
            """, (f_hoy, codigo_emp_exacto, d['numero_serie']))

        # 5. Tablet
        if tab_sel:
            d = tab_sel['data']
            cursor.execute("UPDATE responsivas_tablets SET id_status = 2 WHERE numero_serie = %s AND id_status = 1", (d['numero_serie'],))
            
            cursor.execute("""
                UPDATE inventario_tablets 
                SET id_estatus_tablet = %s, codigo_empleado = %s, 
                    id_condicion = %s, id_cargador = %s, 
                    observaciones = %s, comentarios = %s 
                WHERE numero_serie = %s
            """, (
                d.get('estatus_edit', 3), 
                codigo_emp_exacto, 
                d.get('cond_edit'), 
                d.get('carg_edit'), 
                limpiar_str(d.get('obs_edit')) or None, 
                limpiar_str(d.get('com_edit')) or None, 
                d['numero_serie']
            ))
            
            cursor.execute("""
                INSERT INTO responsivas_tablets (fecha_entrega, codigo_empleado, numero_serie, id_status)
                VALUES (%s, %s, %s, 1)
            """, (f_hoy, codigo_emp_exacto, d['numero_serie']))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al procesar asignación: {e}")
        return False

def procesar_desvinculacion_equipo(tipo_equipo, id_equipo, nuevo_estatus_id, razon_motivo, nombre_colaborador=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        f_hoy = datetime.now().strftime('%Y-%m-%d')
        colab_txt = f" a {nombre_colaborador.strip()}" if nombre_colaborador.strip() else ""

        config_tablas = {
            "celular": {
                "inv": "inventario_celulares", "col_id": "imei", "col_est": "id_estatus_celular",
                "resp": "responsivas_celulares", "col_resp_id": "imei"
            },
            "laptop": {
                "inv": "inventario_laptops", "col_id": "numero_serie", "col_est": "id_estatus_laptops",
                "resp": "responsivas_laptops", "col_resp_id": "numero_serie"
            },
            "cpu": {
                "inv": "inventario_cpu", "col_id": "id_cpu", "col_est": "id_estatus_cpu",
                "resp": "responsivas_cpu", "col_resp_id": "id_cpu"
            },
            "monitor": {
                "inv": "inventario_monitores", "col_id": "numero_serie", "col_est": "id_estatus_monitor",
                "resp": "responsivas_monitores", "col_resp_id": "numero_serie"
            },
            "tablet": {
                "inv": "inventario_tablets", "col_id": "numero_serie", "col_est": "id_estatus_tablet",
                "resp": "responsivas_tablets", "col_resp_id": "numero_serie"
            }
        }

        cfg = config_tablas.get(tipo_equipo)
        if not cfg:
            return False

        # 1. Cerrar responsiva activa
        cursor.execute(f"UPDATE {cfg['resp']} SET id_status = 2 WHERE {cfg['col_resp_id']} = %s AND id_status = 1", (id_equipo,))

        # 2. Si es celular, liberar la línea telefónica
        if tipo_equipo == "celular":
            cursor.execute("SELECT numero FROM inventario_celulares WHERE imei = %s", (id_equipo,))
            res_num = cursor.fetchone()
            if res_num and res_num[0]:
                num_asig = res_num[0]
                cursor.execute("""
                    UPDATE lineas_telefonicas 
                    SET id_estatus_linea = 4, codigo_empleado = NULL 
                    WHERE numero = %s AND id_estatus_linea != 5
                """, (num_asig,))

        # 3. Actualizar inventario
        texto_historial = f"[DESVINCULADO {f_hoy}{colab_txt}]: {razon_motivo.strip()}"

        q_release = f"""
            UPDATE {cfg['inv']} 
            SET codigo_empleado = NULL, 
                {cfg['col_est']} = %s, 
                observaciones = CASE 
                    WHEN observaciones IS NULL OR TRIM(observaciones) = '' THEN %s 
                    ELSE CONCAT(observaciones, ' | ', %s) 
                END
            WHERE {cfg['col_id']} = %s
        """
        cursor.execute(q_release, (nuevo_estatus_id, texto_historial, texto_historial, id_equipo))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al desvincular equipo: {e}")
        return False

# ==============================================================================
# 4. GENERACIÓN Y RENDERIZADO DE ARCHIVOS DOCX
# ==============================================================================
def renderizar_plantilla(nombre_plantilla_env, contexto):
    nombre_archivo = os.getenv(nombre_plantilla_env)
    if not nombre_archivo:
        st.error(f"⚠️ Falta configurar la variable `{nombre_plantilla_env}` en el `.env`")
        return None
        
    ruta_plantilla = DIR_PLANTILLAS / nombre_archivo
    if not ruta_plantilla.exists():
        st.error(f"⚠️ No existe el archivo de plantilla: `{ruta_plantilla}`")
        return None

    doc = DocxTemplate(ruta_plantilla)
    doc.render(contexto)
    target = io.BytesIO()
    doc.save(target)
    target.seek(0)
    return target

def generar_documentos_responsivas(emp_row, cel_sel, lap_sel, cpu_sel, mon_sel, tab_sel):
    archivos = {}
    f_hoy = datetime.now()
    fecha_str = f_hoy.strftime('%Y%m%d')
    cod_emp_clean = str(emp_row['codigo_str']).zfill(5)

    ctx_base = {
        'fecha_entrega': format_fecha(f_hoy),
        'empleado': limpiar_str(emp_row['nombre_completo']).title(),
        'sucursal': limpiar_str(emp_row['sucursal'], 'S/D'),
        'departamento': limpiar_str(emp_row['departamento'], 'S/D'),
        'puesto': limpiar_str(emp_row['puesto'], 'S/D'),
        'correo_gmail': limpiar_str(emp_row['correo_gmail'], ''),
        'correo_corporativo': limpiar_str(emp_row['correo_corporativo'], '')
    }

    if cel_sel:
        folio_cel = f"RESP-CEL-{cod_emp_clean}-{fecha_str}"
        d = cel_sel['data']
        ctx = {**ctx_base, 
            'folio': folio_cel,
            'equipo': limpiar_str(d.get('equipo')), 
            'numero': limpiar_str(d.get('num_edit') or d.get('numero')),
            'imei': limpiar_str(d.get('imei')), 
            'numero_serie': limpiar_str(d.get('numero_serie')),
            'gb': limpiar_str(d.get('gb')), 
            'condicion': limpiar_str(d.get('cond_nom', d.get('condicion')), 'Buenas condiciones'),
            'cargador': limpiar_str(d.get('carg_nom', d.get('cargador')), 'CON Cargador Original y Cable Original'), 
            'caja': limpiar_str(d.get('caja_nom', d.get('caja')), 'Con caja'),
            'comentarios': limpiar_str(d.get('com_edit', d.get('comentarios'))),
            'precio': formatear_precio(d.get('precio')),
            'precio_letras': precio_a_letras(d.get('precio'))
        }
        res = renderizar_plantilla("PLANTILLA_CELULAR", ctx)
        if res: archivos[f"{folio_cel}_{emp_row['codigo_str']}.docx"] = res

    if lap_sel:
        folio_lap = f"RESP-LAP-{cod_emp_clean}-{fecha_str}"
        d = lap_sel['data']
        ctx = {**ctx_base,
            'folio': folio_lap,
            'marca': limpiar_str(d.get('marca')), 
            'modelo': limpiar_str(d.get('modelo')),
            'hostname': limpiar_str(d.get('hostname')),
            'numero_serie': limpiar_str(d.get('numero_serie')), 
            'procesador': limpiar_str(d.get('procesador')),
            'memoria_ram': limpiar_str(d.get('memoria_ram')),
            'tipo_hdd': limpiar_str(d.get('tipo_hdd')),
            'almacenamiento': limpiar_str(d.get('almacenamiento')),
            'condicion_lap': limpiar_str(d.get('cond_nom', d.get('condicion_lap')), 'Buenas condiciones'),
            'cargador': limpiar_str(d.get('carg_nom', d.get('cargador')), 'CON Cargador Original y Cable Original'),
            'comentarios': limpiar_str(d.get('com_edit', d.get('comentarios'))),
            'precio': formatear_precio(d.get('precio')),
            'precio_letras': precio_a_letras(d.get('precio'))
        }
        res = renderizar_plantilla("PLANTILLA_LAPTOP", ctx)
        if res: archivos[f"{folio_lap}_{emp_row['codigo_str']}.docx"] = res

    if cpu_sel:
        folio_cpu = f"RESP-CPU-{cod_emp_clean}-{fecha_str}"
        d = cpu_sel['data']
        ctx = {**ctx_base,
            'folio': folio_cpu,
            'marca': limpiar_str(d.get('marca')),
            'modelo': limpiar_str(d.get('modelo')),
            'hostname': limpiar_str(d.get('hostname')), 
            'numero_serie': limpiar_str(d.get('numero_serie')),
            'procesador': limpiar_str(d.get('procesador')),
            'memoria_ram': limpiar_str(d.get('memoria_ram')), 
            'tipo_hdd': limpiar_str(d.get('tipo_hdd')),
            'almacenamiento': limpiar_str(d.get('almacenamiento')), 
            'condicion': limpiar_str(d.get('cond_nom', d.get('condicion')), 'Buenas condiciones'),
            'comentarios': limpiar_str(d.get('com_edit', d.get('comentarios'))),
            'precio': formatear_precio(d.get('precio')),
            'precio_letras': precio_a_letras(d.get('precio'))
        }
        res = renderizar_plantilla("PLANTILLA_CPU", ctx)
        if res: archivos[f"{folio_cpu}_{emp_row['codigo_str']}.docx"] = res

    if mon_sel:
        folio_mon = f"RESP-MON-{cod_emp_clean}-{fecha_str}"
        d = mon_sel['data']
        ctx = {**ctx_base,
            'folio': folio_mon,
            'marca': limpiar_str(d.get('marca')), 
            'modelo': limpiar_str(d.get('modelo')),
            'numero_serie': limpiar_str(d.get('numero_serie')),
            'condicion': limpiar_str(d.get('cond_nom', d.get('condicion')), 'Buenas condiciones'),
            'comentarios': limpiar_str(d.get('com_edit', d.get('comentarios'))),
            'precio': formatear_precio(d.get('precio')),
            'precio_letras': precio_a_letras(d.get('precio'))
        }
        res = renderizar_plantilla("PLANTILLA_MONITOR", ctx)
        if res: archivos[f"{folio_mon}_{emp_row['codigo_str']}.docx"] = res

    if tab_sel:
        folio_tab = f"RESP-TAB-{cod_emp_clean}-{fecha_str}"
        d = tab_sel['data']
        ctx = {**ctx_base,
            'folio': folio_tab,
            'marca': limpiar_str(d.get('marca')), 
            'modelo': limpiar_str(d.get('modelo')),
            'imei': limpiar_str(d.get('imei')), 
            'numero_serie': limpiar_str(d.get('numero_serie')),
            'condicion': limpiar_str(d.get('cond_nom', d.get('condicion')), 'Buenas condiciones'), 
            'cargador': limpiar_str(d.get('carg_nom', d.get('cargador')), 'CON Cargador Original y Cable Original'),
            'comentarios': limpiar_str(d.get('com_edit', d.get('comentarios'))),
            'precio': formatear_precio(d.get('precio')),
            'precio_letras': precio_a_letras(d.get('precio'))
        }
        res = renderizar_plantilla("PLANTILLA_TABLET", ctx)
        if res: archivos[f"{folio_tab}_{emp_row['codigo_str']}.docx"] = res

    return archivos

# ==============================================================================
# 5. RENDER PRINCIPAL DE STREAMLIT
# ==============================================================================
def render():
    aplicar_estilos_pantalla()
    st.title("📄 Módulo de Responsivas y Gestión de Asignaciones")

    tab_asig, tab_desv = st.tabs(["📄 Nueva Asignación de Responsiva", "🔄 Devolución / Desvinculación de Equipo"])

    # --------------------------------------------------------------------------
    # SUB-TAB 1: NUEVA ASIGNACIÓN
    # --------------------------------------------------------------------------
    with tab_asig:
        df_emp = obtener_empleados_activos_df()
        dict_equipos = obtener_equipos_disponibles()

        dict_cond = obtener_catalogo_dict("condicion", "id_condicion", "condicion_opcion")
        dict_carg = obtener_catalogo_dict("cargadores", "id_cargador", "cargador_opcion")
        dict_caja = obtener_catalogo_dict("caja", "id_caja", "caja_opcion")
        
        dict_est_cel = obtener_catalogo_dict("estatus_celulares", "id_estatus_celular", "estatus_celular")
        dict_est_lap = obtener_catalogo_dict("estatus_laptops", "id_estatus_laptops", "estatus_laptop")
        dict_est_cpu = obtener_catalogo_dict("estatus_cpu", "id_estatus_cpu", "estatus_cpu")
        dict_est_mon = obtener_catalogo_dict("estatus_monitores", "id_estatus_monitor", "estatus_monitor")
        dict_est_tab = obtener_catalogo_dict("estatus_tablets", "id_estatus_tablet", "estatus_tablet")

        if df_emp.empty:
            st.warning("⚠️ No se encontraron empleados activos.")
            return

        col1, col2 = st.columns([2, 1])
        with col1:
            lista_emp = [f"{r['codigo_str']} - {r['nombre_completo']} ({r['sucursal']})" for _, r in df_emp.iterrows()]
            emp_sel_str = st.selectbox("Selecciona el colaborador a asignar:", lista_emp)
            codigo_sel = emp_sel_str.split(" - ")[0]
            emp_row = df_emp[df_emp["codigo_str"] == codigo_sel].iloc[0]

        with col2:
            st.info(f"**Sucursal:** {emp_row['sucursal']}\n\n**Departamento:** {emp_row['departamento']}\n\n**Puesto:** {emp_row['puesto']}")

        st.divider()
        st.markdown("### 📦 Selecciona el Hardware DISPONIBLE a Asignar")

        c1, c2 = st.columns(2)
        with c1:
            opts_cel = ["-- Ninguno --"] + [x["label"] for x in dict_equipos["celulares"]]
            sel_cel_txt = st.selectbox("📱 Celulares Disponibles:", opts_cel)
            obj_cel = next((x for x in dict_equipos["celulares"] if x["label"] == sel_cel_txt), None)

            opts_lap = ["-- Ninguno --"] + [x["label"] for x in dict_equipos["laptops"]]
            sel_lap_txt = st.selectbox("💻 Laptops Disponibles:", opts_lap)
            obj_lap = next((x for x in dict_equipos["laptops"] if x["label"] == sel_lap_txt), None)

            opts_tab = ["-- Ninguno --"] + [x["label"] for x in dict_equipos["tablets"]]
            sel_tab_txt = st.selectbox("📱 Tablets Disponibles:", opts_tab)
            obj_tab = next((x for x in dict_equipos["tablets"] if x["label"] == sel_tab_txt), None)

        with c2:
            opts_cpu = ["-- Ninguno --"] + [x["label"] for x in dict_equipos["cpus"]]
            sel_cpu_txt = st.selectbox("🖥️ CPUs Disponibles:", opts_cpu)
            obj_cpu = next((x for x in dict_equipos["cpus"] if x["label"] == sel_cpu_txt), None)

            opts_mon = ["-- Ninguno --"] + [x["label"] for x in dict_equipos["monitores"]]
            sel_mon_txt = st.selectbox("🖥️ Monitores Disponibles:", opts_mon)
            obj_mon = next((x for x in dict_equipos["monitores"] if x["label"] == sel_mon_txt), None)

        if obj_cel or obj_lap or obj_cpu or obj_mon or obj_tab:
            st.divider()
            st.markdown("### ⚙️ Configuración y Estado del Equipo al Momento de Entrega")
            
            # 1. CELULAR
            if obj_cel:
                with st.expander("📱 Ajustar Datos del Celular", expanded=True):
                    d = obj_cel['data']
                    c_a, c_b, c_c = st.columns(3)
                    num_in = c_a.text_input("Número / Línea Asignada:", value=limpiar_str(d.get('numero')))
                    cond_nom = c_b.selectbox("Condición Celular:", list(dict_cond.keys()), index=list(dict_cond.values()).index(d['id_condicion']) if d.get('id_condicion') in dict_cond.values() else 0, key="cond_cel")
                    carg_nom = c_c.selectbox("Cargador Incluido:", list(dict_carg.keys()), index=list(dict_carg.values()).index(d['id_cargador']) if d.get('id_cargador') in dict_carg.values() else 0, key="carg_cel")
                    
                    c_d, c_e = st.columns(2)
                    caja_nom = c_d.selectbox("Caja Incluida:", list(dict_caja.keys()), index=list(dict_caja.values()).index(d['id_caja']) if d.get('id_caja') in dict_caja.values() else 0, key="caja_cel")
                    est_nom = c_e.selectbox("Estatus Celular:", list(dict_est_cel.keys()), index=list(dict_est_cel.keys()).index("ASIGNADO") if "ASIGNADO" in dict_est_cel else 0, key="est_cel")

                    ca, cb = st.columns(2)
                    obs_in = ca.text_input("Observaciones Celular:", value=limpiar_str(d.get('observaciones')), key="obs_cel")
                    com_in = cb.text_input("Comentarios Celular (va al Word):", value=limpiar_str(d.get('comentarios')), key="com_cel")

                    d['num_edit'] = num_in.strip() or None
                    d['cond_edit'] = dict_cond[cond_nom]; d['cond_nom'] = cond_nom
                    d['carg_edit'] = dict_carg[carg_nom]; d['carg_nom'] = carg_nom
                    d['caja_edit'] = dict_caja[caja_nom]; d['caja_nom'] = caja_nom
                    d['estatus_edit'] = dict_est_cel[est_nom]
                    d['obs_edit'] = obs_in.strip()
                    d['com_edit'] = com_in.strip()

            # 2. LAPTOP
            if obj_lap:
                with st.expander("💻 Ajustar Datos de la Laptop", expanded=True):
                    d = obj_lap['data']
                    c_a, c_b, c_c = st.columns(3)
                    cond_nom = c_a.selectbox("Condición Laptop:", list(dict_cond.keys()), index=list(dict_cond.values()).index(d['id_condicion']) if d.get('id_condicion') in dict_cond.values() else 0, key="cond_lap")
                    carg_nom = c_b.selectbox("Cargador Incluido:", list(dict_carg.keys()), index=list(dict_carg.values()).index(d['id_cargador']) if d.get('id_cargador') in dict_carg.values() else 0, key="carg_lap")
                    est_nom = c_c.selectbox("Estatus Laptop:", list(dict_est_lap.keys()), index=list(dict_est_lap.keys()).index("ASIGNADO") if "ASIGNADO" in dict_est_lap else 0, key="est_lap")

                    ca, cb = st.columns(2)
                    obs_in = ca.text_input("Observaciones Laptop:", value=limpiar_str(d.get('observaciones')), key="obs_lap")
                    com_in = cb.text_input("Comentarios Laptop (va al Word):", value=limpiar_str(d.get('comentarios')), key="com_lap")

                    d['cond_edit'] = dict_cond[cond_nom]; d['cond_nom'] = cond_nom
                    d['carg_edit'] = dict_carg[carg_nom]; d['carg_nom'] = carg_nom
                    d['estatus_edit'] = dict_est_lap[est_nom]
                    d['obs_edit'] = obs_in.strip()
                    d['com_edit'] = com_in.strip()

            # 3. CPU
            if obj_cpu:
                with st.expander("🖥️ Ajustar Datos del CPU", expanded=True):
                    d = obj_cpu['data']
                    c_a, c_b = st.columns(2)
                    cond_nom = c_a.selectbox("Condición CPU:", list(dict_cond.keys()), index=list(dict_cond.values()).index(d['id_condicion']) if d.get('id_condicion') in dict_cond.values() else 0, key="cond_cpu")
                    est_nom = c_b.selectbox("Estatus CPU:", list(dict_est_cpu.keys()), index=list(dict_est_cpu.keys()).index("ASIGNADO") if "ASIGNADO" in dict_est_cpu else 0, key="est_cpu")

                    ca, cb = st.columns(2)
                    obs_in = ca.text_input("Observaciones CPU:", value=limpiar_str(d.get('observaciones')), key="obs_cpu")
                    com_in = cb.text_input("Comentarios CPU (va al Word):", value=limpiar_str(d.get('comentarios')), key="com_cpu")

                    d['cond_edit'] = dict_cond[cond_nom]; d['cond_nom'] = cond_nom
                    d['estatus_edit'] = dict_est_cpu[est_nom]
                    d['obs_edit'] = obs_in.strip()
                    d['com_edit'] = com_in.strip()

            # 4. MONITOR
            if obj_mon:
                with st.expander("🖥️ Ajustar Datos del Monitor", expanded=True):
                    d = obj_mon['data']
                    c_a, c_b = st.columns(2)
                    cond_nom = c_a.selectbox("Condición Monitor:", list(dict_cond.keys()), index=list(dict_cond.values()).index(d['id_condicion']) if d.get('id_condicion') in dict_cond.values() else 0, key="cond_mon")
                    est_nom = c_b.selectbox("Estatus Monitor:", list(dict_est_mon.keys()), index=list(dict_est_mon.keys()).index("ASIGNADO") if "ASIGNADO" in dict_est_mon else 0, key="est_mon")

                    ca, cb = st.columns(2)
                    obs_in = ca.text_input("Observaciones Monitor:", value=limpiar_str(d.get('observaciones')), key="obs_mon")
                    com_in = cb.text_input("Comentarios Monitor (va al Word):", value=limpiar_str(d.get('comentarios')), key="com_mon")

                    d['cond_edit'] = dict_cond[cond_nom]; d['cond_nom'] = cond_nom
                    d['estatus_edit'] = dict_est_mon[est_nom]
                    d['obs_edit'] = obs_in.strip()
                    d['com_edit'] = com_in.strip()

            # 5. TABLET
            if obj_tab:
                with st.expander("📱 Ajustar Datos de la Tablet", expanded=True):
                    d = obj_tab['data']
                    c_a, c_b, c_c = st.columns(3)
                    cond_nom = c_a.selectbox("Condición Tablet:", list(dict_cond.keys()), index=list(dict_cond.values()).index(d['id_condicion']) if d.get('id_condicion') in dict_cond.values() else 0, key="cond_tab")
                    carg_nom = c_b.selectbox("Cargador Incluido:", list(dict_carg.keys()), index=list(dict_carg.values()).index(d['id_cargador']) if d.get('id_cargador') in dict_carg.values() else 0, key="carg_tab")
                    est_nom = c_c.selectbox("Estatus Tablet:", list(dict_est_tab.keys()), index=list(dict_est_tab.keys()).index("ASIGNADO") if "ASIGNADO" in dict_est_tab else 0, key="est_tab")

                    ca, cb = st.columns(2)
                    obs_in = ca.text_input("Observaciones Tablet:", value=limpiar_str(d.get('observaciones')), key="obs_tab")
                    com_in = cb.text_input("Comentarios Tablet (va al Word):", value=limpiar_str(d.get('comentarios')), key="com_tab")

                    d['cond_edit'] = dict_cond[cond_nom]; d['cond_nom'] = cond_nom
                    d['carg_edit'] = dict_carg[carg_nom]; d['carg_nom'] = carg_nom
                    d['estatus_edit'] = dict_est_tab[est_nom]
                    d['obs_edit'] = obs_in.strip()
                    d['com_edit'] = com_in.strip()

        st.divider()

        if not (obj_cel or obj_lap or obj_cpu or obj_mon or obj_tab):
            st.warning("👉 Selecciona al menos un equipo para habilitar la asignación.")
        else:
            if st.button("🚀 Confirmar Asignación y Generar Documentos", type="primary"):
                if procesar_asignacion_responsiva(codigo_sel, obj_cel, obj_lap, obj_cpu, obj_mon, obj_tab):
                    archivos_generados = generar_documentos_responsivas(emp_row, obj_cel, obj_lap, obj_cpu, obj_mon, obj_tab)
                    st.session_state["archivos_responsivas"] = archivos_generados
                    st.toast("¡Asignación guardada, inventario actualizado y documentos listos!", icon="🎉")
                    st.rerun()

        if "archivos_responsivas" in st.session_state:
            st.success("✅ ¡Transacción completada! Descarga los archivos `.docx` correspondientes:")
            for nombre_file, buffer_data in st.session_state["archivos_responsivas"].items():
                st.download_button(
                    label=f"📥 Descargar {nombre_file}",
                    data=buffer_data,
                    file_name=nombre_file,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            if st.button("🔄 Nueva Asignación"):
                del st.session_state["archivos_responsivas"]
                st.rerun()

    # --------------------------------------------------------------------------
    # SUB-TAB 2: DESVINCULACIÓN Y RECEPCIÓN DE HARDWARE
    # --------------------------------------------------------------------------
    with tab_desv:
        st.markdown("### 🔄 Recepción y Liberación de Hardware Asignado")
        st.caption("Usa este módulo cuando un colaborador devuelva un equipo, se vaya de la empresa o el hardware requiera reparación/baja.")

        if "mensaje_exito_desv" in st.session_state:
            st.success(st.session_state["mensaje_exito_desv"])
            del st.session_state["mensaje_exito_desv"]

        df_asig = obtener_hardware_asignado_desvinculacion_df()

        if not df_asig.empty:
            lista_opciones = [
                f"[{row['tipo'].upper()}] - {row['descripcion']} ---> Asignado a: {row['asignado_a']}"
                for _, row in df_asig.iterrows()
            ]
            
            equipo_desv_sel = st.selectbox(
                "Selecciona el equipo a recibir / desvincular:",
                lista_opciones,
                index=None,
                placeholder="🔍 Selecciona o teclea el equipo asignado a liberar...",
                key="sel_desv_hardware"
            )

            if equipo_desv_sel:
                idx_sel = lista_opciones.index(equipo_desv_sel)
                item_row = df_asig.iloc[idx_sel]

                st.divider()

                with st.form("form_desvincular_hardware"):
                    st.markdown(f"**Desvinculando:** `{item_row['descripcion']}`")
                    st.markdown(f"**Usuario Actual:** `{item_row['asignado_a']}` (`Código: {item_row['codigo_empleado']}`)")

                    c_d1, c_d2 = st.columns(2)
                    with c_d1:
                        dict_estatus_destino = {
                            "DISPONIBLE (Devolución limpia al stock)": 4,
                            "EN REPARACIÓN (Pantalla rota, fallo de hardware)": 6,
                            "EN MANTENIMIENTO (Limpieza, formateo, software)": 5,
                            "INACTIVO (Baja definitiva / Inservible)": 2
                        }
                        destino_nom = st.selectbox("Nuevo Estatus del Equipo en Inventario:", list(dict_estatus_destino.keys()))

                    with c_d2:
                        motivo_txt = st.text_input("Motivo / Diagnóstico de Recepción:", placeholder="Ej. Pantalla quebrada por caída, baja de empleado, cambio de equipo")

                    btn_liberar = st.form_submit_button("💥 Confirmar Desvinculación y Liberar Equipo", type="primary")

                    if btn_liberar:
                        if not motivo_txt.strip():
                            st.warning("⚠️ Ingresa un motivo de recepción para el historial de observaciones.")
                        else:
                            nombre_completo_colab = f"{item_row['asignado_a']} (Cód: {item_row['codigo_empleado']})"
                            exito = procesar_desvinculacion_equipo(
                                tipo_equipo=item_row['tipo'],
                                id_equipo=item_row['id'],
                                nuevo_estatus_id=dict_estatus_destino[destino_nom],
                                razon_motivo=motivo_txt,
                                nombre_colaborador=nombre_completo_colab
                            )
                            if exito:
                                st.session_state["mensaje_exito_desv"] = f"🎉 ¡Equipo **{item_row['descripcion']}** (Asignado a: **{item_row['asignado_a']}**) desvinculado con éxito! Se actualizó su estatus a: **{destino_nom}**."
                                st.rerun()
            else:
                st.info("👆 Selecciona un equipo de la lista desplegable de arriba para abrir el formulario de recepción.")
        else:
            st.info("No hay ningún equipo asignado actualmente en la base de datos.")

render_responsivas = render