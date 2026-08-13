import streamlit as st
import pandas as pd
from database import obtener_conexion

DICT_TIPO_CORREO = {"Corporativo": 1, "Gmail": 2}
DICT_TIPO_CORREO_REV = {1: "Corporativo", 2: "Gmail"}

DICT_ESTATUS_CORREO = {"ACTIVO": 1, "INACTIVO": 2}
DICT_ESTATUS_CORREO_REV = {1: "ACTIVO", 2: "INACTIVO"}

DICT_ESTATUS_EMP = {"ACTIVO": 1, "INACTIVO": 2, "BAJA": 3}
DICT_ESTATUS_EMP_REV = {1: "ACTIVO", 2: "INACTIVO", 3: "BAJA"}

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
        st.error(f"⚠️ Error al cargar catálogo {tabla}: {e}")
        return {}

def existe_correo_duplicado(direccion, id_correo_actual=None):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        dir_clean = direccion.strip().lower()
        if id_correo_actual:
            cursor.execute("SELECT COUNT(*) FROM correos_electronicos WHERE LOWER(direccion_correo) = %s AND id_correo != %s", (dir_clean, id_correo_actual))
        else:
            cursor.execute("SELECT COUNT(*) FROM correos_electronicos WHERE LOWER(direccion_correo) = %s", (dir_clean,))
        
        cnt = cursor.fetchone()[0]
        conn.close()
        return cnt > 0
    except Exception:
        return False

# ==============================================================================
# OPERACIONES: CORREOS ELECTRÓNICOS
# ==============================================================================
def obtener_correos_df():
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cols_reales = obtener_columnas_tabla(cursor, "correos_electronicos")
        
        col_pass_nom = None
        for cand in ['contrasena', 'password', 'clave', 'pass']:
            if cand in cols_reales:
                col_pass_nom = cand
                break

        select_pass = f", ce.{col_pass_nom} AS contrasena" if col_pass_nom else ", '' AS contrasena"

        query = f"""
            SELECT 
                ce.id_correo,
                ce.codigo_empleado,
                CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS empleado,
                ce.direccion_correo
                {select_pass},
                ce.id_tipo_correo,
                ce.id_estatus_correo
            FROM correos_electronicos ce
            LEFT JOIN empleados e ON ce.codigo_empleado = e.codigo
            ORDER BY e.nombre ASC, ce.id_correo DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        if not df.empty:
            df["tipo_correo"] = df["id_tipo_correo"].map(DICT_TIPO_CORREO_REV).fillna("Otro")
            df["estatus_correo"] = df["id_estatus_correo"].map(DICT_ESTATUS_CORREO_REV).fillna("ACTIVO")
        return df
    except Exception as e:
        st.error(f"⚠️ Error al consultar correos: {e}")
        return pd.DataFrame()

def guardar_correo_bdd(id_correo, codigo_emp, direccion, pass_val, id_tipo, id_estatus):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        codigo_emp_str = str(codigo_emp).strip()
        direccion_clean = str(direccion).strip().lower()

        cols_reales = obtener_columnas_tabla(cursor, "correos_electronicos")
        col_pass_nom = None
        for cand in ['contrasena', 'password', 'clave', 'pass']:
            if cand in cols_reales:
                col_pass_nom = cand
                break

        if id_correo:
            if col_pass_nom:
                query = f"""
                    UPDATE correos_electronicos 
                    SET codigo_empleado = %s, direccion_correo = %s, {col_pass_nom} = %s, id_tipo_correo = %s, id_estatus_correo = %s
                    WHERE id_correo = %s
                """
                cursor.execute(query, (codigo_emp_str, direccion_clean, pass_val, id_tipo, id_estatus, id_correo))
            else:
                query = """
                    UPDATE correos_electronicos 
                    SET codigo_empleado = %s, direccion_correo = %s, id_tipo_correo = %s, id_estatus_correo = %s
                    WHERE id_correo = %s
                """
                cursor.execute(query, (codigo_emp_str, direccion_clean, id_tipo, id_estatus, id_correo))
        else:
            if col_pass_nom:
                query = f"""
                    INSERT INTO correos_electronicos (codigo_empleado, direccion_correo, {col_pass_nom}, id_tipo_correo, id_estatus_correo)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (codigo_emp_str, direccion_clean, pass_val, id_tipo, id_estatus))
            else:
                query = """
                    INSERT INTO correos_electronicos (codigo_empleado, direccion_correo, id_tipo_correo, id_estatus_correo)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (codigo_emp_str, direccion_clean, id_tipo, id_estatus))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error en la base de datos al guardar correo: {e}")
        return False

# ==============================================================================
# OPERACIONES: EMPLEADOS
# ==============================================================================
def obtener_empleados_completos_df():
    try:
        conn = obtener_conexion()
        query = """
            SELECT 
                e.codigo,
                e.nombre,
                e.apellido_paterno,
                e.apellido_materno,
                CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS nombre_completo,
                e.id_sucursal, s.nombre_sucursal AS sucursal,
                e.id_departamento, d.nombre_departamento AS departamento,
                e.id_puesto, p.nombre_puesto AS puesto,
                e.id_estatus_empleado
            FROM empleados e
            LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
            LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento
            LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
            ORDER BY nombre_completo ASC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        if not df.empty:
            df["codigo_str"] = df["codigo"].astype(str).str.strip()
            df["estatus_empleado"] = df["id_estatus_empleado"].map(DICT_ESTATUS_EMP_REV).fillna("ACTIVO")
        return df
    except Exception as e:
        st.error(f"⚠️ Error al cargar empleados: {e}")
        return pd.DataFrame()

