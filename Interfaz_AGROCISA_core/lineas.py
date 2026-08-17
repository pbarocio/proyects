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

def limpiar_str(val, defecto=""):
    if val is None or pd.isna(val):
        return defecto
    v_str = str(val).strip()
    if v_str.lower() in ["", "nan", "none", "null", "<na>"]:
        return defecto
    return v_str

def obtener_columnas_tabla(cursor, tabla):
    try:
        cursor.execute(f"SHOW COLUMNS FROM {tabla}")
        return [row[0] for row in cursor.fetchall()]
    except Exception:
        return []

def obtener_catalogo_dict(tabla, col_id, col_nombre):
    try:
        conn = obtener_conexion()
        query = f"SELECT {col_id}, {col_nombre} FROM {tabla} ORDER BY {col_nombre} ASC"
        df = pd.read_sql(query, conn)
        conn.close()
        return dict(zip(df[col_nombre], df[col_id]))
    except Exception as e:
        return {}

def obtener_catalogo_estatus_lineas():
    """Detecta dinámicamente si existe tabla de estatus o usa el mapeo del sistema."""
    for tabla in ['estatus_linea', 'estatus_lineas']:
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(f"SHOW TABLES LIKE '{tabla}'")
            if cursor.fetchone():
                cols = obtener_columnas_tabla(cursor, tabla)
                col_id = cols[0]
                col_nom = cols[1] if len(cols) > 1 else cols[0]
                for c in cols:
                    if 'id' in c.lower(): col_id = c
                    if 'nom' in c.lower() or 'estatus' in c.lower() or 'opcion' in c.lower() or 'desc' in c.lower():
                        if 'id' not in c.lower(): col_nom = c
                
                df = pd.read_sql(f"SELECT {col_id}, {col_nom} FROM {tabla} ORDER BY {col_id}", conn)
                conn.close()
                if not df.empty:
                    return dict(zip(df[col_nom], df[col_id]))
            conn.close()
        except Exception:
            pass

    return {
        "ASIGNADO": 3,
        "DISPONIBLE": 4,
        "VIP": 5,
        "INACTIVO / BAJA": 2,
        "SUSPENDIDA": 6
    }

def notificar_exito(mensaje):
    st.session_state["mensaje_exito_linea"] = mensaje
    st.rerun()

