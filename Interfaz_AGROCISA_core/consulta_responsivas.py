import streamlit as st
import pandas as pd
from datetime import datetime
import responsivas
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

def limpiar_campo(val, defecto=""):
    """Elimina valores NaN, None o cadenas vacías antes de enviarlos al Word."""
    if pd.isna(val) or val is None:
        return defecto
    v_str = str(val).strip()
    if v_str.lower() in ["nan", "none", "null", "<na>", ""]:
        return defecto
    return v_str

def obtener_historial_completo_df():
    conn = obtener_conexion()
    if not conn:
        return pd.DataFrame()

    query_historial = """
        /* 1. CELULARES */
        SELECT 
            'celular' AS tipo_raw,
            '📱 Celular' AS tipo,
            rc.fecha_entrega,
            rc.codigo_empleado,
            CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS colaborador,
            COALESCE(s.nombre_sucursal, 'SIN SUCURSAL') AS sucursal,
            COALESCE(d.nombre_departamento, 'SIN DEPARTAMENTO') AS departamento,
            COALESCE(p.nombre_puesto, 'SIN PUESTO') AS puesto,
            ce.correo_gmail,
            ce.correo_corporativo,
            rc.imei AS id_equipo,
            COALESCE(rc.numero, '') AS numero_linea,
            COALESCE(m.marca_modelo, 'Celular') AS equipo_descripcion,
            COALESCE(m.marca_modelo, '') AS marca,
            '' AS modelo,
            '' AS hostname,
            '' AS procesador,
            '' AS memoria_ram,
            '' AS tipo_disco,
            '' AS almacenamiento,
            COALESCE(m.precio, 0) AS precio,
            COALESCE(ic.numero_serie, '') AS numero_serie,
            COALESCE(lt.gb_promocion_2026, lt.gb_2026, lt.gb_2024, '') AS gb,
            COALESCE(cond.condicion_opcion, 'Buenas condiciones') AS condicion,
            COALESCE(cg.cargador_opcion, 'SIN Cargador y SIN Cable') AS cargador,
            COALESCE(cj.caja_opcion, 'Sin caja') AS caja,
            COALESCE(ic.comentarios, '') AS comentarios,
            rc.id_status,
            COALESCE(er.estatus_responsiva, 'ACTIVO') AS estatus_doc,
            CONCAT('RESP-CEL-', LPAD(rc.codigo_empleado, 5, '0'), '-', DATE_FORMAT(rc.fecha_entrega, '%Y%m%d')) AS folio
        FROM responsivas_celulares rc
        JOIN empleados e ON rc.codigo_empleado = e.codigo
        LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
        LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento
        LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
        LEFT JOIN estatus_responsivas er ON rc.id_status = er.id_estatus_responsiva
        LEFT JOIN (
            SELECT 
                TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) AS cod_clean,
                MAX(CASE WHEN id_tipo_correo = 2 THEN direccion_correo END) AS correo_gmail,
                MAX(CASE WHEN id_tipo_correo = 1 THEN direccion_correo END) AS correo_corporativo
            FROM correos_electronicos
            WHERE id_estatus_correo = 1
            GROUP BY cod_clean
        ) ce ON TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR)) = ce.cod_clean
        LEFT JOIN inventario_celulares ic ON rc.imei = ic.imei
        LEFT JOIN modelos_celulares m ON ic.id_modelo = m.id_modelo
        LEFT JOIN condicion cond ON ic.id_condicion = cond.id_condicion
        LEFT JOIN cargadores cg ON ic.id_cargador = cg.id_cargador
        LEFT JOIN caja cj ON ic.id_caja = cj.id_caja
        LEFT JOIN lineas_telefonicas lt ON rc.numero = lt.numero

        UNION ALL

        /* 2. LAPTOPS */
        SELECT 
            'laptop' AS tipo_raw,
            '💻 Laptop' AS tipo,
            rl.fecha_entrega,
            rl.codigo_empleado,
            CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS colaborador,
            COALESCE(s.nombre_sucursal, 'SIN SUCURSAL') AS sucursal,
            COALESCE(d.nombre_departamento, 'SIN DEPARTAMENTO') AS departamento,
            COALESCE(p.nombre_puesto, 'SIN PUESTO') AS puesto,
            ce.correo_gmail,
            ce.correo_corporativo,
            rl.numero_serie AS id_equipo,
            '' AS numero_linea,
            CONCAT(COALESCE(il.marca, ''), ' ', COALESCE(il.modelo, ''), ' [', COALESCE(il.hostname, ''), ']') AS equipo_descripcion,
            COALESCE(il.marca, '') AS marca,
            COALESCE(il.modelo, '') AS modelo,
            COALESCE(il.hostname, '') AS hostname,
            COALESCE(il.procesador, '') AS procesador,
            COALESCE(il.memoria_ram, '') AS memoria_ram,
            COALESCE(ht.hdd_opcion, '') AS tipo_disco,
            COALESCE(il.almacenamiento, '') AS almacenamiento,
            COALESCE(il.precio, 0) AS precio,
            COALESCE(il.numero_serie, '') AS numero_serie,
            '' AS gb,
            COALESCE(cond.condicion_opcion, 'Buenas condiciones') AS condicion,
            COALESCE(cg.cargador_opcion, 'CON Cargador Original y Cable Original') AS cargador,
            '' AS caja,
            COALESCE(il.comentarios, '') AS comentarios,
            rl.id_status,
            COALESCE(er.estatus_responsiva, 'ACTIVO') AS estatus_doc,
            CONCAT('RESP-LAP-', LPAD(rl.codigo_empleado, 5, '0'), '-', DATE_FORMAT(rl.fecha_entrega, '%Y%m%d')) AS folio
        FROM responsivas_laptops rl
        JOIN empleados e ON rl.codigo_empleado = e.codigo
        LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
        LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento
        LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
        LEFT JOIN estatus_responsivas er ON rl.id_status = er.id_estatus_responsiva
        LEFT JOIN (
            SELECT 
                TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) AS cod_clean,
                MAX(CASE WHEN id_tipo_correo = 2 THEN direccion_correo END) AS correo_gmail,
                MAX(CASE WHEN id_tipo_correo = 1 THEN direccion_correo END) AS correo_corporativo
            FROM correos_electronicos
            WHERE id_estatus_correo = 1
            GROUP BY cod_clean
        ) ce ON TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR)) = ce.cod_clean
        LEFT JOIN inventario_laptops il ON rl.numero_serie = il.numero_serie
        LEFT JOIN hdd_tipo ht ON il.id_hdd_tipo = ht.id_hdd_tipo
        LEFT JOIN condicion cond ON il.id_condicion = cond.id_condicion
        LEFT JOIN cargadores cg ON il.id_cargador = cg.id_cargador

        UNION ALL

        /* 3. CPUS */
        SELECT 
            'cpu' AS tipo_raw,
            '🖥️ CPU' AS tipo,
            rcp.fecha_entrega,
            rcp.codigo_empleado,
            CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS colaborador,
            COALESCE(s.nombre_sucursal, 'SIN SUCURSAL') AS sucursal,
            COALESCE(d.nombre_departamento, 'SIN DEPARTAMENTO') AS departamento,
            COALESCE(p.nombre_puesto, 'SIN PUESTO') AS puesto,
            ce.correo_gmail,
            ce.correo_corporativo,
            COALESCE(icp.hostname, CAST(rcp.id_cpu AS CHAR)) AS id_equipo,
            '' AS numero_linea,
            CONCAT('CPU ', COALESCE(icp.marca, ''), ' ', COALESCE(icp.modelo, ''), ' [', COALESCE(icp.hostname, ''), ']') AS equipo_descripcion,
            COALESCE(icp.marca, '') AS marca,
            COALESCE(icp.modelo, '') AS modelo,
            COALESCE(icp.hostname, '') AS hostname,
            COALESCE(icp.procesador, '') AS procesador,
            COALESCE(icp.memoria_ram, '') AS memoria_ram,
            COALESCE(ht.hdd_opcion, '') AS tipo_disco,
            COALESCE(icp.almacenamiento, '') AS almacenamiento,
            COALESCE(icp.precio, 0) AS precio,
            COALESCE(icp.numero_serie, '') AS numero_serie,
            '' AS gb,
            COALESCE(cond.condicion_opcion, 'Buenas condiciones') AS condicion,
            '' AS cargador,
            '' AS caja,
            COALESCE(icp.comentarios, '') AS comentarios,
            rcp.id_status,
            COALESCE(er.estatus_responsiva, 'ACTIVO') AS estatus_doc,
            CONCAT('RESP-CPU-', LPAD(rcp.codigo_empleado, 5, '0'), '-', DATE_FORMAT(rcp.fecha_entrega, '%Y%m%d')) AS folio
        FROM responsivas_cpu rcp
        JOIN empleados e ON rcp.codigo_empleado = e.codigo
        LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
        LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento
        LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
        LEFT JOIN estatus_responsivas er ON rcp.id_status = er.id_estatus_responsiva
        LEFT JOIN (
            SELECT 
                TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) AS cod_clean,
                MAX(CASE WHEN id_tipo_correo = 2 THEN direccion_correo END) AS correo_gmail,
                MAX(CASE WHEN id_tipo_correo = 1 THEN direccion_correo END) AS correo_corporativo
            FROM correos_electronicos
            WHERE id_estatus_correo = 1
            GROUP BY cod_clean
        ) ce ON TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR)) = ce.cod_clean
        LEFT JOIN inventario_cpu icp ON rcp.id_cpu = icp.id_cpu
        LEFT JOIN hdd_tipo ht ON icp.id_hdd_tipo = ht.id_hdd_tipo
        LEFT JOIN condicion cond ON icp.id_condicion = cond.id_condicion

        UNION ALL

        /* 4. MONITORES */
        SELECT 
            'monitor' AS tipo_raw,
            '🖥️ Monitor' AS tipo,
            rm.fecha_entrega,
            rm.codigo_empleado,
            CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS colaborador,
            COALESCE(s.nombre_sucursal, 'SIN SUCURSAL') AS sucursal,
            COALESCE(d.nombre_departamento, 'SIN DEPARTAMENTO') AS departamento,
            COALESCE(p.nombre_puesto, 'SIN PUESTO') AS puesto,
            ce.correo_gmail,
            ce.correo_corporativo,
            rm.numero_serie AS id_equipo,
            '' AS numero_linea,
            CONCAT('Monitor ', COALESCE(im.marca, ''), ' ', COALESCE(im.modelo, '')) AS equipo_descripcion,
            COALESCE(im.marca, '') AS marca,
            COALESCE(im.modelo, '') AS modelo,
            COALESCE(im.hostname, '') AS hostname,
            '' AS procesador,
            '' AS memoria_ram,
            '' AS tipo_disco,
            '' AS almacenamiento,
            COALESCE(im.precio, 0) AS precio,
            COALESCE(im.numero_serie, '') AS numero_serie,
            '' AS gb,
            COALESCE(cond.condicion_opcion, 'Buenas condiciones') AS condicion,
            '' AS cargador,
            '' AS caja,
            COALESCE(im.comentarios, '') AS comentarios,
            rm.id_status,
            COALESCE(er.estatus_responsiva, 'ACTIVO') AS estatus_doc,
            CONCAT('RESP-MON-', LPAD(rm.codigo_empleado, 5, '0'), '-', DATE_FORMAT(rm.fecha_entrega, '%Y%m%d')) AS folio
        FROM responsivas_monitores rm
        JOIN empleados e ON rm.codigo_empleado = e.codigo
        LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
        LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento
        LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
        LEFT JOIN estatus_responsivas er ON rm.id_status = er.id_estatus_responsiva
        LEFT JOIN (
            SELECT 
                TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) AS cod_clean,
                MAX(CASE WHEN id_tipo_correo = 2 THEN direccion_correo END) AS correo_gmail,
                MAX(CASE WHEN id_tipo_correo = 1 THEN direccion_correo END) AS correo_corporativo
            FROM correos_electronicos
            WHERE id_estatus_correo = 1
            GROUP BY cod_clean
        ) ce ON TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR)) = ce.cod_clean
        LEFT JOIN inventario_monitores im ON rm.numero_serie = im.numero_serie
        LEFT JOIN condicion cond ON im.id_condicion = cond.id_condicion

        UNION ALL

        /* 5. TABLETS */
        SELECT 
            'tablet' AS tipo_raw,
            '📱 Tablet' AS tipo,
            rt.fecha_entrega,
            rt.codigo_empleado,
            CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS colaborador,
            COALESCE(s.nombre_sucursal, 'SIN SUCURSAL') AS sucursal,
            COALESCE(d.nombre_departamento, 'SIN DEPARTAMENTO') AS departamento,
            COALESCE(p.nombre_puesto, 'SIN PUESTO') AS puesto,
            ce.correo_gmail,
            ce.correo_corporativo,
            rt.numero_serie AS id_equipo,
            '' AS numero_linea,
            CONCAT('Tablet ', COALESCE(it.marca, ''), ' ', COALESCE(it.modelo, '')) AS equipo_descripcion,
            COALESCE(it.marca, '') AS marca,
            COALESCE(it.modelo, '') AS modelo,
            '' AS hostname,
            '' AS procesador,
            '' AS memoria_ram,
            '' AS tipo_disco,
            '' AS almacenamiento,
            COALESCE(it.precio, 0) AS precio,
            COALESCE(it.numero_serie, '') AS numero_serie,
            '' AS gb,
            COALESCE(cond.condicion_opcion, 'Buenas condiciones') AS condicion,
            COALESCE(cg.cargador_opcion, 'CON Cargador Original y Cable Original') AS cargador,
            '' AS caja,
            COALESCE(it.comentarios, '') AS comentarios,
            rt.id_status,
            COALESCE(er.estatus_responsiva, 'ACTIVO') AS estatus_doc,
            CONCAT('RESP-TAB-', LPAD(rt.codigo_empleado, 5, '0'), '-', DATE_FORMAT(rt.fecha_entrega, '%Y%m%d')) AS folio
        FROM responsivas_tablets rt
        JOIN empleados e ON rt.codigo_empleado = e.codigo
        LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
        LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento
        LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
        LEFT JOIN estatus_responsivas er ON rt.id_status = er.id_estatus_responsiva
        LEFT JOIN (
            SELECT 
                TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) AS cod_clean,
                MAX(CASE WHEN id_tipo_correo = 2 THEN direccion_correo END) AS correo_gmail,
                MAX(CASE WHEN id_tipo_correo = 1 THEN direccion_correo END) AS correo_corporativo
            FROM correos_electronicos
            WHERE id_estatus_correo = 1
            GROUP BY cod_clean
        ) ce ON TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR)) = ce.cod_clean
        LEFT JOIN inventario_tablets it ON rt.numero_serie = it.numero_serie
        LEFT JOIN condicion cond ON it.id_condicion = cond.id_condicion
        LEFT JOIN cargadores cg ON it.id_cargador = cg.id_cargador

        ORDER BY fecha_entrega DESC
    """
    df = pd.read_sql(query_historial, conn)
    conn.close()
    return df