def actualizar_empleado_bdd(codigo, nombre, ap_pat, ap_mat, id_suc, id_dep, id_pue, id_estatus):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        codigo_clean = str(codigo).strip()

        query = """
            UPDATE empleados
            SET nombre = %s, apellido_paterno = %s, apellido_materno = %s,
                id_sucursal = %s, id_departamento = %s, id_puesto = %s, id_estatus_empleado = %s
            WHERE codigo = %s
        """
        cursor.execute(query, (nombre.strip(), ap_pat.strip(), ap_mat.strip() if ap_mat else None,
                              id_suc, id_dep, id_pue, id_estatus, codigo_clean))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error en la base de datos al actualizar empleado: {e}")
        return False

# ==============================================================================
# RENDER PRINCIPAL
# ==============================================================================
def render():
    aplicar_estilos_pantalla()
    st.title("📧 Administración de Correos y Empleados")

    tab_correos, tab_empleados = st.tabs(["📧 Gestión de Correos Electrónicos", "👤 Modificación de Empleados"])

    # --------------------------------------------------------------------------
    # TAB 1: CORREOS ELECTRÓNICOS (Alta y Edición)
    # --------------------------------------------------------------------------
    with tab_correos:
        st.subheader("✉️ Registro y Edición de Cuentas de Correo")

        df_emp = obtener_empleados_completos_df()
        df_correos = obtener_correos_df()

        if df_emp.empty:
            st.warning("⚠️ No hay empleados registrados para asociar correos.")
            return

        c_accion, _ = st.columns([1, 2])
        modo_correo = c_accion.radio("Acción de Correo:", ["➕ Crear Nuevo Correo", "✏️ Editar Existente"], horizontal=True)

        id_correo_edit = None
        emp_codigo_def = df_emp["codigo_str"].iloc[0]
        dir_correo_def = ""
        pass_correo_def = ""
        tipo_id_def = 1
        estatus_id_def = 1

        if modo_correo == "✏️ Editar Existente":
            if df_correos.empty:
                st.info("No hay correos registrados aún para editar.")
            else:
                lista_c = [f"ID {r['id_correo']} | {r['empleado']} - {r['direccion_correo']} ({r['tipo_correo']})" for _, r in df_correos.iterrows()]
                sel_c = st.selectbox("Selecciona la cuenta a modificar:", lista_c)
                idx_c = lista_c.index(sel_c)
                row_c = df_correos.iloc[idx_c]

                id_correo_edit = row_c["id_correo"]
                emp_codigo_def = str(row_c["codigo_empleado"]).strip()
                dir_correo_def = row_c["direccion_correo"]
                pass_correo_def = row_c["contrasena"] or ""
                tipo_id_def = row_c["id_tipo_correo"]
                estatus_id_def = row_c["id_estatus_correo"]

        st.divider()

        with st.form("form_correo"):
            c1, c2 = st.columns(2)
            with c1:
                lista_emp_opts = [f"{r['codigo_str']} - {r['nombre_completo']}" for _, r in df_emp.iterrows()]
                idx_emp_def = 0
                for i, r in enumerate(df_emp.iterrows()):
                    if r[1]["codigo_str"] == emp_codigo_def:
                        idx_emp_def = i
                        break
                
                emp_sel = st.selectbox("Colaborador:", lista_emp_opts, index=idx_emp_def)
                cod_emp_final = emp_sel.split(" - ")[0]

                direccion_in = st.text_input("Dirección de Correo Electrónico:", value=dir_correo_def, placeholder="ejemplo@agrocisa.com o usuario@gmail.com")
                pass_in = st.text_input("Contraseña del Correo:", value=pass_correo_def, type="password", placeholder="Ingresa la contraseña del correo")

            with c2:
                idx_tipo_def = list(DICT_TIPO_CORREO.values()).index(tipo_id_def) if tipo_id_def in DICT_TIPO_CORREO.values() else 0
                tipo_nom = st.selectbox("Tipo de Correo:", list(DICT_TIPO_CORREO.keys()), index=idx_tipo_def)

                idx_est_def = list(DICT_ESTATUS_CORREO.values()).index(estatus_id_def) if estatus_id_def in DICT_ESTATUS_CORREO.values() else 0
                estatus_nom = st.selectbox("Estatus de la Cuenta:", list(DICT_ESTATUS_CORREO.keys()), index=idx_est_def)

            btn_guardar_correo = st.form_submit_button("💾 Guardar Cuenta de Correo", type="primary")

            if btn_guardar_correo:
                if not direccion_in.strip() or "@" not in direccion_in:
                    st.warning("⚠️ Ingresa una dirección de correo válida.")
                elif existe_correo_duplicado(direccion_in, id_correo_edit):
                    st.error(f"⛔ El correo `{direccion_in.strip().lower()}` ya está registrado en la base de datos.")
                else:
                    if guardar_correo_bdd(
                        id_correo=id_correo_edit,
                        codigo_emp=cod_emp_final,
                        direccion=direccion_in,
                        pass_val=pass_in.strip(),
                        id_tipo=DICT_TIPO_CORREO[tipo_nom],
                        id_estatus=DICT_ESTATUS_CORREO[estatus_nom]
                    ):
                        st.toast("¡Cuenta de correo guardada con éxito!", icon="🎉")
                        st.rerun()

        st.divider()
        st.markdown("### 📋 Directorio de Correos Registrados")
        
        if not df_correos.empty:
            f1, f2 = st.columns(2)
            with f1:
                txt_busqueda = st.text_input("🔍 Buscar correo o colaborador:", placeholder="Ej. Juan, 00595, agrocisa.com")
            with f2:
                estatus_opts = ["Todos"] + list(DICT_ESTATUS_CORREO.keys())
                estatus_sel = st.selectbox("Filtrar por Estatus de Correo:", estatus_opts)

            df_filt = df_correos.copy()

            if txt_busqueda.strip():
                term = txt_busqueda.strip().lower()
                df_filt = df_filt[
                    df_filt["empleado"].astype(str).str.lower().str.contains(term) |
                    df_filt["codigo_empleado"].astype(str).str.lower().str.contains(term) |
                    df_filt["direccion_correo"].astype(str).str.lower().str.contains(term)
                ]

            if estatus_sel != "Todos":
                df_filt = df_filt[df_filt["estatus_correo"] == estatus_sel]

            cols_mostrar = ["id_correo", "codigo_empleado", "empleado", "direccion_correo", "tipo_correo", "estatus_correo"]
            st.dataframe(
                df_filt[cols_mostrar],
                use_container_width=True,
                hide_index=True
            )
            st.caption(f"Mostrando **{len(df_filt)}** de **{len(df_correos)}** cuentas registradas.")

    # --------------------------------------------------------------------------
    # TAB 2: EDICIÓN EXCLUSIVA DE EMPLEADOS
    # --------------------------------------------------------------------------
    with tab_empleados:
        st.subheader("👤 Edición de Datos de Colaboradores Existentes")

        df_emp_comp = obtener_empleados_completos_df()
        dict_suc = obtener_catalogo_dict("sucursales", "id_sucursal", "nombre_sucursal")
        dict_dep = obtener_catalogo_dict("departamentos", "id_departamento", "nombre_departamento")
        dict_pue = obtener_catalogo_dict("puestos", "id_puesto", "nombre_puesto")

        if df_emp_comp.empty:
            st.warning("No hay colaboradores registrados en la base de datos.")
            return

        lista_e_opts = [f"{r['codigo_str']} - {r['nombre_completo']} ({r['sucursal']})" for _, r in df_emp_comp.iterrows()]
        emp_edit_sel = st.selectbox("Selecciona el colaborador a modificar:", lista_e_opts)
        idx_e = lista_e_opts.index(emp_edit_sel)
        row_e = df_emp_comp.iloc[idx_e]

        cod_def = row_e["codigo_str"]
        nom_def = row_e["nombre"]
        pat_def = row_e["apellido_paterno"]
        mat_def = row_e["apellido_materno"] or ""
        suc_id_def = row_e["id_sucursal"]
        dep_id_def = row_e["id_departamento"]
        pue_id_def = row_e["id_puesto"]
        est_id_def = row_e["id_estatus_empleado"]

        st.divider()

        with st.form("form_empleado"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.text_input("Código de Empleado (ID):", value=cod_def, disabled=True)
                nom_in = st.text_input("Nombre(s):", value=nom_def)

            with c2:
                pat_in = st.text_input("Apellido Paterno:", value=pat_def)
                mat_in = st.text_input("Apellido Materno:", value=mat_def)

            with c3:
                idx_suc = list(dict_suc.values()).index(suc_id_def) if suc_id_def in dict_suc.values() else 0
                suc_nom = st.selectbox("Sucursal:", list(dict_suc.keys()), index=idx_suc)

                idx_dep = list(dict_dep.values()).index(dep_id_def) if dep_id_def in dict_dep.values() else 0
                dep_nom = st.selectbox("Departamento:", list(dict_dep.keys()), index=idx_dep)

                idx_pue = list(dict_pue.values()).index(pue_id_def) if pue_id_def in dict_pue.values() else 0
                pue_nom = st.selectbox("Puesto:", list(dict_pue.keys()), index=idx_pue)

                idx_est_e = list(DICT_ESTATUS_EMP.values()).index(est_id_def) if est_id_def in DICT_ESTATUS_EMP.values() else 0
                est_e_nom = st.selectbox("Estatus del Empleado:", list(DICT_ESTATUS_EMP.keys()), index=idx_est_e)

            btn_guardar_emp = st.form_submit_button("💾 Actualizar Datos del Empleado", type="primary")

            if btn_guardar_emp:
                if not nom_in.strip() or not pat_in.strip():
                    st.warning("⚠️ El Nombre y Apellido Paterno son obligatorios.")
                else:
                    if actualizar_empleado_bdd(
                        codigo=cod_def,
                        nombre=nom_in,
                        ap_pat=pat_in,
                        ap_mat=mat_in,
                        id_suc=dict_suc[suc_nom],
                        id_dep=dict_dep[dep_nom],
                        id_pue=dict_pue[pue_nom],
                        id_estatus=DICT_ESTATUS_EMP[est_e_nom]
                    ):
                        st.toast("¡Datos del colaborador actualizados en BDD!", icon="🎉")
                        st.rerun()

        st.divider()
        st.markdown("### 📋 Directorio General de Empleados")
        st.dataframe(
            df_emp_comp[["codigo_str", "nombre_completo", "sucursal", "departamento", "puesto", "estatus_empleado"]],
            use_container_width=True,
            hide_index=True
        )