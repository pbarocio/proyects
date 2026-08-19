import streamlit as st
import pandas as pd
import unicodedata
import database
from correos_electronicos import actualizar_empleado_en_cascada_bdd
from responsivas import procesar_desvinculacion_equipo

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
    if not texto or pd.isna(texto):
        return ""
    txt = str(texto).strip().lower()
    txt = ''.join(c for c in unicodedata.normalize('NFD', txt) if unicodedata.category(c) != 'Mn')
    return " ".join(txt.split())

def limpiar_codigo(cod):
    if cod is None or pd.isna(cod):
        return ""
    txt = str(cod).strip()
    try:
        return str(int(float(txt)))
    except Exception:
        return txt.lstrip("0").strip()

def obtener_catalogo_dict(tabla, col_id, col_nombre):
    try:
        conn = database.obtener_conexion()
        if not conn:
            return {}
        query = f"SELECT {col_id}, {col_nombre} FROM {tabla} ORDER BY {col_id} ASC"
        df = pd.read_sql(query, conn)
        conn.close()
        return {str(nom): int(cid) for nom, cid in zip(df[col_nombre], df[col_id])}
    except Exception:
        return {}

# ==============================================================================
# OBTENCIÓN DE DATOS USANDO EL TÚNEL SSH DE DATABASE.PY
# ==============================================================================
def obtener_datos_vps():
    """Jala el DataFrame de empleados activos usando el túnel SSH central."""
    try:
        df_vps = database.obtener_empleados_vps_df()
        if df_vps is None or df_vps.empty:
            return pd.DataFrame(), "No se recibieron registros desde el VPS central."
        
        df_vps["codigo_norm"] = df_vps["codigo"].apply(limpiar_codigo)
        df_vps["codigo_disp"] = df_vps["codigo"].astype(str).str.strip().str.zfill(5)
        
        if "nombre_completo" not in df_vps.columns:
            df_vps["nombre_completo"] = df_vps.apply(
                lambda r: " ".join(filter(None, [str(r.get('nombre', '')), str(r.get('apellido_paterno', '')), str(r.get('apellido_materno', ''))])).strip(),
                axis=1
            )
        df_vps["nombre_norm"] = df_vps["nombre_completo"].apply(normalizar_texto)
        return df_vps, None
    except Exception as e:
        return pd.DataFrame(), f"Error al ejecutar obtener_empleados_vps_df(): {e}"

def obtener_datos_local():
    """Consulta empleados locales directamente desde agrocisa_core."""
    try:
        conn = database.obtener_conexion()
        query = """
            SELECT 
                e.codigo,
                e.nombre,
                e.apellido_paterno,
                e.apellido_materno,
                CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS nombre_completo,
                e.id_sucursal,
                COALESCE(s.nombre_sucursal, 'SIN SUCURSAL') AS sucursal,
                e.id_departamento,
                COALESCE(d.nombre_departamento, 'SIN DEPARTAMENTO') AS departamento,
                e.id_puesto,
                COALESCE(p.nombre_puesto, 'SIN PUESTO') AS puesto,
                e.id_tipo_contrato,
                COALESCE(tce.tipo_contrato, 'INTERNO') AS tipo_contrato,
                e.id_estatus_empleado
            FROM empleados e
            LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
            LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento
            LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
            LEFT JOIN tipo_contrato_empleados tce ON e.id_tipo_contrato = tce.id_tipo_contrato
            WHERE e.id_estatus_empleado = 1
        """
        df_loc = pd.read_sql(query, conn)
        conn.close()
        df_loc["codigo_norm"] = df_loc["codigo"].apply(limpiar_codigo)
        df_loc["codigo_disp"] = df_loc["codigo"].astype(str).str.strip().str.zfill(5)
        df_loc["nombre_norm"] = df_loc["nombre_completo"].apply(normalizar_texto)
        return df_loc, None
    except Exception as e:
        return pd.DataFrame(), f"Error al consultar base local: {e}"

