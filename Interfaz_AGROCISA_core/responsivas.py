import streamlit as st
import pandas as pd
from datetime import datetime
import io
import os
from pathlib import Path
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
        query = f"SELECT {col_id}, {col_nombre} FROM {tabla} ORDER BY {col_nombre} ASC"
        df = pd.read_sql(query, conn)
        conn.close()
        return dict(zip(df[col_nombre], df[col_id]))
    except Exception as e:
        st.error(f"⚠️ Error al cargar catálogo {tabla}: {e}")
        return {}

def obtener_columnas_tabla(cursor, tabla):
    try:
        cursor.execute(f"SHOW COLUMNS FROM {tabla}")
        return [row[0] for row in cursor.fetchall()]
    except Exception:
        return []

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
                s.nombre_sucursal AS sucursal,
                d.nombre_departamento AS departamento,
                p.nombre_puesto AS puesto,
                ce.correo_gmail,
                ce.correo_corporativo
            FROM empleados e
            LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
            LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento
            LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
            LEFT JOIN (
                SELECT 
                    codigo_empleado,
                    MAX(CASE WHEN id_tipo_correo = 2 THEN direccion_correo END) AS correo_gmail,
                    MAX(CASE WHEN id_tipo_correo = 1 THEN direccion_correo END) AS correo_corporativo
                FROM correos_electronicos
                WHERE id_estatus_correo = 1
                GROUP BY codigo_empleado
            ) ce ON e.codigo = ce.codigo_empleado
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
        # 1. Celulares DISPONIBLES (Filtra líneas V.I.P. con id_estatus != 5)
        df_cel = pd.read_sql("""
            SELECT ic.imei, ic.numero, ic.numero_serie, m.marca_modelo AS equipo, m.precio, 
                   ic.id_condicion, c.condicion_opcion AS condicion, 
                   ic.id_cargador, ca.cargador_opcion AS cargador, 
                   ic.id_caja, caja.caja_opcion AS caja,
                   ic.id_estatus_celular, lt.gb_promocion_2026 AS gb, ic.observaciones, ic.comentarios
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
            obs_txt = f" | Obs: {r['observaciones']}" if pd.notna(r['observaciones']) and str(r['observaciones']).strip() else ""
            lbl = f"IMEI: {r['imei']} - {r['equipo']} (Línea: {r['numero'] or 'S/N'}){obs_txt}"
            equipos["celulares"].append({"id": r['imei'], "label": lbl, "data": r.to_dict()})

        # 2. Laptops DISPONIBLES + Observaciones
        df_lap = pd.read_sql("""
            SELECT il.numero_serie, il.marca, il.modelo, il.hostname, il.observaciones, il.comentarios, 
                   il.id_condicion, con.condicion_opcion AS condicion_lap, 
                   il.id_cargador, car.cargador_opcion AS cargador, 
                   il.id_estatus_laptops, 0 AS precio
            FROM inventario_laptops il
            LEFT JOIN condicion con ON il.id_condicion = con.id_condicion
            LEFT JOIN cargadores car ON il.id_cargador = car.id_cargador
            WHERE il.id_estatus_laptops = 4
        """, conn)
        for _, r in df_lap.iterrows():
            obs_txt = f" | Obs: {r['observaciones']}" if pd.notna(r['observaciones']) and str(r['observaciones']).strip() else ""
            lbl = f"Serie: {r['numero_serie']} - {r['marca']} {r['modelo']} [{r['hostname']}]{obs_txt}"
            equipos["laptops"].append({"id": r['numero_serie'], "label": lbl, "data": r.to_dict()})

        # 3. CPUs DISPONIBLES + Observaciones
        df_cpu = pd.read_sql("""
            SELECT icp.hostname, icp.numero_serie, icp.procesador, icp.memoria_ram, icp.almacenamiento, 
                   thd.hdd_opcion AS tipo_hdd, icp.id_condicion, con.condicion_opcion AS condicion, 
                   icp.id_estatus_cpu, icp.observaciones, icp.comentarios, 0 AS precio
            FROM inventario_cpu icp
            LEFT JOIN hdd_tipo thd ON icp.id_hdd_tipo = thd.id_hdd_tipo
            LEFT JOIN condicion con ON icp.id_condicion = con.id_condicion
            WHERE icp.id_estatus_cpu = 4
        """, conn)
        for _, r in df_cpu.iterrows():
            obs_txt = f" | Obs: {r['observaciones']}" if pd.notna(r['observaciones']) and str(r['observaciones']).strip() else ""
            lbl = f"Host: {r['hostname']} - Serie: {r['numero_serie']}{obs_txt}"
            equipos["cpus"].append({"id": r['hostname'], "label": lbl, "data": r.to_dict()})

        # 4. Monitores DISPONIBLES + Observaciones
        df_mon = pd.read_sql("""
            SELECT imon.numero_serie, imon.marca, imon.modelo, imon.id_condicion, 
                   imon.id_estatus_monitor, imon.observaciones, imon.comentarios, 0 AS precio
            FROM inventario_monitores imon
            WHERE imon.id_estatus_monitor = 4
        """, conn)
        for _, r in df_mon.iterrows():
            obs_txt = f" | Obs: {r['observaciones']}" if pd.notna(r['observaciones']) and str(r['observaciones']).strip() else ""
            lbl = f"Serie: {r['numero_serie']} - {r['marca']} {r['modelo']}{obs_txt}"
            equipos["monitores"].append({"id": r['numero_serie'], "label": lbl, "data": r.to_dict()})

        # 5. Tablets DISPONIBLES + Observaciones
        df_tab = pd.read_sql("""
            SELECT itab.numero_serie, itab.imei, itab.marca, itab.modelo, 
                   itab.id_condicion, con.condicion_opcion AS condicion, 
                   itab.id_cargador, car.cargador_opcion AS cargador, 
                   itab.id_estatus_tablet, itab.observaciones, itab.comentarios, 0 AS precio
            FROM inventario_tablets itab
            LEFT JOIN condicion con ON itab.id_condicion = con.id_condicion
            LEFT JOIN cargadores car ON itab.id_cargador = car.id_cargador
            WHERE itab.id_estatus_tablet = 4
        """, conn)
        for _, r in df_tab.iterrows():
            obs_txt = f" | Obs: {r['observaciones']}" if pd.notna(r['observaciones']) and str(r['observaciones']).strip() else ""
            lbl = f"Serie: {r['numero_serie']} - {r['marca']} {r['modelo']}{obs_txt}"
            equipos["tablets"].append({"id": r['numero_serie'], "label": lbl, "data": r.to_dict()})

    except Exception as e:
        st.error(f"⚠️ Error al consultar inventario: {e}")
    finally:
        conn.close()

    return equipos

# ==============================================================================
# 3. TRANSACCIONES: ASIGNACIÓN Y DESVINCULACIÓN
# ==============================================================================
def procesar_asignacion_responsiva(codigo_empleado, cel_sel, lap_sel, cpu_sel, mon_sel, tab_sel):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        f_hoy = datetime.now().strftime('%Y-%m-%d')
        codigo_emp_exacto = str(codigo_empleado).strip()

        def cerrar_responsivas_previas(tabla, col_id_nombre, valor_id):
            """Detecta dinámicamente si la tabla de responsivas tiene columna de estatus para inactivarla."""
            cols_reales = obtener_columnas_tabla(cursor, tabla)
            col_estatus_nom = None
            for cand in ['id_status', 'id_estatus', 'id_estatus_responsiva', 'id_status_responsiva']:
                if cand in cols_reales:
                    col_estatus_nom = cand
                    break
            
            if col_estatus_nom and col_id_nombre in cols_reales:
                q_close = f"UPDATE {tabla} SET {col_estatus_nom} = 2 WHERE {col_id_nombre} = %s AND {col_estatus_nom} = 1"
                cursor.execute(q_close, (valor_id,))

        def ejecutar_insert_adaptativo(tabla, dict_valores):
            cols_reales = obtener_columnas_tabla(cursor, tabla)
            col_estatus_nom = None
            for cand in ['id_status', 'id_estatus', 'id_estatus_responsiva', 'id_status_responsiva']:
                if cand in cols_reales:
                    col_estatus_nom = cand
                    break

            campos_f, vals_f = [], []
            for col, val in dict_valores.items():
                if col in cols_reales:
                    campos_f.append(col)
                    vals_f.append(val)

            if col_estatus_nom:
                campos_f.append(col_estatus_nom)
                vals_f.append(1)

            cols_str = ", ".join(campos_f)
            placeholders = ", ".join(["%s"] * len(vals_f))
            cursor.execute(f"INSERT INTO {tabla} ({cols_str}) VALUES ({placeholders})", tuple(vals_f))

        # 1. Celular
        # 1. Celular
        if cel_sel:
            d = cel_sel['data']
            cerrar_responsivas_previas("responsivas_celulares", "imei", d['imei'])
            
            # Actualiza inventario de celulares
            cursor.execute("""
                UPDATE inventario_celulares 
                SET id_estatus_celular = %s, codigo_empleado = %s, numero = %s, 
                    id_condicion = %s, id_cargador = %s, id_caja = %s, 
                    observaciones = %s, comentarios = %s 
                WHERE imei = %s
            """, (d.get('estatus_edit', 3), codigo_emp_exacto, d.get('num_edit'), d.get('cond_edit'), d.get('carg_edit'), d.get('caja_edit'), d.get('obs_edit', ''), d.get('com_edit', ''), d['imei']))
            
            # 💥 PARCHE LÍNEA: Cambia el estatus de la línea telefónica a ASIGNADO (3) y amarra el empleado
            if d.get('num_edit'):
                cursor.execute("""
                    UPDATE lineas_telefonicas 
                    SET id_estatus_linea = 3, codigo_empleado = %s 
                    WHERE numero = %s
                """, (codigo_emp_exacto, d.get('num_edit')))

            ejecutar_insert_adaptativo("responsivas_celulares", {
                "fecha_entrega": f_hoy, "codigo_empleado": codigo_emp_exacto, "numero": d.get('num_edit'), "imei": d['imei']
            })

        # 2. Laptop
        if lap_sel:
            d = lap_sel['data']
            cerrar_responsivas_previas("responsivas_laptops", "numero_serie", d['numero_serie'])
            
            cursor.execute("""
                UPDATE inventario_laptops 
                SET id_estatus_laptops = %s, codigo_empleado = %s, 
                    id_condicion = %s, id_cargador = %s, 
                    observaciones = %s, comentarios = %s 
                WHERE numero_serie = %s
            """, (d.get('estatus_edit', 3), codigo_emp_exacto, d.get('cond_edit'), d.get('carg_edit'), d.get('obs_edit', ''), d.get('com_edit', ''), d['numero_serie']))
            
            ejecutar_insert_adaptativo("responsivas_laptops", {
                "fecha_entrega": f_hoy, "codigo_empleado": codigo_emp_exacto, "numero_serie": d['numero_serie']
            })

        # 3. CPU
        if cpu_sel:
            d = cpu_sel['data']
            cerrar_responsivas_previas("responsivas_cpu", "hostname", d['hostname'])
            
            cursor.execute("""
                UPDATE inventario_cpu 
                SET id_estatus_cpu = %s, codigo_empleado = %s, 
                    id_condicion = %s, observaciones = %s, comentarios = %s 
                WHERE hostname = %s
            """, (d.get('estatus_edit', 3), codigo_emp_exacto, d.get('cond_edit'), d.get('obs_edit', ''), d.get('com_edit', ''), d['hostname']))
            
            cursor.execute("SELECT id_cpu FROM inventario_cpu WHERE hostname = %s", (d['hostname'],))
            r_cpu = cursor.fetchone()
            id_cpu_val = r_cpu[0] if r_cpu else None

            ejecutar_insert_adaptativo("responsivas_cpu", {
                "fecha_entrega": f_hoy, "codigo_empleado": codigo_emp_exacto, "hostname": d['hostname'], "id_cpu": id_cpu_val
            })

        # 4. Monitor
        if mon_sel:
            d = mon_sel['data']
            cerrar_responsivas_previas("responsivas_monitores", "numero_serie", d['numero_serie'])
            
            cursor.execute("""
                UPDATE inventario_monitores 
                SET id_estatus_monitor = %s, codigo_empleado = %s, 
                    id_condicion = %s, observaciones = %s, comentarios = %s 
                WHERE numero_serie = %s
            """, (d.get('estatus_edit', 3), codigo_emp_exacto, d.get('cond_edit'), d.get('obs_edit', ''), d.get('com_edit', ''), d['numero_serie']))
            
            ejecutar_insert_adaptativo("responsivas_monitores", {
                "fecha_entrega": f_hoy, "codigo_empleado": codigo_emp_exacto, "numero_serie": d['numero_serie']
            })

        # 5. Tablet
        if tab_sel:
            d = tab_sel['data']
            cerrar_responsivas_previas("responsivas_tablets", "numero_serie", d['numero_serie'])
            
            cursor.execute("""
                UPDATE inventario_tablets 
                SET id_estatus_tablet = %s, codigo_empleado = %s, 
                    id_condicion = %s, id_cargador = %s, 
                    observaciones = %s, comentarios = %s 
                WHERE numero_serie = %s
            """, (d.get('estatus_edit', 3), codigo_emp_exacto, d.get('cond_edit'), d.get('carg_edit'), d.get('obs_edit', ''), d.get('com_edit', ''), d['numero_serie']))
            
            ejecutar_insert_adaptativo("responsivas_tablets", {
                "fecha_entrega": f_hoy, "codigo_empleado": codigo_emp_exacto, "numero_serie": d['numero_serie']
            })

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al procesar asignación: {e}")
        return False

def procesar_desvinculacion_equipo(tipo_equipo, id_equipo, nuevo_estatus_id, razon_motivo):
    """
    Cierra la responsiva activa y libera el equipo mandando codigo_empleado a NULL adaptándose al esquema real.
    """
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        f_hoy = datetime.now().strftime('%Y-%m-%d')

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
                "inv": "inventario_cpu", "col_id": "hostname", "col_est": "id_estatus_cpu",
                "resp": "responsivas_cpu", "col_resp_id": "hostname"
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

        # 1. Inactivar la responsiva vigente adaptándonos al nombre real de la columna de estatus
        cols_resp = obtener_columnas_tabla(cursor, cfg['resp'])
        col_estatus_nom = None
        for cand in ['id_status', 'id_estatus', 'id_estatus_responsiva', 'id_status_responsiva']:
            if cand in cols_resp:
                col_estatus_nom = cand
                break

        if col_estatus_nom and cfg['col_resp_id'] in cols_resp:
            q_close = f"UPDATE {cfg['resp']} SET {col_estatus_nom} = 2 WHERE {cfg['col_resp_id']} = %s AND {col_estatus_nom} = 1"
            cursor.execute(q_close, (id_equipo,))

        # 2. Liberar el equipo en inventario: NULL a empleado y nuevo estatus (Disponible, Reparación, etc.)
        q_release = f"""
            UPDATE {cfg['inv']} 
            SET codigo_empleado = NULL, 
                {cfg['col_est']} = %s, 
                observaciones = CONCAT(COALESCE(observaciones, ''), ' | [DESVINCULADO {f_hoy}]: ', %s)
            WHERE {cfg['col_id']} = %s
        """
        cursor.execute(q_release, (nuevo_estatus_id, razon_motivo.strip(), id_equipo))

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
        'empleado': str(emp_row['nombre_completo']).title(),
        'sucursal': emp_row['sucursal'],
        'departamento': emp_row['departamento'],
        'puesto': emp_row['puesto'],
        'correo_gmail': emp_row['correo_gmail'] or '',
        'correo_corporativo': emp_row['correo_corporativo'] or ''
    }

    if cel_sel:
        folio_cel = f"RESP-CEL-{cod_emp_clean}-{fecha_str}"
        d = cel_sel['data']
        ctx = {**ctx_base, 
            'folio': folio_cel,  # 👈 INYECTA {{folio}} AL WORD
            'equipo': d.get('equipo', ''), 'numero': str(d.get('num_edit', '') or ''),
            'imei': str(d.get('imei', '') or ''), 'numero_serie': str(d.get('numero_serie', '') or ''),
            'gb': str(d.get('gb', '') or ''), 'condicion': d.get('cond_nom', d.get('condicion', '')),
            'cargador': d.get('carg_nom', d.get('cargador', '')), 'caja': d.get('caja_nom', d.get('caja', '')),
            'comentarios': d.get('com_edit', d.get('comentarios', '')),
            'precio': formatear_precio(d.get('precio')),
            'precio_letras': precio_a_letras(d.get('precio'))
        }
        res = renderizar_plantilla("PLANTILLA_CELULAR", ctx)
        if res: archivos[f"{folio_cel}_{emp_row['codigo_str']}.docx"] = res

    if lap_sel:
        folio_lap = f"RESP-LAP-{cod_emp_clean}-{fecha_str}"
        d = lap_sel['data']
        ctx = {**ctx_base,
            'folio': folio_lap,  # 👈 INYECTA {{folio}} AL WORD
            'marca': d.get('marca', ''), 'modelo': str(d.get('modelo', '') or ''),
            'numero_serie': d.get('numero_serie', ''), 'condicion_lap': d.get('cond_nom', d.get('condicion_lap', '')),
            'cargador': d.get('carg_nom', d.get('cargador', '')),
            'comentarios': d.get('com_edit', d.get('comentarios', '')),
            'precio': formatear_precio(d.get('precio')),
            'precio_letras': precio_a_letras(d.get('precio'))
        }
        res = renderizar_plantilla("PLANTILLA_LAPTOP", ctx)
        if res: archivos[f"{folio_lap}_{emp_row['codigo_str']}.docx"] = res

    if cpu_sel:
        folio_cpu = f"RESP-CPU-{cod_emp_clean}-{fecha_str}"
        d = cpu_sel['data']
        ctx = {**ctx_base,
            'folio': folio_cpu,  # 👈 INYECTA {{folio}} AL WORD
            'hostname': str(d.get('hostname', '') or ''), 'procesador': str(d.get('procesador', '') or ''),
            'memoria_ram': d.get('memoria_ram', ''), 'tipo_hdd': d.get('tipo_hdd', ''),
            'almacenamiento': d.get('almacenamiento', ''), 'condicion': d.get('cond_nom', d.get('condicion', '')),
            'comentarios': d.get('com_edit', d.get('comentarios', '')),
            'precio': formatear_precio(d.get('precio')),
            'precio_letras': precio_a_letras(d.get('precio'))
        }
        res = renderizar_plantilla("PLANTILLA_CPU", ctx)
        if res: archivos[f"{folio_cpu}_{emp_row['codigo_str']}.docx"] = res

    if mon_sel:
        folio_mon = f"RESP-MON-{cod_emp_clean}-{fecha_str}"
        d = mon_sel['data']
        ctx = {**ctx_base,
            'folio': folio_mon,  # 👈 INYECTA {{folio}} AL WORD
            'marca': str(d.get('marca', '') or ''), 'modelo': str(d.get('modelo', '') or ''),
            'numero_serie': d.get('numero_serie', ''),
            'comentarios': d.get('com_edit', d.get('comentarios', '')),
            'precio': formatear_precio(d.get('precio')),
            'precio_letras': precio_a_letras(d.get('precio'))
        }
        res = renderizar_plantilla("PLANTILLA_MONITOR", ctx)
        if res: archivos[f"{folio_mon}_{emp_row['codigo_str']}.docx"] = res

    if tab_sel:
        folio_tab = f"RESP-TAB-{cod_emp_clean}-{fecha_str}"
        d = tab_sel['data']
        ctx = {**ctx_base,
            'folio': folio_tab,  # 👈 INYECTA {{folio}} AL WORD
            'marca': d.get('marca', ''), 'modelo': str(d.get('modelo', '') or ''),
            'imei': str(d.get('imei', '') or ''), 'numero_serie': d.get('numero_serie', ''),
            'condicion': d.get('cond_nom', d.get('condicion', '')), 'cargador': d.get('carg_nom', d.get('cargador', '')),
            'comentarios': d.get('com_edit', d.get('comentarios', '')),
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

        # CONFIGURACIÓN Y EDICIÓN COMPLETA ANTES DE ENTREGAR
        if obj_cel or obj_lap or obj_cpu or obj_mon or obj_tab:
            st.divider()
            st.markdown("### ⚙️ Configuración y Estado del Equipo al Momento de Entrega")
            
            # 1. CELULAR
            if obj_cel:
                with st.expander("📱 Ajustar Datos del Celular", expanded=True):
                    d = obj_cel['data']
                    c_a, c_b, c_c = st.columns(3)
                    num_in = c_a.text_input("Número / Línea Asignada:", value=str(d.get('numero') or ''))
                    cond_nom = c_b.selectbox("Condición Celular:", list(dict_cond.keys()), index=list(dict_cond.values()).index(d['id_condicion']) if d.get('id_condicion') in dict_cond.values() else 0, key="cond_cel")
                    carg_nom = c_c.selectbox("Cargador Incluido:", list(dict_carg.keys()), index=list(dict_carg.values()).index(d['id_cargador']) if d.get('id_cargador') in dict_carg.values() else 0, key="carg_cel")
                    
                    c_d, c_e = st.columns(2)
                    caja_nom = c_d.selectbox("Caja Incluida:", list(dict_caja.keys()), index=list(dict_caja.values()).index(d['id_caja']) if d.get('id_caja') in dict_caja.values() else 0, key="caja_cel")
                    est_nom = c_e.selectbox("Estatus Celular:", list(dict_est_cel.keys()), index=list(dict_est_cel.keys()).index("ASIGNADO") if "ASIGNADO" in dict_est_cel else 0, key="est_cel")

                    ca, cb = st.columns(2)
                    obs_in = ca.text_input("Observaciones Celular:", value=str(d.get('observaciones') or ''), key="obs_cel")
                    com_in = cb.text_input("Comentarios Celular (va al Word):", value=str(d.get('comentarios') or ''), key="com_cel")

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
                    obs_in = ca.text_input("Observaciones Laptop:", value=str(d.get('observaciones') or ''), key="obs_lap")
                    com_in = cb.text_input("Comentarios Laptop (va al Word):", value=str(d.get('comentarios') or ''), key="com_lap")

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
                    obs_in = ca.text_input("Observaciones CPU:", value=str(d.get('observaciones') or ''), key="obs_cpu")
                    com_in = cb.text_input("Comentarios CPU (va al Word):", value=str(d.get('comentarios') or ''), key="com_cpu")

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
                    obs_in = ca.text_input("Observaciones Monitor:", value=str(d.get('observaciones') or ''), key="obs_mon")
                    com_in = cb.text_input("Comentarios Monitor (va al Word):", value=str(d.get('comentarios') or ''), key="com_mon")

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
                    obs_in = ca.text_input("Observaciones Tablet:", value=str(d.get('observaciones') or ''), key="obs_tab")
                    com_in = cb.text_input("Comentarios Tablet (va al Word):", value=str(d.get('comentarios') or ''), key="com_tab")

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

        conn = obtener_conexion()
        query_asignados = """
            SELECT 'celular' AS tipo, ic.imei AS id, ic.numero_serie, CONCAT(m.marca_modelo, ' (IMEI: ', ic.imei, ')') AS descripcion, 
                   CONCAT(e.nombre, ' ', e.apellido_paterno) AS asignado_a, ic.codigo_empleado
            FROM inventario_celulares ic
            JOIN empleados e ON ic.codigo_empleado = e.codigo
            JOIN modelos_celulares m ON ic.id_modelo = m.id_modelo
            WHERE ic.id_estatus_celular = 3

            UNION ALL

            SELECT 'laptop' AS tipo, il.numero_serie AS id, il.numero_serie, CONCAT(il.marca, ' ', il.modelo, ' [', il.hostname, ']'), 
                   CONCAT(e.nombre, ' ', e.apellido_paterno) AS asignado_a, il.codigo_empleado
            FROM inventario_laptops il
            JOIN empleados e ON il.codigo_empleado = e.codigo
            WHERE il.id_estatus_laptops = 3

            UNION ALL

            SELECT 'cpu' AS tipo, icp.hostname AS id, icp.numero_serie, CONCAT('CPU ', icp.marca, ' ', icp.modelo, ' [', icp.hostname, ']'), 
                   CONCAT(e.nombre, ' ', e.apellido_paterno) AS asignado_a, icp.codigo_empleado
            FROM inventario_cpu icp
            JOIN empleados e ON icp.codigo_empleado = e.codigo
            WHERE icp.id_estatus_cpu = 3

            UNION ALL

            SELECT 'monitor' AS tipo, im.numero_serie AS id, im.numero_serie, CONCAT('Monitor ', im.marca, ' ', im.modelo, ' (S/N: ', im.numero_serie, ')'), 
                   CONCAT(e.nombre, ' ', e.apellido_paterno) AS asignado_a, im.codigo_empleado
            FROM inventario_monitores im
            JOIN empleados e ON im.codigo_empleado = e.codigo
            WHERE im.id_estatus_monitor = 3

            UNION ALL

            SELECT 'tablet' AS tipo, it.numero_serie AS id, it.numero_serie, CONCAT('Tablet ', it.marca, ' ', it.modelo, ' (S/N: ', it.numero_serie, ')'), 
                   CONCAT(e.nombre, ' ', e.apellido_paterno) AS asignado_a, it.codigo_empleado
            FROM inventario_tablets it
            JOIN empleados e ON it.codigo_empleado = e.codigo
            WHERE it.id_estatus_tablet = 3
        """
        df_asig = pd.read_sql(query_asignados, conn)
        conn.close()

        if not df_asig.empty:
            lista_opciones = [
                f"[{row['tipo'].upper()}] - {row['descripcion']} ---> Asignado a: {row['asignado_a']}"
                for _, row in df_asig.iterrows()
            ]
            
            equipo_desv_sel = st.selectbox("Selecciona el equipo a recibir / desvincular:", lista_opciones)
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
                        exito = procesar_desvinculacion_equipo(
                            tipo_equipo=item_row['tipo'],
                            id_equipo=item_row['id'],
                            nuevo_estatus_id=dict_estatus_destino[destino_nom],
                            razon_motivo=motivo_txt
                        )
                        if exito:
                            st.toast(f"¡Equipo {item_row['id']} desvinculado con éxito!", icon="🎉")
                            st.rerun()
        else:
            st.info("No hay ningún equipo asignado actualmente en la base de datos.")