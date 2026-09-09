import io
from datetime import datetime
import pandas as pd
import streamlit as st
import plotly.express as px
from database import obtener_conexion
from estilos_dashboard import aplicar_estilo_sb_admin
import sync_drive

# ==============================================================================
# 1. GENERADOR DE GRÁFICA DE DONA (DONUT CHART)
# ==============================================================================
def generar_grafica_dona(df_kpi):
    if df_kpi.empty:
        return None
    
    conteo = df_kpi['Categoria'].value_counts().reset_index()
    conteo.columns = ['Categoría', 'Cantidad']

    fig = px.pie(
        conteo, 
        values='Cantidad', 
        names='Categoría', 
        hole=0.6,
        color_discrete_sequence=['#3b82f6', '#10b981', '#06b6d4', '#f59e0b', '#8b5cf6']
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e2e8f0', size=13),
        showlegend=True,
        margin=dict(t=10, b=10, l=10, r=10),
        height=280,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return fig

# ==============================================================================
# 2. CONSULTAS DE MÉTRICAS Y DASHBOARD GENERAL
# ==============================================================================
def obtener_kpis_inventario():
    try:
        conn = obtener_conexion()
        if not conn:
            return 0, 0, 0, 0, pd.DataFrame()

        query = """
            SELECT 'Celulares' AS Categoria, id_estatus_celular AS estatus FROM inventario_celulares
            UNION ALL
            SELECT 'Laptops' AS Categoria, id_estatus_laptops AS estatus FROM inventario_laptops
            UNION ALL
            SELECT 'CPUs' AS Categoria, id_estatus_cpu AS estatus FROM inventario_cpu
            UNION ALL
            SELECT 'Monitores' AS Categoria, id_estatus_monitor AS estatus FROM inventario_monitores
            UNION ALL
            SELECT 'Tablets' AS Categoria, id_estatus_tablet AS estatus FROM inventario_tablets
        """
        df = pd.read_sql(query, conn)
        conn.close()

        total_equipos = len(df)
        asignados = len(df[df['estatus'] == 3])
        disponibles = len(df[df['estatus'] == 4])
        mantenimiento = len(df[df['estatus'].isin([5, 6])])

        return total_equipos, asignados, disponibles, mantenimiento, df
    except Exception as e:
        st.error(f"⚠️ Error al calcular KPIs: {e}")
        return 0, 0, 0, 0, pd.DataFrame()

def obtener_equipos_por_colaborador(codigo_empleado):
    conn = obtener_conexion()
    if not conn:
        return pd.DataFrame()

    cod_clean = str(codigo_empleado).strip().lstrip('0')
    try:
        q_cel = """
            SELECT '📱 Celular' AS Tipo, CONCAT(COALESCE(m.marca_modelo, 'Celular'), ' (IMEI: ', ic.imei, ')') AS Equipo, 
                   COALESCE(ic.numero, 'Sin Línea') AS Identificador_Serie, COALESCE(c.condicion_opcion, 'Buenas condiciones') AS Condicion
            FROM inventario_celulares ic
            LEFT JOIN modelos_celulares m ON ic.id_modelo = m.id_modelo
            LEFT JOIN condicion c ON ic.id_condicion = c.id_condicion
            WHERE TRIM(LEADING '0' FROM CAST(ic.codigo_empleado AS CHAR)) = %s
        """
        q_lap = """
            SELECT '💻 Laptop' AS Tipo, CONCAT(COALESCE(il.marca, ''), ' ', COALESCE(il.modelo, ''), ' [', COALESCE(il.hostname, ''), ']') AS Equipo, 
                   il.numero_serie AS Identificador_Serie, COALESCE(c.condicion_opcion, 'Buenas condiciones') AS Condicion
            FROM inventario_laptops il
            LEFT JOIN condicion c ON il.id_condicion = c.id_condicion
            WHERE TRIM(LEADING '0' FROM CAST(il.codigo_empleado AS CHAR)) = %s
        """
        q_cpu = """
            SELECT '🖥️ CPU' AS Tipo, CONCAT('CPU ', COALESCE(icp.marca, ''), ' ', COALESCE(icp.modelo, ''), ' [', COALESCE(icp.hostname, ''), ']') AS Equipo, 
                   COALESCE(icp.numero_serie, icp.hostname) AS Identificador_Serie, COALESCE(c.condicion_opcion, 'Buenas condiciones') AS Condicion
            FROM inventario_cpu icp
            LEFT JOIN condicion c ON icp.id_condicion = c.id_condicion
            WHERE TRIM(LEADING '0' FROM CAST(icp.codigo_empleado AS CHAR)) = %s
        """
        q_mon = """
            SELECT '🖥️ Monitor' AS Tipo, CONCAT('Monitor ', COALESCE(im.marca, ''), ' ', COALESCE(im.modelo, '')) AS Equipo, 
                   im.numero_serie AS Identificador_Serie, COALESCE(c.condicion_opcion, 'Buenas condiciones') AS Condicion
            FROM inventario_monitores im
            LEFT JOIN condicion c ON im.id_condicion = c.id_condicion
            WHERE TRIM(LEADING '0' FROM CAST(im.codigo_empleado AS CHAR)) = %s
        """
        q_tab = """
            SELECT '📱 Tablet' AS Tipo, CONCAT('Tablet ', COALESCE(it.marca, ''), ' ', COALESCE(it.modelo, '')) AS Equipo, 
                   it.numero_serie AS Identificador_Serie, COALESCE(c.condicion_opcion, 'Buenas condiciones') AS Condicion
            FROM inventario_tablets it
            LEFT JOIN condicion c ON it.id_condicion = c.id_condicion
            WHERE TRIM(LEADING '0' FROM CAST(it.codigo_empleado AS CHAR)) = %s
        """

        dfs = []
        for q in [q_cel, q_lap, q_cpu, q_mon, q_tab]:
            df_part = pd.read_sql(q, conn, params=(cod_clean,))
            if not df_part.empty:
                dfs.append(df_part)

        conn.close()
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    except Exception as e:
        conn.close()
        st.error(f"⚠️ Error al consultar equipos del empleado: {e}")
        return pd.DataFrame()

def obtener_reporte_lineas_df():
    try:
        conn = obtener_conexion()
        query = """
            SELECT 
                lt.numero AS `Línea Telefónica`,
                COALESCE(CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno), 'SIN ASIGNAR') AS Colaborador,
                COALESCE(s.nombre_sucursal, 'SIN SUCURSAL') AS Sucursal,
                COALESCE(d.nombre_departamento, 'SIN DEPARTAMENTO') AS Departamento,
                COALESCE(p.nombre_puesto, 'SIN PUESTO') AS Puesto,
                COALESCE(lt.plan_2026, lt.plan_2024, '4') AS Plan,
                COALESCE(elt.estatus_linea, 'ACTIVO') AS Estatus,
                COALESCE(m.marca_modelo, 'Línea / Chip Suelto') AS `Modelo Equipo`,
                COALESCE(ic.imei, 'S/I') AS IMEI
            FROM lineas_telefonicas lt
            LEFT JOIN empleados e ON TRIM(LEADING '0' FROM CAST(lt.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR))
            LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
            LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento
            LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
            LEFT JOIN estatus_linea_telefonica elt ON lt.id_estatus_linea = elt.id_estatus_linea
            LEFT JOIN inventario_celulares ic ON lt.numero = ic.numero
            LEFT JOIN modelos_celulares m ON ic.id_modelo = m.id_modelo
            ORDER BY e.nombre ASC, lt.numero ASC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error en reporte de líneas: {e}")
        return pd.DataFrame()

def obtener_dispositivos_disponibles_df():
    """Consulta modular de stock disponible sin UNION SQL para prevenir errores de colación."""
    conn = obtener_conexion()
    if not conn:
        return pd.DataFrame()

    try:
        q_cel = """
            SELECT '📱 Celular' AS Categoria, COALESCE(m.marca_modelo, 'Celular') AS Descripcion, 
                   ic.imei AS `Serie / Identificador`, COALESCE(c.condicion_opcion, 'Buenas condiciones') AS Condicion, 
                   COALESCE(ic.observaciones, '') AS Observaciones
            FROM inventario_celulares ic
            LEFT JOIN modelos_celulares m ON ic.id_modelo = m.id_modelo
            LEFT JOIN condicion c ON ic.id_condicion = c.id_condicion
            WHERE ic.id_estatus_celular = 4
        """
        q_lap = """
            SELECT '💻 Laptop' AS Categoria, CONCAT(COALESCE(il.marca, ''), ' ', COALESCE(il.modelo, ''), ' [', COALESCE(il.hostname, ''), ']') AS Descripcion, 
                   il.numero_serie AS `Serie / Identificador`, COALESCE(c.condicion_opcion, 'Buenas condiciones') AS Condicion, 
                   COALESCE(il.observaciones, '') AS Observaciones
            FROM inventario_laptops il
            LEFT JOIN condicion c ON il.id_condicion = c.id_condicion
            WHERE il.id_estatus_laptops = 4
        """
        q_cpu = """
            SELECT '🖥️ CPU' AS Categoria, CONCAT('CPU ', COALESCE(icp.marca, ''), ' ', COALESCE(icp.modelo, ''), ' [', COALESCE(icp.hostname, ''), ']') AS Descripcion, 
                   COALESCE(icp.hostname, CAST(icp.id_cpu AS CHAR)) AS `Serie / Identificador`, COALESCE(c.condicion_opcion, 'Buenas condiciones') AS Condicion, 
                   COALESCE(icp.observaciones, '') AS Observaciones
            FROM inventario_cpu icp
            LEFT JOIN condicion c ON icp.id_condicion = c.id_condicion
            WHERE icp.id_estatus_cpu = 4
        """
        q_mon = """
            SELECT '🖥️ Monitor' AS Categoria, CONCAT('Monitor ', COALESCE(im.marca, ''), ' ', COALESCE(im.modelo, '')) AS Descripcion, 
                   im.numero_serie AS `Serie / Identificador`, COALESCE(c.condicion_opcion, 'Buenas condiciones') AS Condicion, 
                   COALESCE(im.observaciones, '') AS Observaciones
            FROM inventario_monitores im
            LEFT JOIN condicion c ON im.id_condicion = c.id_condicion
            WHERE im.id_estatus_monitor = 4
        """
        q_tab = """
            SELECT '📱 Tablet' AS Categoria, CONCAT('Tablet ', COALESCE(it.marca, ''), ' ', COALESCE(it.modelo, '')) AS Descripcion, 
                   it.numero_serie AS `Serie / Identificador`, COALESCE(c.condicion_opcion, 'Buenas condiciones') AS Condicion, 
                   COALESCE(it.observaciones, '') AS Observaciones
            FROM inventario_tablets it
            LEFT JOIN condicion c ON it.id_condicion = c.id_condicion
            WHERE it.id_estatus_tablet = 4
        """

        dfs = []
        for q in [q_cel, q_lap, q_cpu, q_mon, q_tab]:
            df_p = pd.read_sql(q, conn)
            if not df_p.empty:
                dfs.append(df_p)

        conn.close()
        return pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()
    except Exception as e:
        conn.close()
        st.error(f"⚠️ Error al obtener disponibles: {e}")
        return pd.DataFrame()

def obtener_lista_distribucion_df():
    try:
        conn = obtener_conexion()
        query = """
            SELECT 
                CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS Nombre,
                COALESCE(s.nombre_sucursal, 'SIN SUCURSAL') AS Sucursal,
                COALESCE(d.nombre_departamento, 'SIN DEPARTAMENTO') AS Departamento,
                COALESCE(p.nombre_puesto, 'SIN PUESTO') AS Puesto,
                COALESCE(ce.correo_gmail, '') AS `Correo Gmail`,
                COALESCE(ce.correo_corporativo, '') AS `Correo Institucional`,
                COALESCE(lt.numero, ic.numero, '') AS Celular
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
            LEFT JOIN (
                SELECT 
                    TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) AS cod_clean,
                    MAX(numero) AS numero
                FROM lineas_telefonicas
                WHERE codigo_empleado IS NOT NULL AND TRIM(numero) != ''
                GROUP BY cod_clean
            ) lt ON TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR)) = lt.cod_clean
            LEFT JOIN (
                SELECT 
                    TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) AS cod_clean, 
                    MAX(numero) AS numero
                FROM inventario_celulares
                WHERE codigo_empleado IS NOT NULL AND numero IS NOT NULL AND TRIM(numero) != ''
                GROUP BY cod_clean
            ) ic ON TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR)) = ic.cod_clean
            WHERE e.id_estatus_empleado = 1
            ORDER BY Nombre ASC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error al generar lista de distribución: {e}")
        return pd.DataFrame()

