import streamlit as st
import pandas as pd
import unicodedata
from database import obtener_conexion
# Importamos la función de cascada desde correos_electronicos
from correos_electronicos import actualizar_empleado_en_cascada_bdd

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

def normalizar_texto(texto):
    """Limpia acentos, mayúsculas y espacios dobles para comparaciones exactas."""
    if not texto or pd.isna(texto):
        return ""
    txt = str(texto).strip().lower()
    txt = ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')
    return " ".join(txt.split())

def obtener_datos_vps():
    """Consulta la base de datos central en el VPS (GoDaddy)."""
    try:
        from database import obtener_conexion_vps
        conn = obtener_conexion_vps()
    except Exception:
        # Fallback si se usa la misma base o función parametrizada
        conn = obtener_conexion()

    if not conn:
        st.error("⚠️ No se pudo conectar al VPS central.")
        return pd.DataFrame()

    try:
        query = """
            SELECT 
                codigo,
                nombre,
                apellido_paterno,
                apellido_materno,
                CONCAT_WS(' ', nombre, apellido_paterno, apellido_materno) AS nombre_completo,
                id_sucursal,
                id_departamento,
                id_puesto,
                id_estatus_empleado
            FROM empleados
            WHERE id_estatus_empleado = 1
        """
        df = pd.read_sql(query, conn)
        conn.close()
        df["codigo_clean"] = df["codigo"].astype(str).str.strip().str.zfill(5)
        df["nombre_norm"] = df["nombre_completo"].apply(normalizar_texto)
        return df
    except Exception as e:
        st.error(f"⚠️ Error al consultar empleados en VPS: {e}")
        return pd.DataFrame()

def obtener_datos_local():
    """Consulta la base de datos local."""
    conn = obtener_conexion()
    if not conn:
        return pd.DataFrame()

    try:
        query = """
            SELECT 
                e.codigo,
                e.nombre,
                e.apellido_paterno,
                e.apellido_materno,
                CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS nombre_completo,
                e.id_sucursal,
                s.nombre_sucursal AS sucursal,
                e.id_departamento,
                d.nombre_departamento AS departamento,
                e.id_puesto,
                p.nombre_puesto AS puesto,
                e.id_estatus_empleado
            FROM empleados e
            LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
            LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento
            LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
            WHERE e.id_estatus_empleado = 1
        """
        df = pd.read_sql(query, conn)
        conn.close()
        df["codigo_clean"] = df["codigo"].astype(str).str.strip().str.zfill(5)
        df["nombre_norm"] = df["nombre_completo"].apply(normalizar_texto)
        return df
    except Exception as e:
        st.error(f"⚠️ Error al consultar empleados locales: {e}")
        return pd.DataFrame()

def obtener_equipos_empleado(codigo_empleado):
    """Obtiene los equipos asignados al colaborador para la vista de bajas."""
    conn = obtener_conexion()
    equipos = []
    if not conn:
        return equipos

    cod_clean = str(codigo_empleado).strip()
    try:
        # Celulares
        df_cel = pd.read_sql("""
            SELECT ic.imei AS id, CONCAT('📱 Celular: ', ic.imei, ' - ', COALESCE(m.marca_modelo, 'S/M')) AS descr, 'celular' AS tipo
            FROM inventario_celulares ic
            LEFT JOIN modelos_celulares m ON ic.id_modelo = m.id_modelo
            WHERE TRIM(LEADING '0' FROM CAST(ic.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(%s AS CHAR))
              AND ic.id_estatus_celular = 3
        """, conn, params=(cod_clean,))
        equipos.extend(df_cel.to_dict('records'))

        # Laptops
        df_lap = pd.read_sql("""
            SELECT il.numero_serie AS id, CONCAT('💻 Laptop: ', il.numero_serie, ' - ', il.marca, ' ', il.modelo) AS descr, 'laptop' AS tipo
            FROM inventario_laptops il
            WHERE TRIM(LEADING '0' FROM CAST(il.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(%s AS CHAR))
              AND il.id_estatus_laptops = 3
        """, conn, params=(cod_clean,))
        equipos.extend(df_lap.to_dict('records'))

        # CPUs
        df_cpu = pd.read_sql("""
            SELECT icp.hostname AS id, CONCAT('🖥️ CPU: ', icp.hostname, ' - ', icp.numero_serie) AS descr, 'cpu' AS tipo
            FROM inventario_cpu icp
            WHERE TRIM(LEADING '0' FROM CAST(icp.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(%s AS CHAR))
              AND icp.id_estatus_cpu = 3
        """, conn, params=(cod_clean,))
        equipos.extend(df_cpu.to_dict('records'))

        # Monitores
        df_mon = pd.read_sql("""
            SELECT im.numero_serie AS id, CONCAT('🖥️ Monitor: ', im.numero_serie, ' - ', im.marca) AS descr, 'monitor' AS tipo
            FROM inventario_monitores im
            WHERE TRIM(LEADING '0' FROM CAST(im.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(%s AS CHAR))
              AND im.id_estatus_monitor = 3
        """, conn, params=(cod_clean,))
        equipos.extend(df_mon.to_dict('records'))

        # Tablets
        df_tab = pd.read_sql("""
            SELECT it.numero_serie AS id, CONCAT('📱 Tablet: ', it.numero_serie, ' - ', it.marca) AS descr, 'tablet' AS tipo
            FROM inventario_tablets it
            WHERE TRIM(LEADING '0' FROM CAST(it.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(%s AS CHAR))
              AND it.id_estatus_tablet = 3
        """, conn, params=(cod_clean,))
        equipos.extend(df_tab.to_dict('records'))

    except Exception:
        pass
    finally:
        conn.close()

    return equipos