def generar_excel_bytes(df_exportar, nombre_hoja="Lineas_Telefonicas"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_exportar.to_excel(writer, index=False, sheet_name=nombre_hoja)
    buffer.seek(0)
    return buffer

# ==============================================================================
# OPERACIONES DE BASE DE DATOS ADAPTATIVAS
# ==============================================================================
def obtener_lineas_completas_df(dict_est_rev):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cols_reales = obtener_columnas_tabla(cursor, "lineas_telefonicas")

        cand_plan = next((c for c in ['plan', 'id_plan', 'nombre_plan', 'tipo_plan', 'plan_tarifario'] if c in cols_reales), None)
        select_plan = f"COALESCE(CAST(lt.{cand_plan} AS CHAR), '') AS plan" if cand_plan else "'' AS plan"

        cand_gb = next((c for c in ['gb_promocion_2026', 'gb', 'datos_gb'] if c in cols_reales), None)
        select_gb = f"COALESCE(CAST(lt.{cand_gb} AS CHAR), '') AS gb" if cand_gb else "'' AS gb"

        cand_mpp = next((c for c in ['mpp', 'mpp_folio'] if c in cols_reales), None)
        select_mpp = f"COALESCE(CAST(lt.{cand_mpp} AS CHAR), '') AS mpp" if cand_mpp else "'' AS mpp"

        cand_knox = next((c for c in ['knox', 'seguridad_knox'] if c in cols_reales), None)
        if cand_knox:
            select_knox = f"CASE WHEN lt.{cand_knox} = 1 OR lt.{cand_knox} = '1' OR LOWER(CAST(lt.{cand_knox} AS CHAR)) IN ('si', 'sí', 'true') THEN '🔒 Sí' ELSE '🔓 No' END AS knox_disp, lt.{cand_knox} AS knox"
        else:
            select_knox = "'🔓 No' AS knox_disp, 0 AS knox"

        cand_est = next((c for c in ['id_estatus_linea', 'id_estatus', 'id_status'] if c in cols_reales), None)
        select_est = f"lt.{cand_est} AS id_estatus_linea" if cand_est else "4 AS id_estatus_linea"

        cand_emp = next((c for c in ['codigo_empleado', 'codigo', 'id_empleado'] if c in cols_reales), None)
        if cand_emp:
            join_emp = f"LEFT JOIN empleados e ON TRIM(LEADING '0' FROM CAST(lt.{cand_emp} AS CHAR)) = TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR))"
            select_emp = f"lt.{cand_emp} AS codigo_empleado"
        else:
            join_emp = "LEFT JOIN empleados e ON 1=0"
            select_emp = "NULL AS codigo_empleado"

        cand_com = next((c for c in ['comentarios', 'comentario'] if c in cols_reales), None)
        select_com = f"COALESCE(lt.{cand_com}, '') AS comentarios" if cand_com else "'' AS comentarios"

        cand_obs = next((c for c in ['observaciones', 'observacion'] if c in cols_reales), None)
        select_obs = f"COALESCE(lt.{cand_obs}, '') AS observaciones" if cand_obs else "'' AS observaciones"

        query = f"""
            SELECT 
                lt.numero,
                {select_plan},
                {select_gb},
                {select_mpp},
                {select_knox},
                {select_est},
                COALESCE(CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno), 'SIN ASIGNAR') AS titular,
                {select_emp},
                COALESCE(s.nombre_sucursal, 'SIN SUCURSAL') AS sucursal,
                COALESCE(d.nombre_departamento, 'SIN DEPARTAMENTO') AS departamento,
                COALESCE(p.nombre_puesto, 'SIN PUESTO') AS puesto,
                {select_com},
                {select_obs}
            FROM lineas_telefonicas lt
            {join_emp}
            LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
            LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento
            LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
            ORDER BY lt.numero ASC
        """
        df = pd.read_sql(query, conn)
        conn.close()

        if not df.empty:
            df["estatus_linea"] = df["id_estatus_linea"].map(dict_est_rev).fillna("DESCONOCIDO")

        return df
    except Exception as e:
        st.error(f"⚠️ Error al consultar líneas telefónicas: {e}")
        return pd.DataFrame()

def guardar_nueva_linea(numero, plan, gb, mpp, knox_val, id_estatus, codigo_emp, comentarios):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cols_reales = obtener_columnas_tabla(cursor, "lineas_telefonicas")
        
        datos = {}
        if "numero" in cols_reales:
            datos["numero"] = str(numero).strip()
            
        cand_plan = next((c for c in ['plan', 'id_plan', 'nombre_plan', 'tipo_plan'] if c in cols_reales), None)
        if cand_plan:
            datos[cand_plan] = str(plan).strip() or None
            
        cand_gb = next((c for c in ['gb_promocion_2026', 'gb', 'datos_gb'] if c in cols_reales), None)
        if cand_gb:
            datos[cand_gb] = str(gb).strip() or None
            
        cand_mpp = next((c for c in ['mpp', 'mpp_folio'] if c in cols_reales), None)
        if cand_mpp:
            datos[cand_mpp] = str(mpp).strip() or None
            
        cand_knox = next((c for c in ['knox', 'seguridad_knox'] if c in cols_reales), None)
        if cand_knox:
            datos[cand_knox] = knox_val
            
        cand_est = next((c for c in ['id_estatus_linea', 'id_estatus', 'id_status'] if c in cols_reales), None)
        if cand_est:
            datos[cand_est] = id_estatus
            
        cand_emp = next((c for c in ['codigo_empleado', 'codigo', 'id_empleado'] if c in cols_reales), None)
        if cand_emp:
            datos[cand_emp] = str(codigo_emp).strip() if codigo_emp else None
            
        cand_com = next((c for c in ['comentarios', 'comentario'] if c in cols_reales), None)
        if cand_com:
            datos[cand_com] = limpiar_str(comentarios) or None

        cols_str = ", ".join(datos.keys())
        placeholders = ", ".join(["%s"] * len(datos))
        query = f"INSERT INTO lineas_telefonicas ({cols_str}) VALUES ({placeholders})"
        cursor.execute(query, tuple(datos.values()))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar nueva línea: {e}")
        return False

def actualizar_linea(numero, plan, gb, mpp, knox_val, id_estatus, codigo_emp, comentarios, observaciones=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cols_reales = obtener_columnas_tabla(cursor, "lineas_telefonicas")
        
        updates = []
        valores = []
        
        cand_plan = next((c for c in ['plan', 'id_plan', 'nombre_plan', 'tipo_plan'] if c in cols_reales), None)
        if cand_plan:
            updates.append(f"{cand_plan} = %s")
            valores.append(str(plan).strip() or None)
            
        cand_gb = next((c for c in ['gb_promocion_2026', 'gb', 'datos_gb'] if c in cols_reales), None)
        if cand_gb:
            updates.append(f"{cand_gb} = %s")
            valores.append(str(gb).strip() or None)
            
        cand_mpp = next((c for c in ['mpp', 'mpp_folio'] if c in cols_reales), None)
        if cand_mpp:
            updates.append(f"{cand_mpp} = %s")
            valores.append(str(mpp).strip() or None)
            
        cand_knox = next((c for c in ['knox', 'seguridad_knox'] if c in cols_reales), None)
        if cand_knox:
            updates.append(f"{cand_knox} = %s")
            valores.append(knox_val)
            
        cand_est = next((c for c in ['id_estatus_linea', 'id_estatus', 'id_status'] if c in cols_reales), None)
        if cand_est:
            updates.append(f"{cand_est} = %s")
            valores.append(id_estatus)
            
        cand_emp = next((c for c in ['codigo_empleado', 'codigo', 'id_empleado'] if c in cols_reales), None)
        if cand_emp:
            updates.append(f"{cand_emp} = %s")
            valores.append(str(codigo_emp).strip() if codigo_emp else None)
            
        cand_com = next((c for c in ['comentarios', 'comentario'] if c in cols_reales), None)
        if cand_com:
            updates.append(f"{cand_com} = %s")
            valores.append(limpiar_str(comentarios) or None)
            
        cand_obs = next((c for c in ['observaciones', 'observacion'] if c in cols_reales), None)
        if cand_obs:
            updates.append(f"{cand_obs} = %s")
            valores.append(limpiar_str(observaciones) or None)
            
        if updates:
            set_str = ", ".join(updates)
            query = f"UPDATE lineas_telefonicas SET {set_str} WHERE numero = %s"
            valores.append(str(numero).strip())
            cursor.execute(query, tuple(valores))
            conn.commit()

        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al actualizar línea: {e}")
        return False

# ==============================================================================
# RENDER PRINCIPAL
# ==============================================================================
def render():
    aplicar_estilos_pantalla()
    st.title("📞 Gestión y Edición de Líneas Telefónicas")

    if "mensaje_exito_linea" in st.session_state:
        st.success(f"✅ {st.session_state['mensaje_exito_linea']}")
        del st.session_state["mensaje_exito_linea"]

    dict_est_lineas = obtener_catalogo_estatus_lineas()
    dict_est_rev = {v: k for k, v in dict_est_lineas.items()}
    defaults_fallback = {1: "ASIGNADO", 2: "INACTIVO / BAJA", 3: "ASIGNADO", 4: "DISPONIBLE", 5: "VIP", 6: "SUSPENDIDA"}
    for k_f, v_f in defaults_fallback.items():
        if k_f not in dict_est_rev:
            dict_est_rev[k_f] = v_f

    df_lineas = obtener_lineas_completas_df(dict_est_rev)
    
    dict_empleados = {}
    try:
        conn = obtener_conexion()
        df_e = pd.read_sql("SELECT codigo, CONCAT_WS(' ', nombre, apellido_paterno, apellido_materno) AS nom FROM empleados WHERE id_estatus_empleado = 1 ORDER BY nom ASC", conn)
        conn.close()
        for _, r in df_e.iterrows():
            dict_empleados[f"{str(r['codigo']).zfill(5)} - {r['nom']}"] = str(r['codigo']).strip()
    except Exception:
        pass

    tab_cat, tab_add, tab_edit = st.tabs([
        "📋 Catálogo General de Líneas",
        "➕ Registrar Nueva Línea",
        "✏️ Editar Línea / Cambiar Estatus VIP"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: CONSULTA CON AUTOCOMPLETADO
    # --------------------------------------------------------------------------
    with tab_cat:
        if not df_lineas.empty:
            opts_auto_lineas = [
                f"{r['numero']} | {r['titular']} | [{r['estatus_linea']}] | Plan: {r['plan'] or 'S/P'} ({r['sucursal']})"
                for _, r in df_lineas.iterrows()
            ]

            c_auto, c_est = st.columns([2, 1])
            with c_auto:
                sel_auto_linea = st.selectbox(
                    "🔍 Autocompletar por Número o Titular:",
                    opts_auto_lineas,
                    index=None,
                    placeholder="🔍 Teclea aquí el número telefónico, titular o sucursal...",
                    key="sel_auto_linea_cat"
                )
            with c_est:
                opts_est = ["Todos"] + sorted(list(df_lineas["estatus_linea"].dropna().unique()))
                est_sel = st.selectbox("Filtrar por Estatus de Línea:", opts_est, key="est_f_lineas")

            c_txt, c_suc = st.columns([2, 1])
            with c_txt:
                txt_busq = st.text_input("Búsqueda libre:", placeholder="Ej. Juan, 3931234567, SIN ASIGNAR, Morelia...", key="txt_f_lineas")
            with c_suc:
                opts_suc = ["Todas"] + sorted(list(df_lineas["sucursal"].dropna().unique()))
                suc_sel = st.selectbox("Filtrar por Sucursal:", opts_suc, key="suc_f_lineas")

            df_filtrado = df_lineas.copy()

            if sel_auto_linea:
                num_sel = sel_auto_linea.split(" | ")[0].strip()
                df_filtrado = df_filtrado[df_filtrado["numero"].astype(str).str.strip() == num_sel]
            else:
                if est_sel != "Todos":
                    df_filtrado = df_filtrado[df_filtrado["estatus_linea"] == est_sel]
                if suc_sel != "Todas":
                    df_filtrado = df_filtrado[df_filtrado["sucursal"] == suc_sel]
                if txt_busq.strip():
                    term = txt_busq.strip().lower()
                    df_filtrado = df_filtrado[
                        df_filtrado["numero"].astype(str).str.lower().str.contains(term) |
                        df_filtrado["titular"].astype(str).str.lower().str.contains(term) |
                        df_filtrado["sucursal"].astype(str).str.lower().str.contains(term) |
                        df_filtrado["departamento"].astype(str).str.lower().str.contains(term) |
                        df_filtrado["puesto"].astype(str).str.lower().str.contains(term) |
                        df_filtrado["comentarios"].astype(str).str.lower().str.contains(term)
                    ]

            cols_mostrar = ["numero", "plan", "gb", "mpp", "knox_disp", "estatus_linea", "titular", "sucursal", "comentarios"]
            st.dataframe(
                df_filtrado[cols_mostrar].rename(columns={"knox_disp": "Knox", "mpp": "MPP"}),
                use_container_width=True,
                hide_index=True
            )

            c_inf, c_btn = st.columns([3, 1])
            with c_inf:
                st.caption(f"Mostrando **{len(df_filtrado)}** de **{len(df_lineas)}** líneas encontradas.")
            with c_btn:
                st.download_button(
                    label="📊 Exportar a Excel (.xlsx)",
                    data=generar_excel_bytes(df_filtrado[cols_mostrar], "Lineas_Telefonicas"),
                    file_name="Lineas_Telefonicas_AGROCISA.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )
        else:
            st.info("No hay líneas telefónicas registradas en el sistema.")

    # --------------------------------------------------------------------------
    # TAB 2: REGISTRAR NUEVA LÍNEA
    # --------------------------------------------------------------------------
    with tab_add:
        st.subheader("➕ Alta de Nueva Línea Telefónica")
        with st.form("form_nueva_linea"):
            c1, c2, c3 = st.columns(3)
            with c1:
                nuevo_num = st.text_input("Número Telefónico (10 dígitos)*:", placeholder="Ej. 3931234567")
                plan_in = st.text_input("Plan Contratado:", placeholder="Ej. 1, 5, Telcel Plus...")
            with c2:
                gb_in = st.text_input("GB Incluidos / Promoción:", placeholder="Ej. 6, 9, 45...")
                mpp_in = st.text_input("MPP / Folio:", placeholder="Ej. MPP-12345")
            with c3:
                knox_check = st.checkbox("¿Tiene Knox / Seguridad Corporativa?", value=False)
                id_est_def = dict_est_lineas.get("DISPONIBLE", 4)
                idx_est = list(dict_est_lineas.values()).index(id_est_def) if id_est_def in dict_est_lineas.values() else 0
                est_sel_add = st.selectbox("Estatus Inicial:", list(dict_est_lineas.keys()), index=idx_est)

            st.divider()
            c_emp, c_com = st.columns(2)
            with c_emp:
                opts_emp = ["-- Sin Asignar / Vacante --"] + list(dict_empleados.keys())
                emp_sel_add = st.selectbox("Titular / Asignado Inicial (Opcional):", opts_emp)
                cod_emp_add = dict_empleados[emp_sel_add] if emp_sel_add != "-- Sin Asignar / Vacante --" else None
            with c_com:
                com_add = st.text_area("Comentarios de la Línea:", placeholder="Ej. Chip nuevo, renovación, etc.")

            btn_guardar_nueva = st.form_submit_button("💾 Guardar Línea Telefónica", type="primary")

            if btn_guardar_nueva:
                if not nuevo_num.strip() or len(nuevo_num.strip()) < 10:
                    st.warning("⚠️ Ingresa un número telefónico válido de 10 dígitos.")
                else:
                    knox_val = 1 if knox_check else 0
                    if guardar_nueva_linea(
                        numero=nuevo_num,
                        plan=plan_in,
                        gb=gb_in,
                        mpp=mpp_in,
                        knox_val=knox_val,
                        id_estatus=dict_est_lineas[est_sel_add],
                        codigo_emp=cod_emp_add,
                        comentarios=com_add
                    ):
                        notificar_exito(f"¡Línea {nuevo_num} dada de alta con éxito!")

    # --------------------------------------------------------------------------
    # TAB 3: EDITAR LÍNEA / CAMBIAR ESTATUS VIP
    # --------------------------------------------------------------------------
    with tab_edit:
        st.subheader("✏️ Modificación y Configuración de Líneas")
        if not df_lineas.empty:
            opts_lineas_edit = [
                f"{r['numero']} | {r['titular']} | [{r['estatus_linea']}] | Plan: {r['plan'] or 'S/P'} ({r['sucursal']})"
                for _, r in df_lineas.iterrows()
            ]

            linea_sel_edit = st.selectbox(
                "Selecciona o teclea la línea a modificar:",
                opts_lineas_edit,
                index=None,
                placeholder="🔍 Teclea aquí el número o titular a modificar...",
                key="sel_linea_edit_auto"
            )

            if linea_sel_edit:
                num_editar = linea_sel_edit.split(" | ")[0].strip()
                r = df_lineas[df_lineas["numero"].astype(str).str.strip() == num_editar].iloc[0]

                st.divider()
                with st.form(f"form_edicion_linea_{num_editar}"):
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.text_input("Número Telefónico:", value=str(r["numero"]), disabled=True)
                        e_plan = st.text_input("Plan:", value=limpiar_str(r["plan"]))
                    with c2:
                        e_gb = st.text_input("GB:", value=limpiar_str(r["gb"]))
                        e_mpp = st.text_input("MPP:", value=limpiar_str(r["mpp"]))
                    with c3:
                        knox_actual = bool(r["knox"] == 1 or r["knox"] == '1' or str(r["knox"]).lower() == 'si')
                        e_knox = st.checkbox("¿Tiene Knox / Seguridad?", value=knox_actual)
                        
                        idx_est_act = list(dict_est_lineas.values()).index(r["id_estatus_linea"]) if r["id_estatus_linea"] in dict_est_lineas.values() else 0
                        e_est = st.selectbox("Estatus de la Línea (VIP, Asignado, etc.):", list(dict_est_lineas.keys()), index=idx_est_act)

                    st.divider()
                    c_emp_e, c_com_e = st.columns(2)
                    with c_emp_e:
                        opts_emp_e = ["-- Sin Asignar / Vacante --"] + list(dict_empleados.keys())
                        cod_act_clean = str(r["codigo_empleado"]).strip().zfill(5) if r["codigo_empleado"] else None
                        
                        idx_emp_actual = 0
                        if cod_act_clean:
                            for idx_i, (k_nom, v_cod) in enumerate(dict_empleados.items(), start=1):
                                if v_cod.zfill(5) == cod_act_clean:
                                    idx_emp_actual = idx_i
                                    break

                        e_emp_sel = st.selectbox("Titular / Colaborador Asignado:", opts_emp_e, index=idx_emp_actual)
                        e_cod_emp = dict_empleados[e_emp_sel] if e_emp_sel != "-- Sin Asignar / Vacante --" else None

                    with c_com_e:
                        e_com = st.text_area("Comentarios:", value=limpiar_str(r["comentarios"]))

                    e_obs = st.text_area("Observaciones Generales / Historial:", value=limpiar_str(r["observaciones"]))

                    btn_guardar_edit = st.form_submit_button("💾 Actualizar Datos de la Línea", type="primary")

                    if btn_guardar_edit:
                        knox_final = 1 if e_knox else 0
                        if actualizar_linea(
                            numero=num_editar,
                            plan=e_plan,
                            gb=e_gb,
                            mpp=e_mpp,
                            knox_val=knox_final,
                            id_estatus=dict_est_lineas[e_est],
                            codigo_emp=e_cod_emp,
                            comentarios=e_com,
                            observaciones=e_obs
                        ):
                            notificar_exito(f"¡Línea {num_editar} actualizada correctamente!")
            else:
                st.info("👆 Selecciona o escribe una línea en el buscador de arriba para cargar sus datos.")
        else:
            st.info("No hay líneas registradas para editar.")

# Alias para compatibilidad de invocación en app.py
render_lineas = render