def generar_docx_reimpresion(row_data):
    ctx_base = {
        'folio': limpiar_campo(row_data['folio']),
        'fecha_entrega': responsivas.format_fecha(row_data['fecha_entrega']),
        'empleado': limpiar_campo(row_data['colaborador']).title(),
        'sucursal': limpiar_campo(row_data['sucursal'], 'S/D'),
        'departamento': limpiar_campo(row_data['departamento'], 'S/D'),
        'puesto': limpiar_campo(row_data['puesto'], 'S/D'),
        'correo_gmail': limpiar_campo(row_data['correo_gmail'], ''),
        'correo_corporativo': limpiar_campo(row_data['correo_corporativo'], '')
    }

    t_raw = row_data['tipo_raw']

    if t_raw == 'celular':
        ctx = {**ctx_base, 
            'equipo': limpiar_campo(row_data['equipo_descripcion']), 
            'numero': limpiar_campo(row_data['numero_linea']),
            'imei': limpiar_campo(row_data['id_equipo']), 
            'numero_serie': limpiar_campo(row_data['numero_serie']),
            'gb': limpiar_campo(row_data['gb']), 
            'condicion': limpiar_campo(row_data['condicion'], 'Buenas condiciones'),
            'cargador': limpiar_campo(row_data['cargador'], 'CON Cargador Original y Cable Original'), 
            'caja': limpiar_campo(row_data['caja'], 'Con caja'),
            'comentarios': limpiar_campo(row_data['comentarios']),
            'precio': responsivas.formatear_precio(row_data['precio']),
            'precio_letras': responsivas.precio_a_letras(row_data['precio'])
        }
        return responsivas.renderizar_plantilla("PLANTILLA_CELULAR", ctx)

    elif t_raw == 'laptop':
        ctx = {**ctx_base,
            'marca': limpiar_campo(row_data['marca']), 
            'modelo': limpiar_campo(row_data['modelo']),
            'hostname': limpiar_campo(row_data['hostname']),
            'numero_serie': limpiar_campo(row_data['numero_serie']), 
            'procesador': limpiar_campo(row_data['procesador']),
            'memoria_ram': limpiar_campo(row_data['memoria_ram']),
            'tipo_hdd': limpiar_campo(row_data['tipo_disco']),
            'almacenamiento': limpiar_campo(row_data['almacenamiento']),
            'condicion_lap': limpiar_campo(row_data['condicion'], 'Buenas condiciones'),
            'cargador': limpiar_campo(row_data['cargador'], 'CON Cargador Original y Cable Original'),
            'comentarios': limpiar_campo(row_data['comentarios']),
            'precio': responsivas.formatear_precio(row_data['precio']),
            'precio_letras': responsivas.precio_a_letras(row_data['precio'])
        }
        return responsivas.renderizar_plantilla("PLANTILLA_LAPTOP", ctx)

    elif t_raw == 'cpu':
        ctx = {**ctx_base,
            'marca': limpiar_campo(row_data['marca']),
            'modelo': limpiar_campo(row_data['modelo']),
            'hostname': limpiar_campo(row_data['hostname']), 
            'numero_serie': limpiar_campo(row_data['numero_serie']),
            'procesador': limpiar_campo(row_data['procesador']),
            'memoria_ram': limpiar_campo(row_data['memoria_ram']), 
            'tipo_hdd': limpiar_campo(row_data['tipo_disco']), 
            'almacenamiento': limpiar_campo(row_data['almacenamiento']),
            'condicion': limpiar_campo(row_data['condicion'], 'Buenas condiciones'),
            'comentarios': limpiar_campo(row_data['comentarios']),
            'precio': responsivas.formatear_precio(row_data['precio']),
            'precio_letras': responsivas.precio_a_letras(row_data['precio'])
        }
        return responsivas.renderizar_plantilla("PLANTILLA_CPU", ctx)

    elif t_raw == 'monitor':
        ctx = {**ctx_base,
            'marca': limpiar_campo(row_data['marca']), 
            'modelo': limpiar_campo(row_data['modelo']),
            'hostname': limpiar_campo(row_data['hostname']),
            'numero_serie': limpiar_campo(row_data['numero_serie']),
            'condicion': limpiar_campo(row_data['condicion'], 'Buenas condiciones'),
            'comentarios': limpiar_campo(row_data['comentarios']),
            'precio': responsivas.formatear_precio(row_data['precio']),
            'precio_letras': responsivas.precio_a_letras(row_data['precio'])
        }
        return responsivas.renderizar_plantilla("PLANTILLA_MONITOR", ctx)

    elif t_raw == 'tablet':
        ctx = {**ctx_base,
            'marca': limpiar_campo(row_data['marca']), 
            'modelo': limpiar_campo(row_data['modelo']),
            'imei': limpiar_campo(row_data['id_equipo']), 
            'numero_serie': limpiar_campo(row_data['numero_serie']),
            'condicion': limpiar_campo(row_data['condicion'], 'Buenas condiciones'), 
            'cargador': limpiar_campo(row_data['cargador'], 'CON Cargador Original y Cable Original'),
            'comentarios': limpiar_campo(row_data['comentarios']),
            'precio': responsivas.formatear_precio(row_data['precio']),
            'precio_letras': responsivas.precio_a_letras(row_data['precio'])
        }
        return responsivas.renderizar_plantilla("PLANTILLA_TABLET", ctx)

    return None