def convertir_df_a_excel(df, sheet_name="Reporte"):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)
    return output.getvalue()

# ==============================================================================
# RENDER PRINCIPAL DEL MÓDULO
# ==============================================================================
def render():
    aplicar_estilo_sb_admin()
    st.title("📊 Módulo de Reportería y Métricas")

    # --------------------------------------------------------------------------
    # DASHBOARD Y MÉTRICAS EN PANTALLA INICIAL
    # --------------------------------------------------------------------------
    total_eq, asig, disp, mant, df_kpi = obtener_kpis_inventario()

    col_kpis, col_grafica = st.columns([2.5, 1.5])

    with col_kpis:
        st.write(" ")
        k1, k2 = st.columns(2)
        k1.metric("📦 Total Hardware", total_eq)
        k2.metric("✅ Asignados", asig)

        st.write(" ")
        k3, k4 = st.columns(2)
        k3.metric("🟢 Stock Disponible", disp)
        k4.metric("🛠️ En Taller / Mant.", mant)

    with col_grafica:
        fig_dona = generar_grafica_dona(df_kpi)
        if fig_dona:
            st.plotly_chart(fig_dona, use_container_width=True, config={'displayModeBar': False})

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Dispositivos por Colaborador",
        "📞 Reporte de Líneas",
        "📦 Hardware Disponible",
        "📧 Lista de Distribución (Drive)"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: DISPOSITIVOS POR COLABORADOR
    # --------------------------------------------------------------------------
    with tab1:
        st.subheader("👤 Consulta de Hardware Asignado por Colaborador")
        try:
            conn = obtener_conexion()
            df_emp = pd.read_sql("""
                SELECT codigo, CONCAT_WS(' ', nombre, apellido_paterno, apellido_materno) AS nom_comp, s.nombre_sucursal AS sucursal
                FROM empleados e
                LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
                WHERE e.id_estatus_empleado = 1 
                ORDER BY nom_comp ASC
            """, conn)
            conn.close()

            if not df_emp.empty:
                dict_emp = {f"{r['nom_comp']} ({r['sucursal']})": r['codigo'] for _, r in df_emp.iterrows()}
                emp_sel_nom = st.selectbox("Selecciona un Colaborador:", list(dict_emp.keys()))
                cod_sel = dict_emp[emp_sel_nom]

                df_eq_emp = obtener_equipos_por_colaborador(cod_sel)

                if not df_eq_emp.empty:
                    st.success(f"Dispositivos asignados a **{emp_sel_nom}**:")
                    st.dataframe(df_eq_emp, use_container_width=True, hide_index=True)
                else:
                    st.info(f"El colaborador **{emp_sel_nom}** no tiene ningún equipo asignado actualmente.")
        except Exception as e:
            st.error(f"Error al cargar la lista de colaboradores: {e}")

    # --------------------------------------------------------------------------
    # TAB 2: REPORTE DE LÍNEAS
    # --------------------------------------------------------------------------
    with tab2:
        st.subheader("📞 Reporte General de Líneas Telefónicas")
        df_lineas = obtener_reporte_lineas_df()

        if not df_lineas.empty:
            st.dataframe(df_lineas, use_container_width=True, hide_index=True)
            
            col_l1, col_l2 = st.columns([1, 2])
            with col_l1:
                excel_lineas_bytes = convertir_df_a_excel(df_lineas, sheet_name="Lineas_Telefonicas")
                st.download_button(
                    label="📥 Descargar Reporte de Líneas (.xlsx)",
                    data=excel_lineas_bytes,
                    file_name="Reporte_Lineas_AGROCISA.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary"
                )
            with col_l2:
                st.caption(f"Total de líneas registradas en sistema: **{len(df_lineas)}**")
        else:
            st.info("No se encontraron líneas telefónicas registradas.")

    # --------------------------------------------------------------------------
    # TAB 3: HARDWARE DISPONIBLE (STOCK)
    # --------------------------------------------------------------------------
    with tab3:
        st.subheader("📦 Stock de Equipos Disponibles para Asignación")
        df_disp = obtener_dispositivos_disponibles_df()

        if not df_disp.empty:
            cats = ["Todas"] + sorted(list(df_disp["Categoria"].unique()))
            cat_sel = st.selectbox("Filtrar por Categoría:", cats)

            df_filtrado = df_disp if cat_sel == "Todas" else df_disp[df_disp["Categoria"] == cat_sel]
            st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
            st.caption(f"Total de equipos en stock listo para entregar: **{len(df_filtrado)}**")
        else:
            st.info("No hay equipos disponibles en stock por el momento.")

    # --------------------------------------------------------------------------
    # TAB 4: LISTA DE DISTRIBUCIÓN (GOOGLE DRIVE / EXCEL)
    # --------------------------------------------------------------------------
    with tab4:
        st.subheader("📧 Lista de Distribución General (Mapeo Google Drive)")
        st.caption("Estructura en vivo vinculada con el archivo 'Listas de distribución' de Google Sheets.")

        df_dist = obtener_lista_distribucion_df()

        if not df_dist.empty:
            col_btn1, col_btn2, col_btn3 = st.columns([1.5, 1.5, 2])
            
            with col_btn1:
                if st.button("🚀 Sincronizar a Google Drive Ahora", type="primary"):
                    with st.spinner("⏳ Enviando registros a Google Sheets..."):
                        exito, msj_err = sync_drive.auto_sincronizar_google_sheet()
                        if exito:
                            st.session_state["ultima_sync_drive"] = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
                            st.toast("¡Google Sheets actualizado con éxito!", icon="🎉")
                            st.rerun()
                        else:
                            st.error(f"⚠️ Falló la conexión: {msj_err}")

            with col_btn2:
                excel_bytes = convertir_df_a_excel(df_dist, sheet_name="Colaboradores")
                st.download_button(
                    label="📥 Descargar copia local (.xlsx)",
                    data=excel_bytes,
                    file_name="Listas_de_distribucion_AGROCISA.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

            with col_btn3:
                if "ultima_sync_drive" in st.session_state:
                    st.success(f"🟢 **Última sincronización exitosa:**\n\n`{st.session_state['ultima_sync_drive']}`")
                else:
                    st.info("⚪ Sin sincronizaciones ejecutadas en esta sesión.")

            st.divider()
            st.dataframe(df_dist, use_container_width=True, hide_index=True)