# ==============================================================================
# RENDER PRINCIPAL DEL SINCRONIZADOR
# ==============================================================================
def render():
    aplicar_estilos_pantalla()
    st.title("🔄 Sincronización Automática con VPS")
    st.markdown("### ⚙️ Panel de Control de Sincronización")
    st.caption("Cruza de información entre MariaDB VPS (GoDaddy) y BDD Local con conciliación automática de códigos provisionales.")

    if st.button("🚀 Ejecutar Sincronización y Diagnóstico", type="primary"):
        st.session_state["ejecutar_sync"] = True

    if st.session_state.get("ejecutar_sync", False):
        df_vps = obtener_datos_vps()
        df_loc = obtener_datos_local()

        if df_vps.empty or df_loc.empty:
            st.warning("⚠️ No se pudieron obtener los datos completos para sincronizar.")
            return

        set_vps_codigos = set(df_vps["codigo_clean"].tolist())
        set_loc_codigos = set(df_loc["codigo_clean"].tolist())

        # 1. Candidatos directos por código
        loc_sin_vps = df_loc[~df_loc["codigo_clean"].isin(set_vps_codigos)].copy()
        vps_sin_loc = df_vps[~df_vps["codigo_clean"].isin(set_loc_codigos)].copy()

        # 2. Reconciliación por Nombre (Detección de Códigos Provisionales)
        homologaciones = []
        indices_loc_homologados = []
        indices_vps_homologados = []

        for idx_l, row_l in loc_sin_vps.iterrows():
            match_vps = vps_sin_loc[vps_sin_loc["nombre_norm"] == row_l["nombre_norm"]]
            if not match_vps.empty:
                row_v = match_vps.iloc[0]
                homologaciones.append({
                    "colaborador": row_l["nombre_completo"],
                    "codigo_local": row_l["codigo_clean"],
                    "codigo_vps": row_v["codigo_clean"],
                    "sucursal": row_l["sucursal"],
                    "departamento": row_l["departamento"],
                    "puesto": row_l["puesto"],
                    "row_vps": row_v.to_dict(),
                    "row_local": row_l.to_dict()
                })
                indices_loc_homologados.append(idx_l)
                indices_vps_homologados.append(match_vps.index[0])

        # 3. Bajas y Altas Reales (Excluyendo los homologados por nombre)
        bajas_reales = loc_sin_vps.drop(index=indices_loc_homologados)
        altas_reales = vps_sin_loc.drop(index=indices_vps_homologados)

        # Métricas principales
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🚨 Bajas Reales (Internos)", f"{len(bajas_reales)} empleados")
        m2.metric("🔄 Códigos Provisionales", f"{len(homologaciones)} detectados")
        m3.metric("✨ Altas Detectadas", f"{len(altas_reales)} empleados")
        m4.metric("✅ Total Activos VPS", f"{len(df_vps)} empleados")

        st.divider()

        tab_homologar, tab_bajas, tab_altas = st.tabs([
            f"🔄 Códigos Provisionales a Homologar ({len(homologaciones)})",
            f"🚨 Bajas a Procesar ({len(bajas_reales)})",
            f"✨ Nuevas Altas ({len(altas_reales)})"
        ])

        # ----------------------------------------------------------------------
        # TAB 1: CÓDIGOS PROVISIONALES (CASO RODRIGO Y SIMILARES)
        # ----------------------------------------------------------------------
        with tab_homologar:
            if homologaciones:
                st.info("💡 **Se detectaron colaboradores dados de alta localmente con código provisional que ya cuentan con su código oficial de RH en el VPS.**")
                st.caption("Al homologar, el código se actualiza en cascada en todos sus equipos, líneas telefónicas, responsivas y correos sin borrarlos.")

                for item in homologaciones:
                    with st.container():
                        c_info, c_btn = st.columns([3, 1])
                        with c_info:
                            st.markdown(f"👤 **{item['colaborador']}** ({item['sucursal']} - {item['puesto']})")
                            st.markdown(f"Código Local Provisional: `:red[{item['codigo_local']}]` ➔ Código Oficial VPS: `:green[{item['codigo_vps']}]`")
                        with c_btn:
                            st.write("")
                            if st.button(f"⚡ Homologar a {item['codigo_vps']}", key=f"btn_hom_{item['codigo_local']}"):
                                r_l = item['row_local']
                                r_v = item['row_vps']
                                exito = actualizar_empleado_en_cascada_bdd(
                                    codigo_viejo=item['codigo_local'],
                                    codigo_nuevo=item['codigo_vps'],
                                    nombre=r_v['nombre'],
                                    ap_pat=r_v['apellido_paterno'],
                                    ap_mat=r_v['apellido_materno'],
                                    id_suc=int(r_v['id_sucursal']),
                                    id_dep=int(r_v['id_departamento']),
                                    id_pue=int(r_v['id_puesto']),
                                    id_estatus=1
                                )
                                if exito:
                                    st.toast(f"¡Código homologado a {item['codigo_vps']} para {item['colaborador']}!", icon="🎉")
                                    st.rerun()
                        st.divider()
            else:
                st.success("✅ No hay discrepancias de códigos provisionales pendientes de homologar.")

        # ----------------------------------------------------------------------
        # TAB 2: BAJAS A PROCESAR
        # ----------------------------------------------------------------------
        with tab_bajas:
            if not bajas_reales.empty:
                st.error("Los siguientes empleados internos ya no están activos en el VPS central. Procesa sus equipos:")
                
                lista_bajas = [f"{r['codigo_clean']} - {r['nombre_completo']} ({r['sucursal']})" for _, r in bajas_reales.iterrows()]
                emp_baja_sel = st.selectbox("Selecciona colaborador para procesar salida:", lista_bajas, key="sel_baja_proc")

                if emp_baja_sel:
                    cod_baja = emp_baja_sel.split(" - ")[0]
                    row_baja = bajas_reales[bajas_reales["codigo_clean"] == cod_baja].iloc[0]
                    equipos_asignados = obtener_equipos_empleado(cod_baja)

                    st.markdown(f"#### 📦 Equipos Asignados a `{cod_baja}` ({row_baja['sucursal']})")
                    if equipos_asignados:
                        for eq in equipos_asignados:
                            st.write(f"- {eq['descr']}")
                    else:
                        st.info("Este colaborador no tiene equipos asignados actualmente.")
            else:
                st.success("✅ No hay bajas de personal pendientes.")

        # ----------------------------------------------------------------------
        # TAB 3: NUEVAS ALTAS
        # ----------------------------------------------------------------------
        with tab_altas:
            if not altas_reales.empty:
                st.info("Empleados registrados en VPS central que aún no existen en la base de datos local:")
                st.dataframe(
                    altas_reales[["codigo_clean", "nombre_completo"]].rename(columns={"codigo_clean": "Código", "nombre_completo": "Nombre Completo"}),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("✅ La base de datos local está al día con las altas del VPS.")

render_sincronizador = render