def ejecutar_diagnostico_completo():
    df_vps, err_vps = obtener_datos_vps()
    if err_vps:
        return None, err_vps

    df_loc, err_loc = obtener_datos_local()
    if err_loc:
        return None, err_loc

    codigos_vps_norm = set(df_vps["codigo_norm"].tolist())
    codigos_loc_norm = set(df_loc["codigo_norm"].tolist())

    loc_sin_vps_id = df_loc[~df_loc["codigo_norm"].isin(codigos_vps_norm)].copy()
    vps_sin_loc_id = df_vps[~df_vps["codigo_norm"].isin(codigos_loc_norm)].copy()

    # Conciliación por Nombre y Apellidos
    homologaciones = []
    idx_loc_homologados = []
    idx_vps_homologados = []

    for idx_l, row_l in loc_sin_vps_id.iterrows():
        match_vps = vps_sin_loc_id[vps_sin_loc_id["nombre_norm"] == row_l["nombre_norm"]]
        if not match_vps.empty:
            row_v = match_vps.iloc[0]
            homologaciones.append({
                "colaborador": row_l["nombre_completo"],
                "codigo_local": row_l["codigo_disp"],
                "codigo_vps": row_v["codigo_disp"],
                "sucursal": row_l.get("sucursal", "S/D"),
                "puesto": row_l.get("puesto", "S/D"),
                "id_sucursal": row_l.get("id_sucursal", 1),
                "id_departamento": row_l.get("id_departamento", 1),
                "id_puesto": row_l.get("id_puesto", 1),
                "id_tipo_contrato": row_l.get("id_tipo_contrato", 1),
                "row_vps": row_v.to_dict(),
                "row_local": row_l.to_dict()
            })
            idx_loc_homologados.append(idx_l)
            idx_vps_homologados.append(match_vps.index[0])

    loc_reales_discrepantes = loc_sin_vps_id.drop(index=idx_loc_homologados)
    altas_reales = vps_sin_loc_id.drop(index=idx_vps_homologados)

    es_externo = loc_reales_discrepantes["puesto"].astype(str).str.lower().str.contains("externo|asesor|proveedor|contratista") | \
                 loc_reales_discrepantes["sucursal"].astype(str).str.lower().str.contains("externo|corporativo externo") | \
                 (loc_reales_discrepantes["id_tipo_contrato"] == 2)

    externos_protegidos = loc_reales_discrepantes[es_externo]
    bajas_reales = loc_reales_discrepantes[~es_externo]

    return {
        "total_vps": len(df_vps),
        "total_local": len(df_loc),
        "homologaciones": homologaciones,
        "bajas_reales": bajas_reales,
        "externos_protegidos": externos_protegidos,
        "altas_detectadas": altas_reales
    }, None

