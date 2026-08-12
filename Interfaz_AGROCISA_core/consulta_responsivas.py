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
    """Elimina valores NaN, None o cadenas 'nan' de Pandas antes de enviarlos a Word."""
    if pd.isna(val) or val is None:
        return defecto
    v_str = str(val).strip()
    if v_str.lower() in ["nan", "none", "null", "<na>"]:
        return defecto
    return v_str

def obtener_historial_completo_df():
    conn = obtener_conexion()
    if not conn:
        return pd.DataFrame()

    query_historial = """
        SELECT 
            'celular' AS tipo_raw, '📱 Celular' AS tipo, rc.fecha_entrega, rc.codigo_empleado,
            CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS colaborador,
            s.nombre_sucursal AS sucursal, d.nombre_departamento AS departamento, p.nombre_puesto AS puesto,
            ce.correo_gmail, ce.correo_corporativo,
            rc.imei AS id_equipo, rc.numero AS numero_linea, m.marca_modelo AS equipo_descripcion, m.precio,
            ic.numero_serie, lt.gb_promocion_2026 AS gb, cond.condicion_opcion AS condicion,
            cg.cargador_opcion AS cargador, cj.caja_opcion AS caja, ic.comentarios,
            rc.id_status, CONCAT('RESP-CEL-', LPAD(rc.codigo_empleado, 5, '0'), '-', DATE_FORMAT(rc.fecha_entrega, '%Y%m%d')) AS folio
        FROM responsivas_celulares rc
        JOIN empleados e ON rc.codigo_empleado = e.codigo
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
        LEFT JOIN inventario_celulares ic ON rc.imei = ic.imei
        LEFT JOIN modelos_celulares m ON ic.id_modelo = m.id_modelo
        LEFT JOIN condicion cond ON ic.id_condicion = cond.id_condicion
        LEFT JOIN cargadores cg ON ic.id_cargador = cg.id_cargador
        LEFT JOIN caja cj ON ic.id_caja = cj.id_caja
        LEFT JOIN lineas_telefonicas lt ON rc.numero = lt.numero

        UNION ALL

        SELECT 
            'laptop' AS tipo_raw, '💻 Laptop' AS tipo, rl.fecha_entrega, rl.codigo_empleado,
            CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS colaborador,
            s.nombre_sucursal AS sucursal, d.nombre_departamento AS departamento, p.nombre_puesto AS puesto,
            ce.correo_gmail, ce.correo_corporativo,
            rl.numero_serie AS id_equipo, '' AS numero_linea, CONCAT(il.marca, ' ', il.modelo, ' [', il.hostname, ']') AS equipo_descripcion, 0 AS precio,
            il.numero_serie, '' AS gb, cond.condicion_opcion AS condicion,
            cg.cargador_opcion AS cargador, '' AS caja, il.comentarios,
            rl.id_status, CONCAT('RESP-LAP-', LPAD(rl.codigo_empleado, 5, '0'), '-', DATE_FORMAT(rl.fecha_entrega, '%Y%m%d')) AS folio
        FROM responsivas_laptops rl
        JOIN empleados e ON rl.codigo_empleado = e.codigo
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
        LEFT JOIN inventario_laptops il ON rl.numero_serie = il.numero_serie
        LEFT JOIN condicion cond ON il.id_condicion = cond.id_condicion
        LEFT JOIN cargadores cg ON il.id_cargador = cg.id_cargador

        UNION ALL

        SELECT 
            'cpu' AS tipo_raw, '🖥️ CPU' AS tipo, rcp.fecha_entrega, rcp.codigo_empleado,
            CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS colaborador,
            s.nombre_sucursal AS sucursal, d.nombre_departamento AS departamento, p.nombre_puesto AS puesto,
            ce.correo_gmail, ce.correo_corporativo,
            COALESCE(icp.hostname, 'S/H') AS id_equipo, '' AS numero_linea, CONCAT('CPU ', COALESCE(icp.marca, ''), ' ', COALESCE(icp.modelo, ''), ' [', COALESCE(icp.hostname, ''), ']') AS equipo_descripcion, 0 AS precio,
            icp.numero_serie, '' AS gb, cond.condicion_opcion AS condicion,
            '' AS cargador, '' AS caja, icp.comentarios,
            rcp.id_status, CONCAT('RESP-CPU-', LPAD(rcp.codigo_empleado, 5, '0'), '-', DATE_FORMAT(rcp.fecha_entrega, '%Y%m%d')) AS folio
        FROM responsivas_cpu rcp
        JOIN empleados e ON rcp.codigo_empleado = e.codigo
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
        LEFT JOIN inventario_cpu icp ON rcp.id_cpu = icp.id_cpu
        LEFT JOIN condicion cond ON icp.id_condicion = cond.id_condicion

        UNION ALL

        SELECT 
            'monitor' AS tipo_raw, '🖥️ Monitor' AS tipo, rm.fecha_entrega, rm.codigo_empleado,
            CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS colaborador,
            s.nombre_sucursal AS sucursal, d.nombre_departamento AS departamento, p.nombre_puesto AS puesto,
            ce.correo_gmail, ce.correo_corporativo,
            rm.numero_serie AS id_equipo, '' AS numero_linea, CONCAT('Monitor ', im.marca, ' ', im.modelo) AS equipo_descripcion, 0 AS precio,
            im.numero_serie, '' AS gb, cond.condicion_opcion AS condicion,
            '' AS cargador, '' AS caja, im.comentarios,
            rm.id_status, CONCAT('RESP-MON-', LPAD(rm.codigo_empleado, 5, '0'), '-', DATE_FORMAT(rm.fecha_entrega, '%Y%m%d')) AS folio
        FROM responsivas_monitores rm
        JOIN empleados e ON rm.codigo_empleado = e.codigo
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
        LEFT JOIN inventario_monitores im ON rm.numero_serie = im.numero_serie
        LEFT JOIN condicion cond ON im.id_condicion = cond.id_condicion

        UNION ALL

        SELECT 
            'tablet' AS tipo_raw, '📱 Tablet' AS tipo, rt.fecha_entrega, rt.codigo_empleado,
            CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS colaborador,
            s.nombre_sucursal AS sucursal, d.nombre_departamento AS departamento, p.nombre_puesto AS puesto,
            ce.correo_gmail, ce.correo_corporativo,
            rt.numero_serie AS id_equipo, '' AS numero_linea, CONCAT('Tablet ', it.marca, ' ', it.modelo) AS equipo_descripcion, 0 AS precio,
            it.numero_serie, '' AS gb, cond.condicion_opcion AS condicion,
            cg.cargador_opcion AS cargador, '' AS caja, it.comentarios,
            rt.id_status, CONCAT('RESP-TAB-', LPAD(rt.codigo_empleado, 5, '0'), '-', DATE_FORMAT(rt.fecha_entrega, '%Y%m%d')) AS folio
        FROM responsivas_tablets rt
        JOIN empleados e ON rt.codigo_empleado = e.codigo
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
            'condicion': limpiar_campo(row_data['condicion'], 'Bueno'),
            'cargador': limpiar_campo(row_data['cargador'], 'Sí'), 
            'caja': limpiar_campo(row_data['caja'], 'Sí'),
            'comentarios': limpiar_campo(row_data['comentarios']),
            'precio': responsivas.formatear_precio(row_data['precio']),
            'precio_letras': responsivas.precio_a_letras(row_data['precio'])
        }
        return responsivas.renderizar_plantilla("PLANTILLA_CELULAR", ctx)

    elif t_raw == 'laptop':
        ctx = {**ctx_base,
            'marca': limpiar_campo(row_data['equipo_descripcion']), 
            'modelo': '',
            'numero_serie': limpiar_campo(row_data['id_equipo']), 
            'condicion_lap': limpiar_campo(row_data['condicion'], 'Bueno'),
            'cargador': limpiar_campo(row_data['cargador'], 'Sí'),
            'comentarios': limpiar_campo(row_data['comentarios']),
            'precio': responsivas.formatear_precio(row_data['precio']),
            'precio_letras': responsivas.precio_a_letras(row_data['precio'])
        }
        return responsivas.renderizar_plantilla("PLANTILLA_LAPTOP", ctx)

    elif t_raw == 'cpu':
        ctx = {**ctx_base,
            'hostname': limpiar_campo(row_data['id_equipo']), 
            'procesador': '',
            'memoria_ram': '', 
            'tipo_hdd': '', 
            'almacenamiento': '',
            'condicion': limpiar_campo(row_data['condicion'], 'Bueno'),
            'comentarios': limpiar_campo(row_data['comentarios']),
            'precio': responsivas.formatear_precio(row_data['precio']),
            'precio_letras': responsivas.precio_a_letras(row_data['precio'])
        }
        return responsivas.renderizar_plantilla("PLANTILLA_CPU", ctx)

    elif t_raw == 'monitor':
        ctx = {**ctx_base,
            'marca': limpiar_campo(row_data['equipo_descripcion']), 
            'modelo': '',
            'numero_serie': limpiar_campo(row_data['id_equipo']),
            'comentarios': limpiar_campo(row_data['comentarios']),
            'precio': responsivas.formatear_precio(row_data['precio']),
            'precio_letras': responsivas.precio_a_letras(row_data['precio'])
        }
        return responsivas.renderizar_plantilla("PLANTILLA_MONITOR", ctx)

    elif t_raw == 'tablet':
        ctx = {**ctx_base,
            'marca': limpiar_campo(row_data['equipo_descripcion']), 
            'modelo': '',
            'imei': limpiar_campo(row_data['id_equipo']), 
            'numero_serie': limpiar_campo(row_data['numero_serie']),
            'condicion': limpiar_campo(row_data['condicion'], 'Bueno'), 
            'cargador': limpiar_campo(row_data['cargador'], 'Sí'),
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
        st.info("No hay historial de responsivas registrado.")
        return

    df_historial["Estatus Documento"] = df_historial["id_status"].apply(
        lambda x: "🟢 VIGENTE" if x == 1 else "🔴 INACTIVO / DEVUELTO"
    )

    c1, c2 = st.columns(2)
    with c1:
        colaboradores = ["Todos"] + sorted(list(df_historial["colaborador"].dropna().unique()))
        emp_sel = st.selectbox("Filtrar por Colaborador:", colaboradores)
    with c2:
        estatus_sel = st.selectbox("Filtrar por Estatus:", ["Todos", "🟢 VIGENTE", "🔴 INACTIVO / DEVUELTO"])

    df_filtrado = df_historial.copy()
    if emp_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["colaborador"] == emp_sel]
    if estatus_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Estatus Documento"] == estatus_sel]

    st.divider()

    st.dataframe(
        df_filtrado[["folio", "fecha_entrega", "colaborador", "tipo", "equipo_descripcion", "Estatus Documento"]],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.markdown("### 🖨️ Re-generar Documento DOCX por Folio")
    
    if not df_filtrado.empty:
        opts_folios = [f"{r['folio']} | {r['colaborador']} - {r['tipo']} ({r['equipo_descripcion']})" for _, r in df_filtrado.iterrows()]
        folio_sel_str = st.selectbox("Selecciona la carta responsiva a descargar:", opts_folios)

        folio_codigo = folio_sel_str.split(" | ")[0]
        row_sel = df_filtrado[df_filtrado["folio"] == folio_codigo].iloc[0]

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
            st.error("No se pudo generar el archivo. Verifica las plantillas .docx en el servidor.")

# Alias para compatibilidad de invocación en app.py
render = render_consulta