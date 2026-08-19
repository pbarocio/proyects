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

def notificar_exito(mensaje):
    st.session_state["mensaje_exito_linea"] = mensaje
    st.rerun()

def generar_excel_bytes(df_exportar, nombre_hoja="Lineas_Telefonicas"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_exportar.to_excel(writer, index=False, sheet_name=nombre_hoja)
    buffer.seek(0)
    return buffer

def obtener_catalogo_estatus_lineas():
    """Consulta la tabla oficial estatus_linea_telefonica directamente de MariaDB."""
    try:
        conn = obtener_conexion()
        if not conn:
            return {}
        df = pd.read_sql("SELECT id_estatus_linea, estatus_linea FROM estatus_linea_telefonica ORDER BY id_estatus_linea ASC", conn)
        conn.close()
        if not df.empty:
            return dict(zip(df["estatus_linea"].astype(str), df["id_estatus_linea"].astype(int)))
        return {}
    except Exception as e:
        st.error(f"⚠️ Error al consultar catálogo 'estatus_linea_telefonica': {e}")
        return {}

# ==============================================================================
# OPERACIONES BDD: LÍNEAS TELEFÓNICAS
# ==============================================================================
def obtener_lineas_completas_df():
    try:
        conn = obtener_conexion()
        query = """
            SELECT 
                lt.numero,
                COALESCE(NULLIF(CAST(lt.plan_2026 AS CHAR), ''), NULLIF(CAST(lt.plan_2024 AS CHAR), ''), '') AS plan,
                COALESCE(NULLIF(CAST(lt.GB_promocion_2026 AS CHAR), ''), NULLIF(CAST(lt.GB_2026 AS CHAR), ''), NULLIF(CAST(lt.GB_2024 AS CHAR), ''), '') AS gb,
                CASE WHEN lt.is_mpp = 1 OR lt.is_mpp = '1' OR LOWER(CAST(lt.is_mpp AS CHAR)) IN ('si', 'sí', 'true') THEN '🔒 Sí' ELSE '🔓 No' END AS mpp_disp,
                lt.is_mpp,
                CASE WHEN lt.knox = 1 OR lt.knox = '1' OR LOWER(CAST(lt.knox AS CHAR)) IN ('si', 'sí', 'true') THEN '🔒 Sí' ELSE '🔓 No' END AS knox_disp,
                lt.knox,
                COALESCE(elt.estatus_linea, 'DISPONIBLE') AS estatus_linea,
                lt.id_estatus_linea,
                lt.codigo_empleado,
                COALESCE(CONCAT_WS(' ', emp.nombre, emp.apellido_paterno, emp.apellido_materno), 'SIN ASIGNAR') AS titular,
                COALESCE(suc.nombre_sucursal, 'SIN SUCURSAL') AS sucursal,
                COALESCE(dep.nombre_departamento, 'SIN DEPARTAMENTO') AS departamento,
                COALESCE(pue.nombre_puesto, 'SIN PUESTO') AS puesto,
                COALESCE(lt.comentarios, '') AS comentarios,
                COALESCE(lt.mensualidad_2026, 0.0) AS mensualidad_2026,
                COALESCE(lt.GB_promocion_2026, 0.0) AS gb_promocion_2026
            FROM lineas_telefonicas lt
            LEFT JOIN estatus_linea_telefonica elt ON lt.id_estatus_linea = elt.id_estatus_linea
            LEFT JOIN empleados emp ON TRIM(LEADING '0' FROM CAST(lt.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(emp.codigo AS CHAR))
            LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
            LEFT JOIN departamentos dep ON emp.id_departamento = dep.id_departamento
            LEFT JOIN puestos pue ON emp.id_puesto = pue.id_puesto
            ORDER BY lt.numero ASC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error al consultar líneas telefónicas: {e}")
        return pd.DataFrame()

def guardar_nueva_linea_bdd(numero, codigo_emp, id_estatus, is_mpp, knox, plan_2026, mensualidad, gb_2026, gb_promo, comentarios=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        num_clean = str(numero).strip()
        cod_emp = str(codigo_emp).strip() if codigo_emp else None
        com_clean = limpiar_str(comentarios) or None

        query = """
            INSERT INTO lineas_telefonicas (
                numero, codigo_empleado, id_estatus_linea, is_mpp, knox, 
                plan_2026, mensualidad_2026, GB_2026, GB_promocion_2026, comentarios
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                codigo_empleado = VALUES(codigo_empleado),
                id_estatus_linea = VALUES(id_estatus_linea),
                is_mpp = VALUES(is_mpp),
                knox = VALUES(knox),
                plan_2026 = VALUES(plan_2026),
                mensualidad_2026 = VALUES(mensualidad_2026),
                GB_2026 = VALUES(GB_2026),
                GB_promocion_2026 = VALUES(GB_promocion_2026),
                comentarios = VALUES(comentarios)
        """
        cursor.execute(query, (
            num_clean, cod_emp, int(id_estatus), int(is_mpp), int(knox),
            str(plan_2026).strip() if plan_2026 else None,
            float(mensualidad), float(gb_2026), float(gb_promo), com_clean
        ))
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

def actualizar_linea_bdd(num_viejo, num_nuevo, codigo_emp, id_estatus, is_mpp, knox, plan_2026, mensualidad, gb_2026, gb_promo, comentarios=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        num_v = str(num_viejo).strip()
        num_n = str(num_nuevo).strip()
        cod_emp = str(codigo_emp).strip() if codigo_emp else None
        com_clean = limpiar_str(comentarios) or None

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        query = """
            UPDATE lineas_telefonicas
            SET numero = %s, codigo_empleado = %s, id_estatus_linea = %s, is_mpp = %s, knox = %s,
                plan_2026 = %s, mensualidad_2026 = %s, GB_2026 = %s, GB_promocion_2026 = %s, comentarios = %s
            WHERE numero = %s
        """
        cursor.execute(query, (
            num_n, cod_emp, int(id_estatus), int(is_mpp), int(knox),
            str(plan_2026).strip() if plan_2026 else None,
            float(mensualidad), float(gb_2026), float(gb_promo), com_clean, num_v
        ))

        if num_v != num_n:
            cursor.execute("UPDATE responsivas_celulares SET numero = %s WHERE numero = %s", (num_n, num_v))
            cursor.execute("UPDATE inventario_celulares SET numero = %s WHERE numero = %s", (num_n, num_v))

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        return False, str(e)

# ==============================================================================
# RENDER PRINCIPAL
# ==============================================================================
def render():
    aplicar_estilos_pantalla()
    st.title("📞 Gestión y Edición de Líneas Telefónicas")

    if "mensaje_exito_linea" in st.session_state:
        st.success(st.session_state["mensaje_exito_linea"])
        del st.session_state["mensaje_exito_linea"]

    dict_est_lineas = obtener_catalogo_estatus_lineas()

    # Cargar empleados activos para asignación
    dict_empleados = {}
    try:
        conn = obtener_conexion()
        df_e = pd.read_sql("""
            SELECT codigo, CONCAT_WS(' ', nombre, apellido_paterno, apellido_materno) AS nom, s.nombre_sucursal AS sucursal
            FROM empleados e
            LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
            WHERE e.id_estatus_empleado = 1
            ORDER BY nom ASC
        """, conn)
        conn.close()
        for _, r in df_e.iterrows():
            dict_empleados[f"{str(r['codigo']).zfill(5)} - {r['nom']} ({r['sucursal']})"] = str(r['codigo']).strip()
    except Exception:
        pass

    tab_cat, tab_add, tab_edit = st.tabs([
        "📋 Catálogo General de Líneas",
        "➕ Registrar Nueva Línea",
        "✏️ Editar Línea / Cambiar Estatus"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: CATÁLOGO GENERAL
    # --------------------------------------------------------------------------
    with tab_cat:
        df_lineas = obtener_lineas_completas_df()
        
        if not df_lineas.empty:
            c_auto, c_est = st.columns([2, 1])
            with c_auto:
                opts_auto = [
                    f"{r['numero']} | {r['titular']} ({r['sucursal']}) [{r['estatus_linea']}]"
                    for _, r in df_lineas.iterrows()
                ]
                sel_auto = st.selectbox(
                    "🔍 Autocompletar por Número o Titular:",
                    opts_auto,
                    index=None,
                    placeholder="🔍 Teclea aquí el número telefónico, titular o sucursal...",
                    key="sel_auto_lineas_v3"
                )

            with c_est:
                opts_est = ["Todos"] + sorted(list(df_lineas["estatus_linea"].dropna().unique()))
                est_sel = st.selectbox("Filtrar por Estatus de Línea:", opts_est, key="filtro_est_lineas_v3")

            c_busq, f1, f2, f3 = st.columns([1.5, 1, 1, 1])
            with c_busq:
                txt_busq = st.text_input("Búsqueda libre:", placeholder="Ej. Juan, 3931234567...", key="txt_busq_lineas_v3")
            with f1:
                opts_suc = ["Todas"] + sorted(list(df_lineas["sucursal"].dropna().unique()))
                suc_sel = st.selectbox("Sucursal:", opts_suc, key="suc_f_lineas_v3")
            with f2:
                opts_dep = ["Todos"] + sorted(list(df_lineas["departamento"].dropna().unique()))
                dep_sel = st.selectbox("Departamento:", opts_dep, key="dep_f_lineas_v3")
            with f3:
                opts_pue = ["Todos"] + sorted(list(df_lineas["puesto"].dropna().unique()))
                pue_sel = st.selectbox("Puesto:", opts_pue, key="pue_f_lineas_v3")

            df_filt = df_lineas.copy()

            if sel_auto:
                num_sel = sel_auto.split(" | ")[0].strip()
                df_filt = df_filt[df_filt["numero"].astype(str) == num_sel]
            else:
                if est_sel != "Todos":
                    df_filt = df_filt[df_filt["estatus_linea"] == est_sel]
                if suc_sel != "Todas":
                    df_filt = df_filt[df_filt["sucursal"] == suc_sel]
                if dep_sel != "Todos":
                    df_filt = df_filt[df_filt["departamento"] == dep_sel]
                if pue_sel != "Todos":
                    df_filt = df_filt[df_filt["puesto"] == pue_sel]

                if txt_busq.strip():
                    term = txt_busq.strip().lower()
                    cols_str = ["numero", "titular", "sucursal", "departamento", "puesto", "comentarios", "plan"]
                    mascara = pd.Series(False, index=df_filt.index)
                    for col in cols_str:
                        mascara |= df_filt[col].astype(str).str.lower().str.contains(term, na=False)
                    df_filt = df_filt[mascara]

            cols_view = ["numero", "plan", "gb", "mpp_disp", "knox_disp", "estatus_linea", "titular", "sucursal", "departamento", "puesto", "comentarios"]
            st.dataframe(
                df_filt[cols_view].rename(columns={
                    "numero": "Número",
                    "plan": "Plan",
                    "gb": "GB",
                    "mpp_disp": "MPP",
                    "knox_disp": "Knox",
                    "estatus_linea": "Estatus",
                    "titular": "Titular Asignado",
                    "sucursal": "Sucursal",
                    "departamento": "Departamento",
                    "puesto": "Puesto",
                    "comentarios": "Comentarios"
                }),
                use_container_width=True,
                hide_index=True
            )

            col_inf, col_btn = st.columns([3, 1])
            with col_inf:
                st.caption(f"Mostrando **{len(df_filt)}** de **{len(df_lineas)}** líneas encontradas.")
            with col_btn:
                st.download_button(
                    label="📊 Exportar a Excel (.xlsx)",
                    data=generar_excel_bytes(df_filt, "Lineas_Telefonicas"),
                    file_name="Lineas_Telefonicas_AGROCISA.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )
        else:
            st.info("No hay líneas telefónicas registradas en la base de datos.")

    # --------------------------------------------------------------------------
    # TAB 2: REGISTRAR NUEVA LÍNEA
    # --------------------------------------------------------------------------
    with tab_add:
        st.subheader("➕ Alta de Nueva Línea Telefónica")
        with st.form("form_add_linea_v3"):
            c1, c2 = st.columns(2)
            with c1:
                num_in = st.text_input("Número Telefónico (10 dígitos)*:", placeholder="Ej. 3931234567")
                
                lista_emp_add = ["SIN ASIGNAR (Línea Libre / Vacante)"] + list(dict_empleados.keys())
                emp_sel_add = st.selectbox("Colaborador Asignado:", lista_emp_add)
                
                id_est_def = dict_est_lineas.get("DISPONIBLE", 4)
                idx_est = list(dict_est_lineas.values()).index(id_est_def) if id_est_def in dict_est_lineas.values() else 0
                est_sel_add = st.selectbox("Estatus de la Línea*:", list(dict_est_lineas.keys()), index=idx_est)

            with c2:
                plan_in = st.text_input("Plan Telcel (ej. 4, 5, BASE, Plus 4):", value="4")
                mens_in = st.number_input("Mensualidad ($ MXN):", min_value=0.0, value=599.0, step=50.0)
                gb_in = st.number_input("GB Base del Plan:", min_value=0.0, value=15.0, step=1.0)
                gb_p_in = st.number_input("GB Promoción 2026:", min_value=0.0, value=22.5, step=1.0)

            c3, c4 = st.columns(2)
            with c3:
                mpp_check = st.checkbox("¿Tiene MPP (Módulo de Protección Personal)?", value=False)
            with c4:
                knox_check = st.checkbox("¿Tiene Knox / Administrador?", value=False)

            com_in = st.text_area("Comentarios / Observaciones de la Línea:", placeholder="Ej. Línea temporal, módem, directivo...")

            btn_add = st.form_submit_button("💾 Guardar Línea Telefónica", type="primary")

            if btn_add:
                if not num_in.strip() or len(num_in.strip()) < 10:
                    st.warning("⚠️ Ingresa un número telefónico válido a 10 dígitos.")
                else:
                    cod_final = None
                    if emp_sel_add != "SIN ASIGNAR (Línea Libre / Vacante)":
                        cod_final = dict_empleados[emp_sel_add]

                    ok, err_msg = guardar_nueva_linea_bdd(
                        numero=num_in,
                        codigo_emp=cod_final,
                        id_estatus=dict_est_lineas[est_sel_add],
                        is_mpp=1 if mpp_check else 0,
                        knox=1 if knox_check else 0,
                        plan_2026=plan_in.strip(),
                        mensualidad=mens_in,
                        gb_2026=gb_in,
                        gb_promo=gb_p_in,
                        comentarios=com_in
                    )
                    if ok:
                        st.session_state["mensaje_exito_linea"] = f"🎉 ¡Línea `{num_in.strip()}` registrada exitosamente!"
                        st.rerun()
                    else:
                        st.error(f"⛔ Error al registrar línea: {err_msg}")

    # --------------------------------------------------------------------------
    # TAB 3: EDITAR LÍNEA / MODIFICAR
    # --------------------------------------------------------------------------
    with tab_edit:
        df_lineas_ed = obtener_lineas_completas_df()
        if not df_lineas_ed.empty:
            opts_ed = [
                f"{r['numero']} | {r['titular']} ({r['sucursal']}) [{r['estatus_linea']}]"
                for _, r in df_lineas_ed.iterrows()
            ]
            sel_linea_edit = st.selectbox(
                "Selecciona o teclea la línea a editar:",
                opts_ed,
                index=None,
                placeholder="🔍 Teclea aquí el número telefónico para editar...",
                key="sel_linea_edit_v3"
            )

            if sel_linea_edit:
                num_edit_orig = sel_linea_edit.split(" | ")[0].strip()
                r_linea = df_lineas_ed[df_lineas_ed["numero"].astype(str) == num_edit_orig].iloc[0]

                st.divider()
                with st.form(f"form_edit_linea_v3_{num_edit_orig}"):
                    c1, c2 = st.columns(2)
                    with c1:
                        num_mod_in = st.text_input("Número Telefónico (Identificador):", value=str(r_linea["numero"]))
                        
                        lista_emp_ed = ["SIN ASIGNAR (Línea Libre / Vacante)"] + list(dict_empleados.keys())
                        
                        idx_emp = 0
                        if pd.notna(r_linea["codigo_empleado"]) and str(r_linea["codigo_empleado"]).strip():
                            cod_target = str(r_linea["codigo_empleado"]).strip().lstrip("0")
                            for idx_k, (k_nom, v_cod) in enumerate(dict_empleados.items(), start=1):
                                if v_cod.lstrip("0") == cod_target:
                                    idx_emp = idx_k
                                    break

                        emp_sel_ed = st.selectbox("Colaborador Asignado:", lista_emp_ed, index=idx_emp)
                        
                        # Estatus actual exacto
                        est_actual_nom = r_linea["estatus_linea"]
                        idx_est_ed = list(dict_est_lineas.keys()).index(est_actual_nom) if est_actual_nom in dict_est_lineas else 0
                        est_sel_ed = st.selectbox("Estatus de la Línea*:", list(dict_est_lineas.keys()), index=idx_est_ed)

                    with c2:
                        plan_mod_in = st.text_input("Plan Telcel:", value=str(r_linea["plan"]) if pd.notna(r_linea["plan"]) else "4")
                        mens_mod_in = st.number_input("Mensualidad ($ MXN):", min_value=0.0, value=float(r_linea["mensualidad_2026"] or 599.0), step=50.0)
                        gb_mod_in = st.number_input("GB Base:", min_value=0.0, value=float(r_linea["gb"] or 15.0), step=1.0)
                        gb_p_mod_in = st.number_input("GB Promoción 2026:", min_value=0.0, value=float(r_linea["gb_promocion_2026"] or 22.5), step=1.0)

                    c3, c4 = st.columns(2)
                    with c3:
                        mpp_mod = st.checkbox("¿Tiene MPP?", value=bool(r_linea["is_mpp"] == 1 or r_linea["is_mpp"] == '1'))
                    with c4:
                        knox_mod = st.checkbox("¿Tiene Knox / Administrador?", value=bool(r_linea["knox"] == 1 or r_linea["knox"] == '1'))

                    com_mod_in = st.text_area("Comentarios / Observaciones:", value=limpiar_str(r_linea["comentarios"]))

                    btn_update = st.form_submit_button("💾 Actualizar Línea Telefónica", type="primary")

                    if btn_update:
                        cod_final_ed = None
                        if emp_sel_ed != "SIN ASIGNAR (Línea Libre / Vacante)":
                            cod_final_ed = dict_empleados[emp_sel_ed]

                        ok, err_msg = actualizar_linea_bdd(
                            num_viejo=num_edit_orig,
                            num_nuevo=num_mod_in.strip(),
                            codigo_emp=cod_final_ed,
                            id_estatus=dict_est_lineas[est_sel_ed],
                            is_mpp=1 if mpp_mod else 0,
                            knox=1 if knox_mod else 0,
                            plan_2026=plan_mod_in.strip(),
                            mensualidad=mens_mod_in,
                            gb_2026=gb_mod_in,
                            gb_promo=gb_p_mod_in,
                            comentarios=com_mod_in
                        )
                        if ok:
                            st.session_state["mensaje_exito_linea"] = f"🎉 ¡Línea `{num_mod_in.strip()}` actualizada exitosamente con estatus: **{est_sel_ed}**!"
                            st.rerun()
                        else:
                            st.error(f"⛔ Error al actualizar línea: {err_msg}")
        else:
            st.info("No hay líneas telefónicas registradas para editar.")

render_lineas = render