def render_consulta():
    aplicar_estilos_pantalla()
    st.title("🔍 Historial y Re-impresión de Responsivas")

    df_historial = obtener_historial_completo_df()

    if df_historial.empty:
        st.info("No hay historial de responsivas registrado en la base de datos.")
        return

    # Mapeo visual del estatus directo de MariaDB
    df_historial["Estatus Documento"] = df_historial["estatus_doc"].apply(
        lambda x: f"🟢 {x}" if str(x).upper() == "ACTIVO" else f"🔴 {x}"
    )

    c1, c2, c3 = st.columns([1.5, 1, 1])
    with c1:
        colaboradores = ["Todos"] + sorted(list(df_historial["colaborador"].dropna().unique()))
        emp_sel = st.selectbox("Filtrar por Colaborador:", colaboradores)
    with c2:
        tipos_disp = ["Todos"] + sorted(list(df_historial["tipo"].dropna().unique()))
        tipo_sel = st.selectbox("Filtrar por Tipo de Equipo:", tipos_disp)
    with c3:
        estatus_opts = ["Todos"] + sorted(list(df_historial["Estatus Documento"].dropna().unique()))
        estatus_sel = st.selectbox("Filtrar por Estatus:", estatus_opts)

    df_filtrado = df_historial.copy()
    if emp_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["colaborador"] == emp_sel]
    if tipo_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["tipo"] == tipo_sel]
    if estatus_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Estatus Documento"] == estatus_sel]

    df_filtrado = df_filtrado.reset_index(drop=True)

    st.divider()

    st.dataframe(
        df_filtrado[["folio", "fecha_entrega", "colaborador", "tipo", "id_equipo", "equipo_descripcion", "Estatus Documento"]].rename(
            columns={
                "folio": "Folio",
                "fecha_entrega": "Fecha de Entrega",
                "colaborador": "Colaborador Asignado",
                "tipo": "Tipo de Hardware",
                "id_equipo": "Identificador / Serie / IMEI",
                "equipo_descripcion": "Descripción del Equipo",
                "Estatus Documento": "Estatus"
            }
        ),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.markdown("### 🖨️ Re-generar Documento DOCX por Folio")
    
    if not df_filtrado.empty:
        def formatear_opcion(i):
            r = df_filtrado.iloc[i]
            id_txt = f" (ID/IMEI: {r['id_equipo']})" if r['id_equipo'] else ""
            return f"{r['folio']} | {r['colaborador']} - {r['tipo']} {r['equipo_descripcion']}{id_txt} [{r['Estatus Documento']}]"

        idx_sel = st.selectbox(
            "Selecciona la carta responsiva a descargar:",
            options=range(len(df_filtrado)),
            format_func=formatear_opcion,
            key="sel_reimpresion_responsiva"
        )

        row_sel = df_filtrado.iloc[idx_sel]
        buffer_docx = generar_docx_reimpresion(row_sel)

        if buffer_docx:
            st.download_button(
                label=f"📥 Descargar Documento ({row_sel['folio']}.docx)",
                data=buffer_docx,
                file_name=f"{row_sel['folio']}_{row_sel['colaborador'].replace(' ', '_')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary"
            )
        else:
            st.error("No se pudo generar el archivo. Verifica que las plantillas .docx existan en la ruta correspondiente.")

render = render_consulta