def obtener_equipos_empleado(codigo_empleado):
    conn = database.obtener_conexion()
    equipos = []
    if not conn:
        return equipos

    cod_clean = str(codigo_empleado).strip().lstrip("0")
    try:
        # Celulares
        df_cel = pd.read_sql("""
            SELECT ic.imei, ic.numero, m.marca_modelo
            FROM inventario_celulares ic
            LEFT JOIN modelos_celulares m ON ic.id_modelo = m.id_modelo
            WHERE TRIM(LEADING '0' FROM CAST(ic.codigo_empleado AS CHAR)) = %s
              AND ic.id_estatus_celular = 3
        """, conn, params=(cod_clean,))
        for _, r in df_cel.iterrows():
            equipos.append({"tipo": "celular", "id": r['imei'], "descr": f"📱 Celular: {r['imei']} - {r['marca_modelo'] or 'S/M'} (Línea: {r['numero'] or 'S/N'})"})

        # Laptops
        df_lap = pd.read_sql("""
            SELECT il.numero_serie, il.marca, il.modelo, il.hostname
            FROM inventario_laptops il
            WHERE TRIM(LEADING '0' FROM CAST(il.codigo_empleado AS CHAR)) = %s
              AND il.id_estatus_laptops = 3
        """, conn, params=(cod_clean,))
        for _, r in df_lap.iterrows():
            equipos.append({"tipo": "laptop", "id": r['numero_serie'], "descr": f"💻 Laptop: {r['numero_serie']} - {r['marca']} {r['modelo']} [{r['hostname']}]"})

        # CPUs
        df_cpu = pd.read_sql("""
            SELECT icp.id_cpu, icp.hostname, icp.numero_serie, icp.marca, icp.modelo
            FROM inventario_cpu icp
            WHERE TRIM(LEADING '0' FROM CAST(icp.codigo_empleado AS CHAR)) = %s
              AND icp.id_estatus_cpu = 3
        """, conn, params=(cod_clean,))
        for _, r in df_cpu.iterrows():
            equipos.append({"tipo": "cpu", "id": str(r['id_cpu']), "descr": f"🖥️ CPU: ID {r['id_cpu']} - {r['hostname']} ({r['marca']} {r['modelo']})"})

        # Monitores
        df_mon = pd.read_sql("""
            SELECT im.numero_serie, im.marca, im.modelo
            FROM inventario_monitores im
            WHERE TRIM(LEADING '0' FROM CAST(im.codigo_empleado AS CHAR)) = %s
              AND im.id_estatus_monitor = 3
        """, conn, params=(cod_clean,))
        for _, r in df_mon.iterrows():
            equipos.append({"tipo": "monitor", "id": r['numero_serie'], "descr": f"🖥️ Monitor: {r['numero_serie']} - {r['marca']} {r['modelo']}"})

        # Tablets
        df_tab = pd.read_sql("""
            SELECT it.numero_serie, it.marca, it.modelo
            FROM inventario_tablets it
            WHERE TRIM(LEADING '0' FROM CAST(it.codigo_empleado AS CHAR)) = %s
              AND it.id_estatus_tablet = 3
        """, conn, params=(cod_clean,))
        for _, r in df_tab.iterrows():
            equipos.append({"tipo": "tablet", "id": r['numero_serie'], "descr": f"📱 Tablet: {r['numero_serie']} - {r['marca']} {r['modelo']}"})

    except Exception:
        pass
    finally:
        conn.close()

    return equipos

def guardar_alta_individual(codigo, nombre, ap_pat, ap_mat, id_suc, id_dep, id_pue, id_contrato, id_estatus=1):
    conn = database.obtener_conexion()
    if not conn:
        return False, "No hay conexión con la base local."
    
    cursor = conn.cursor()
    try:
        q = """
            INSERT INTO empleados (codigo, nombre, apellido_paterno, apellido_materno, id_sucursal, id_departamento, id_puesto, id_tipo_contrato, id_estatus_empleado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                nombre = VALUES(nombre), apellido_paterno = VALUES(apellido_paterno), apellido_materno = VALUES(apellido_materno),
                id_sucursal = VALUES(id_sucursal), id_departamento = VALUES(id_departamento), id_puesto = VALUES(id_puesto),
                id_tipo_contrato = VALUES(id_tipo_contrato), id_estatus_empleado = VALUES(id_estatus_empleado)
        """
        cursor.execute(q, (
            str(codigo).strip().zfill(5), str(nombre).strip(), str(ap_pat).strip(),
            str(ap_mat).strip() if ap_mat else None, int(id_suc), int(id_dep), int(id_pue), int(id_contrato), int(id_estatus)
        ))

        conn.commit()
        return True, None
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()

# ==============================================================================
# RENDER PRINCIPAL
# ==============================================================================
def render():
    aplicar_estilos_pantalla()

    if "mensaje_exito_sync" in st.session_state:
        st.success(st.session_state["mensaje_exito_sync"])
        del st.session_state["mensaje_exito_sync"]

    dict_suc = obtener_catalogo_dict("sucursales", "id_sucursal", "nombre_sucursal")
    dict_dep = obtener_catalogo_dict("departamentos", "id_departamento", "nombre_departamento")
    dict_pue = obtener_catalogo_dict("puestos", "id_puesto", "nombre_puesto")
    dict_contrato = obtener_catalogo_dict("tipo_contrato_empleados", "id_tipo_contrato", "tipo_contrato")

    st.markdown("### ⚙️ Panel de Control de Sincronización")
    st.caption("Cruza de información entre MariaDB VPS (GoDaddy vía Túnel SSH) y BDD Local con conciliación automática por nombre.")

    if st.button("🚀 Ejecutar Sincronización y Diagnóstico", type="primary"):
        with st.spinner("Abriendo túnel SSH con VPS y procesando registros..."):
            diag, err = ejecutar_diagnostico_completo()
            if err:
                st.error(f"⛔ {err}")
            else:
                st.session_state["diag_data"] = diag

    if "diag_data" in st.session_state and st.session_state["diag_data"]:
        data = st.session_state["diag_data"]
        homologaciones = data.get("homologaciones", [])
        bajas_reales = data["bajas_reales"]
        externos_protegidos = data["externos_protegidos"]
        altas_detectadas = data["altas_detectadas"]

        st.divider()
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔄 A Homologar (Nombre)", f"{len(homologaciones)} detectados")
        c2.metric("🚨 Bajas Reales", f"{len(bajas_reales)} empleados")
        c3.metric("🛡️ Externos Protegidos", f"{len(externos_protegidos)} empleados")
        c4.metric("✨ Altas Detectadas", f"{len(altas_detectadas)} empleados")

        st.divider()

        tab_homologar, tab_bajas, tab_ext, tab_altas = st.tabs([
            f"🔄 Conciliar Códigos ({len(homologaciones)})",
            f"🚨 Bajas a Procesar ({len(bajas_reales)})",
            f"🛡️ Externos Omitidos ({len(externos_protegidos)})",
            f"✨ Nuevas Altas ({len(altas_detectadas)})"
        ])

        # ----------------------------------------------------------------------
        # TAB 1: CONCILIAR CÓDIGOS PROVISIONALES
        # ----------------------------------------------------------------------
        with tab_homologar:
            if homologaciones:
                st.info("💡 **Se detectaron colaboradores dados de alta localmente cuyos nombres coinciden con un registro oficial del VPS pero con código distinto.**")
                st.caption("Al presionar 'Homologar', su código se actualiza en cascada en inventarios, responsivas, líneas y correos.")

                for item in homologaciones:
                    with st.container():
                        c_info, c_btn = st.columns([3, 1])
                        with c_info:
                            st.markdown(f"👤 **{item['colaborador']}** ({item['sucursal']} - {item['puesto']})")
                            st.markdown(f"Código Local: `{item['codigo_local']}` ➔ Oficial VPS: `{item['codigo_vps']}`")
                        with c_btn:
                            st.write("")
                            if st.button(f"⚡ Homologar a {item['codigo_vps']}", key=f"btn_hom_{item['codigo_local']}"):
                                r_v = item['row_vps']
                                exito = actualizar_empleado_en_cascada_bdd(
                                    codigo_viejo=item['codigo_local'],
                                    codigo_nuevo=item['codigo_vps'],
                                    nombre=r_v.get('nombre', ''),
                                    ap_pat=r_v.get('apellido_paterno', ''),
                                    ap_mat=r_v.get('apellido_materno', ''),
                                    id_suc=int(item['id_sucursal']),
                                    id_dep=int(item['id_departamento']),
                                    id_pue=int(item['id_puesto']),
                                    id_contrato=int(item['id_tipo_contrato']),
                                    id_estatus=1
                                )
                                if exito:
                                    st.session_state["mensaje_exito_sync"] = f"🎉 ¡Código de {item['colaborador']} homologado exitosamente de `{item['codigo_local']}` a `{item['codigo_vps']}` en cascada!"
                                    del st.session_state["diag_data"]
                                    st.rerun()
                        st.divider()
            else:
                st.success("✅ No hay colaboradores con códigos provisionales pendientes de conciliar.")

        # ----------------------------------------------------------------------
        # TAB 2: BAJAS A PROCESAR
        # ----------------------------------------------------------------------
        with tab_bajas:
            if not bajas_reales.empty:
                st.error("Los siguientes empleados internos ya no están activos en VPS central. Procesa sus equipos:")

                lista_bajas = [f"{r['codigo_disp']} - {r['nombre_completo']} ({r['sucursal']})" for _, r in bajas_reales.iterrows()]
                emp_sel = st.selectbox("Selecciona colaborador para procesar salida:", lista_bajas, key="sel_baja_salida")

                if emp_sel:
                    cod_sel = emp_sel.split(" - ")[0]
                    row_emp = bajas_reales[bajas_reales["codigo_disp"] == cod_sel].iloc[0]
                    equipos = obtener_equipos_empleado(cod_sel)

                    st.markdown(f"#### 📦 Equipos Asignados a `{row_emp['nombre_completo']}` ({row_emp['sucursal']})")

                    if equipos:
                        for eq in equipos:
                            with st.expander(f"⚙️ {eq['descr']}", expanded=True):
                                c_e1, c_e2, c_e3 = st.columns([1.5, 2, 1])
                                with c_e1:
                                    st_dest = st.selectbox(
                                        f"Estatus destino ({eq['tipo']}):",
                                        ["DISPONIBLE", "EN MANTENIMIENTO", "EN REPARACIÓN", "INACTIVO"],
                                        key=f"st_eq_{eq['id']}"
                                    )
                                with c_e2:
                                    obs_dest = st.text_input(
                                        "Observaciones / Destino:",
                                        value="Baja de colaborador vía sincronizador",
                                        key=f"obs_eq_{eq['id']}"
                                    )
                                with c_e3:
                                    st.write("")
                                    dict_est_lib = {"DISPONIBLE": 4, "EN MANTENIMIENTO": 5, "EN REPARACIÓN": 6, "INACTIVO": 2}
                                    if st.button(f"💥 Liberar {eq['tipo']}", key=f"btn_lib_{eq['id']}"):
                                        if procesar_desvinculacion_equipo(
                                            tipo_equipo=eq['tipo'],
                                            id_equipo=eq['id'],
                                            nuevo_estatus_id=dict_est_lib[st_dest],
                                            razon_motivo=obs_dest,
                                            nombre_colaborador=f"{row_emp['nombre_completo']} (Cód: {cod_sel})"
                                        ):
                                            st.session_state["mensaje_exito_sync"] = f"🎉 ¡Equipo {eq['tipo']} ({eq['id']}) liberado correctamente con estatus: {st_dest}!"
                                            del st.session_state["diag_data"]
                                            st.rerun()
                    else:
                        st.info("Este colaborador no tiene equipos asignados en el inventario.")
            else:
                st.success("✅ No hay bajas de empleados pendientes por procesar.")

        # ----------------------------------------------------------------------
        # TAB 3: EXTERNOS OMITIDOS
        # ----------------------------------------------------------------------
        with tab_ext:
            if not externos_protegidos.empty:
                st.info("Los siguientes empleados no están en el VPS central pero se mantienen locales por ser externos/contratistas:")
                st.dataframe(
                    externos_protegidos[["codigo_disp", "nombre_completo", "sucursal", "puesto"]].rename(columns={
                        "codigo_disp": "Código",
                        "nombre_completo": "Colaborador",
                        "sucursal": "Sucursal",
                        "puesto": "Puesto"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.caption("No hay empleados externos identificados en la lista local.")

        # ----------------------------------------------------------------------
        # TAB 4: NUEVAS ALTAS (PROCESAMIENTO INDIVIDUAL CONTROLADO)
        # ----------------------------------------------------------------------
        with tab_altas:
            if not altas_detectadas.empty:
                st.info(f"Se detectaron **{len(altas_detectadas)}** empleados en el VPS que aún no están en la base de datos local.")
                st.caption("Selecciona al colaborador para asignarle correctamente sus catálogos locales antes de darlo de alta:")

                lista_altas_opts = [f"{r['codigo_disp']} - {r['nombre_completo']}" for _, r in altas_detectadas.iterrows()]
                alta_sel_str = st.selectbox(
                    "Selecciona el colaborador a registrar:",
                    lista_altas_opts,
                    index=None,
                    placeholder="🔍 Selecciona o teclea el empleado a dar de alta...",
                    key="sel_alta_indiv"
                )

                if alta_sel_str:
                    cod_alta_sel = alta_sel_str.split(" - ")[0]
                    row_alta = altas_detectadas[altas_detectadas["codigo_disp"] == cod_alta_sel].iloc[0]

                    st.divider()
                    with st.form(f"form_alta_vps_{cod_alta_sel}"):
                        st.markdown(f"#### 📝 Registro de Alta Local: `{row_alta['nombre_completo']}` (Código: `{cod_alta_sel}`)")

                        c1, c2 = st.columns(2)
                        with c1:
                            nom_alta = st.text_input("Nombre(s)*:", value=str(row_alta.get("nombre", "")))
                            pat_alta = st.text_input("Apellido Paterno*:", value=str(row_alta.get("apellido_paterno", "")))
                            mat_alta = st.text_input("Apellido Materno:", value=str(row_alta.get("apellido_materno", "") or ""))

                        with c2:
                            suc_nom = st.selectbox("Sucursal Local*:", list(dict_suc.keys()))
                            dep_nom = st.selectbox("Departamento Local*:", list(dict_dep.keys()))
                            pue_nom = st.selectbox("Puesto Local*:", list(dict_pue.keys()))
                            contrato_nom = st.selectbox("Tipo de Contrato:", list(dict_contrato.keys()))

                        btn_guardar_indiv = st.form_submit_button("💾 Guardar y Registrar en Base de Datos Local", type="primary")

                        if btn_guardar_indiv:
                            if not nom_alta.strip() or not pat_alta.strip():
                                st.warning("⚠️ Nombre y Apellido Paterno son obligatorios.")
                            else:
                                ok, err_alta = guardar_alta_individual(
                                    codigo=cod_alta_sel,
                                    nombre=nom_alta,
                                    ap_pat=pat_alta,
                                    ap_mat=mat_alta,
                                    id_suc=int(dict_suc[suc_nom]),
                                    id_dep=int(dict_dep[dep_nom]),
                                    id_pue=int(dict_pue[pue_nom]),
                                    id_contrato=int(dict_contrato[contrato_nom]),
                                    id_estatus=1
                                )
                                if ok:
                                    st.session_state["mensaje_exito_sync"] = f"🎉 ¡Colaborador `{nom_alta.strip()} {pat_alta.strip()}` (Código: {cod_alta_sel}) registrado con éxito en `{suc_nom}` como `{pue_nom}`!"
                                    del st.session_state["diag_data"]
                                    st.rerun()
                                else:
                                    st.error(f"Error al registrar empleado: {err_alta}")

                st.divider()
                st.markdown("##### 📋 Listado Completo de Altas Pendientes")
                st.dataframe(
                    altas_detectadas[["codigo_disp", "nombre_completo"]].rename(columns={
                        "codigo_disp": "Código",
                        "nombre_completo": "Nombre Completo"
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("✅ La base de datos local está al día con las altas del VPS.")

render_sincronizador = render