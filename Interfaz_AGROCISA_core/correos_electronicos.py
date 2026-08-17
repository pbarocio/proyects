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
        return {str(nom): int(cid) for nom, cid in zip(df[col_nombre], df[col_id])}
    except Exception:
        return {}

def obtener_catalogo_estatus_correos():
    """Consulta directamente la tabla oficial estatus_correos_electronicos."""
    tablas_posibles = [
        'estatus_correos_electronicos',
        'estatus_correo_electronico',
        'estatus_correos',
        'estatus_correo'
    ]
    for tabla in tablas_posibles:
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(f"SHOW TABLES LIKE '{tabla}'")
            if cursor.fetchone():
                cols = obtener_columnas_tabla(cursor, tabla)
                col_id = next((c for c in cols if 'id' in c.lower()), cols[0])
                col_nom = next((c for c in cols if any(k in c.lower() for k in ['nom', 'estatus', 'desc', 'opcion']) and c != col_id), cols[1] if len(cols) > 1 else cols[0])
                
                df = pd.read_sql(f"SELECT {col_id}, {col_nom} FROM {tabla} ORDER BY {col_id}", conn)
                conn.close()
                if not df.empty:
                    return {str(nom): int(cid) for nom, cid in zip(df[col_nom], df[col_id])}
            conn.close()
        except Exception:
            pass

    return {
        "ACTIVO": 1,
        "INACTIVO": 2
    }

def obtener_catalogo_tipos_correo():
    """Consulta la tabla de tipos de correos."""
    tablas_posibles = [
        'tipos_correos_electronicos',
        'tipo_correos_electronicos',
        'tipos_correo',
        'tipo_correo'
    ]
    for tabla in tablas_posibles:
        try:
            conn = obtener_conexion()
            cursor = conn.cursor()
            cursor.execute(f"SHOW TABLES LIKE '{tabla}'")
            if cursor.fetchone():
                cols = obtener_columnas_tabla(cursor, tabla)
                col_id = next((c for c in cols if 'id' in c.lower()), cols[0])
                col_nom = next((c for c in cols if any(k in c.lower() for k in ['nom', 'tipo', 'desc', 'opcion']) and c != col_id), cols[1] if len(cols) > 1 else cols[0])
                
                df = pd.read_sql(f"SELECT {col_id}, {col_nom} FROM {tabla} ORDER BY {col_id}", conn)
                conn.close()
                if not df.empty:
                    return {str(nom): int(cid) for nom, cid in zip(df[col_nom], df[col_id])}
            conn.close()
        except Exception:
            pass

    return {
        "Corporativo": 1,
        "Gmail": 2
    }

def existe_correo_duplicado(direccion, id_correo_actual=None):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        dir_clean = direccion.strip().lower()
        if id_correo_actual is not None:
            cursor.execute("SELECT COUNT(*) FROM correos_electronicos WHERE LOWER(direccion_correo) = %s AND id_correo != %s", (dir_clean, int(id_correo_actual)))
        else:
            cursor.execute("SELECT COUNT(*) FROM correos_electronicos WHERE LOWER(direccion_correo) = %s", (dir_clean,))
        
        cnt = cursor.fetchone()[0]
        conn.close()
        return cnt > 0
    except Exception:
        return False

def existe_codigo_empleado(codigo):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        codigo_clean = str(codigo).strip()
        cursor.execute("SELECT COUNT(*) FROM empleados WHERE TRIM(LEADING '0' FROM CAST(codigo AS CHAR)) = TRIM(LEADING '0' FROM CAST(%s AS CHAR))", (codigo_clean,))
        cnt = cursor.fetchone()[0]
        conn.close()
        return cnt > 0
    except Exception:
        return False

# ==============================================================================
# OPERACIONES: CORREOS ELECTRÓNICOS
# ==============================================================================
def obtener_correos_df(dict_tipo_rev, dict_est_rev):
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
            LEFT JOIN empleados e ON TRIM(LEADING '0' FROM CAST(ce.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR))
            ORDER BY e.nombre ASC, ce.id_correo DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        if not df.empty:
            df["tipo_correo"] = df["id_tipo_correo"].astype(int).map(dict_tipo_rev).fillna("Otro")
            df["estatus_correo"] = df["id_estatus_correo"].astype(int).map(dict_est_rev).fillna("DESCONOCIDO")
        return df
    except Exception as e:
        st.error(f"⚠️ Error al consultar correos: {e}")
        return pd.DataFrame()

def guardar_correo_bdd(id_correo, codigo_emp, direccion, pass_val, id_tipo, id_estatus):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        id_correo_val = int(id_correo) if id_correo is not None else None
        codigo_emp_str = str(codigo_emp).strip()
        direccion_clean = str(direccion).strip().lower()
        pass_clean = str(pass_val).strip() if pass_val else None
        id_tipo_val = int(id_tipo)
        id_estatus_val = int(id_estatus)

        cols_reales = obtener_columnas_tabla(cursor, "correos_electronicos")
        col_pass_nom = None
        for cand in ['contrasena', 'password', 'clave', 'pass']:
            if cand in cols_reales:
                col_pass_nom = cand
                break

        if id_correo_val is not None:
            if col_pass_nom:
                query = f"""
                    UPDATE correos_electronicos 
                    SET codigo_empleado = %s, direccion_correo = %s, {col_pass_nom} = %s, id_tipo_correo = %s, id_estatus_correo = %s
                    WHERE id_correo = %s
                """
                cursor.execute(query, (codigo_emp_str, direccion_clean, pass_clean, id_tipo_val, id_estatus_val, id_correo_val))
            else:
                query = """
                    UPDATE correos_electronicos 
                    SET codigo_empleado = %s, direccion_correo = %s, id_tipo_correo = %s, id_estatus_correo = %s
                    WHERE id_correo = %s
                """
                cursor.execute(query, (codigo_emp_str, direccion_clean, id_tipo_val, id_estatus_val, id_correo_val))
        else:
            if col_pass_nom:
                query = f"""
                    INSERT INTO correos_electronicos (codigo_empleado, direccion_correo, {col_pass_nom}, id_tipo_correo, id_estatus_correo)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (codigo_emp_str, direccion_clean, pass_clean, id_tipo_val, id_estatus_val))
            else:
                query = """
                    INSERT INTO correos_electronicos (codigo_empleado, direccion_correo, id_tipo_correo, id_estatus_correo)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.execute(query, (codigo_emp_str, direccion_clean, id_tipo_val, id_estatus_val))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error en la base de datos al guardar correo: {e}")
        return False

# ==============================================================================
# OPERACIONES: EMPLEADOS Y ACTUALIZACIÓN EN CASCADA
# ==============================================================================
def obtener_empleados_completos_df(dict_est_emp_rev):
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
            df["codigo_str"] = df["codigo"].astype(str).str.strip().str.zfill(5)
            df["estatus_empleado"] = df["id_estatus_empleado"].astype(int).map(dict_est_emp_rev).fillna("ACTIVO")
        return df
    except Exception as e:
        st.error(f"⚠️ Error al cargar empleados: {e}")
        return pd.DataFrame()

def guardar_nuevo_empleado_bdd(codigo, nombre, ap_pat, ap_mat, id_suc, id_dep, id_pue, id_estatus):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        codigo_clean = str(codigo).strip().zfill(5)

        query = """
            INSERT INTO empleados (codigo, nombre, apellido_paterno, apellido_materno, id_sucursal, id_departamento, id_puesto, id_estatus_empleado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            codigo_clean, 
            str(nombre).strip(), 
            str(ap_pat).strip(), 
            str(ap_mat).strip() if ap_mat else None,
            int(id_suc), 
            int(id_dep), 
            int(id_pue), 
            int(id_estatus)
        ))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error en la base de datos al guardar empleado: {e}")
        return False

def actualizar_empleado_en_cascada_bdd(codigo_viejo, codigo_nuevo, nombre, ap_pat, ap_mat, id_suc, id_dep, id_pue, id_estatus):
    """
    Actualiza los datos del empleado y, si se cambió el código de nómina,
    propaga el cambio en cascada a todos los inventarios, responsivas, líneas y correos
    desactivando temporalmente las restricciones de llave foránea.
    """
    conn = obtener_conexion()
    if not conn:
        return False
        
    cursor = conn.cursor()
    c_viejo = str(codigo_viejo).strip()
    c_nuevo = str(codigo_nuevo).strip().zfill(5)

    try:
        # 1. Desactivar validación de Foreign Keys en la sesión
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        # 2. Actualizar datos base del empleado
        query_emp = """
            UPDATE empleados
            SET codigo = %s, nombre = %s, apellido_paterno = %s, apellido_materno = %s,
                id_sucursal = %s, id_departamento = %s, id_puesto = %s, id_estatus_empleado = %s
            WHERE TRIM(LEADING '0' FROM CAST(codigo AS CHAR)) = TRIM(LEADING '0' FROM CAST(%s AS CHAR))
        """
        cursor.execute(query_emp, (
            c_nuevo, 
            str(nombre).strip(), 
            str(ap_pat).strip(), 
            str(ap_mat).strip() if ap_mat else None,
            int(id_suc), 
            int(id_dep), 
            int(id_pue), 
            int(id_estatus), 
            c_viejo
        ))

        # 3. Propagar en cascada a tablas dependientes si el código cambió
        if c_viejo.lstrip('0') != c_nuevo.lstrip('0'):
            tablas_cascada = [
                ("correos_electronicos", "codigo_empleado"),
                ("lineas_telefonicas", "codigo_empleado"),
                ("inventario_celulares", "codigo_empleado"),
                ("inventario_laptops", "codigo_empleado"),
                ("inventario_cpu", "codigo_empleado"),
                ("inventario_monitores", "codigo_empleado"),
                ("inventario_tablets", "codigo_empleado"),
                ("responsivas_celulares", "codigo_empleado"),
                ("responsivas_laptops", "codigo_empleado"),
                ("responsivas_cpu", "codigo_empleado"),
                ("responsivas_monitores", "codigo_empleado"),
                ("responsivas_tablets", "codigo_empleado"),
            ]

            for tabla, col in tablas_cascada:
                try:
                    cursor.execute(f"SHOW TABLES LIKE '{tabla}'")
                    if cursor.fetchone():
                        cols_t = obtener_columnas_tabla(cursor, tabla)
                        if col in cols_t:
                            q_cascade = f"""
                                UPDATE {tabla}
                                SET {col} = %s
                                WHERE TRIM(LEADING '0' FROM CAST({col} AS CHAR)) = TRIM(LEADING '0' FROM CAST(%s AS CHAR))
                            """
                            cursor.execute(q_cascade, (c_nuevo, c_viejo))
                except Exception:
                    pass

        # 4. Reactivar Foreign Keys y guardar cambios
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        except Exception:
            pass
        st.error(f"⚠️ Error al actualizar colaborador en cascada: {e}")
        return False
    finally:
        conn.close()

# ==============================================================================
# RENDER PRINCIPAL
# ==============================================================================
def render():
    aplicar_estilos_pantalla()
    st.title("📧 Administración de Correos y Empleados")

    if "mensaje_exito_correo" in st.session_state:
        st.success(st.session_state["mensaje_exito_correo"])
        del st.session_state["mensaje_exito_correo"]

    dict_tipo_correo = obtener_catalogo_tipos_correo()
    dict_tipo_correo_rev = {int(v): str(k) for k, v in dict_tipo_correo.items()}

    dict_est_correos = obtener_catalogo_estatus_correos()
    dict_est_correos_rev = {int(v): str(k) for k, v in dict_est_correos.items()}

    dict_est_emp = obtener_catalogo_dict("estatus_empleados", "id_estatus_empleado", "estatus_empleado")
    if not dict_est_emp:
        dict_est_emp = {"ACTIVO": 1, "INACTIVO": 2, "BAJA": 3}
    dict_est_emp_rev = {int(v): str(k) for k, v in dict_est_emp.items()}

    tab_correos, tab_empleados = st.tabs(["📧 Gestión de Correos Electrónicos", "👤 Registro y Modificación de Empleados"])

    # --------------------------------------------------------------------------
    # TAB 1: CORREOS ELECTRÓNICOS
    # --------------------------------------------------------------------------
    with tab_correos:
        st.subheader("✉️ Registro y Edición de Cuentas de Correo")

        df_emp = obtener_empleados_completos_df(dict_est_emp_rev)
        df_correos = obtener_correos_df(dict_tipo_correo_rev, dict_est_correos_rev)

        if df_emp.empty:
            st.warning("⚠️ No hay empleados registrados para asociar correos. Da de alta uno en la pestaña de Empleados.")
            return

        c_accion, _ = st.columns([1, 2])
        modo_correo = c_accion.radio("Acción de Correo:", ["➕ Crear Nuevo Correo", "✏️ Editar Existente"], horizontal=True)

        if modo_correo == "➕ Crear Nuevo Correo":
            with st.form("form_correo_nuevo"):
                c1, c2 = st.columns(2)
                with c1:
                    lista_emp_opts = [f"{r['codigo_str']} - {r['nombre_completo']}" for _, r in df_emp.iterrows()]
                    emp_sel = st.selectbox("Colaborador:", lista_emp_opts)
                    cod_emp_final = emp_sel.split(" - ")[0]

                    direccion_in = st.text_input("Dirección de Correo Electrónico:", placeholder="ejemplo@agrocisa.com o usuario@gmail.com")
                    pass_in = st.text_input("Contraseña del Correo:", type="password", placeholder="Ingresa la contraseña del correo")

                with c2:
                    tipo_nom = st.selectbox("Tipo de Correo:", list(dict_tipo_correo.keys()))
                    estatus_nom = st.selectbox("Estatus de la Cuenta:", list(dict_est_correos.keys()))

                btn_guardar_correo = st.form_submit_button("💾 Guardar Nueva Cuenta de Correo", type="primary")

                if btn_guardar_correo:
                    if not direccion_in.strip() or "@" not in direccion_in:
                        st.warning("⚠️ Ingresa una dirección de correo válida.")
                    elif existe_correo_duplicado(direccion_in):
                        st.error(f"⛔ El correo `{direccion_in.strip().lower()}` ya está registrado en la base de datos.")
                    else:
                        if guardar_correo_bdd(
                            id_correo=None,
                            codigo_emp=cod_emp_final,
                            direccion=direccion_in,
                            pass_val=pass_in.strip(),
                            id_tipo=int(dict_tipo_correo[tipo_nom]),
                            id_estatus=int(dict_est_correos[estatus_nom])
                        ):
                            st.session_state["mensaje_exito_correo"] = f"🎉 ¡Cuenta `{direccion_in.strip().lower()}` registrada exitosamente!"
                            st.rerun()

        else:
            if df_correos.empty:
                st.info("No hay correos registrados aún para editar.")
            else:
                lista_c = [f"ID {r['id_correo']} | {r['direccion_correo']} ({r['tipo_correo']}) [{r['estatus_correo']}]" for _, r in df_correos.iterrows()]
                sel_c = st.selectbox(
                    "Selecciona o teclea la cuenta a modificar:",
                    lista_c,
                    index=None,
                    placeholder="🔍 Teclea aquí para autocompletar la cuenta de correo...",
                    key="sel_correo_edit_auto"
                )

                if sel_c:
                    id_correo_edit = int(sel_c.split(" | ")[0].replace("ID ", ""))
                    row_c = df_correos[df_correos["id_correo"] == id_correo_edit].iloc[0]

                    emp_codigo_def = str(row_c["codigo_empleado"]).strip().zfill(5) if pd.notna(row_c["codigo_empleado"]) else df_emp["codigo_str"].iloc[0]
                    dir_correo_def = str(row_c["direccion_correo"]) if pd.notna(row_c["direccion_correo"]) else ""
                    pass_correo_def = str(row_c["contrasena"]) if pd.notna(row_c["contrasena"]) else ""
                    tipo_id_def = int(row_c["id_tipo_correo"]) if pd.notna(row_c["id_tipo_correo"]) else list(dict_tipo_correo.values())[0]
                    estatus_id_def = int(row_c["id_estatus_correo"]) if pd.notna(row_c["id_estatus_correo"]) else list(dict_est_correos.values())[0]

                    st.divider()

                    with st.form(f"form_correo_edit_{id_correo_edit}"):
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

                            direccion_in = st.text_input("Dirección de Correo Electrónico:", value=dir_correo_def)
                            pass_in = st.text_input("Contraseña del Correo:", value=pass_correo_def, type="password")

                        with c2:
                            idx_tipo_def = list(dict_tipo_correo.values()).index(tipo_id_def) if tipo_id_def in dict_tipo_correo.values() else 0
                            tipo_nom = st.selectbox("Tipo de Correo:", list(dict_tipo_correo.keys()), index=idx_tipo_def)

                            idx_est_def = list(dict_est_correos.values()).index(estatus_id_def) if estatus_id_def in dict_est_correos.values() else 0
                            estatus_nom = st.selectbox("Estatus de la Cuenta:", list(dict_est_correos.keys()), index=idx_est_def)

                        btn_actualizar_correo = st.form_submit_button("💾 Actualizar Cuenta de Correo", type="primary")

                        if btn_actualizar_correo:
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
                                    id_tipo=int(dict_tipo_correo[tipo_nom]),
                                    id_estatus=int(dict_est_correos[estatus_nom])
                                ):
                                    st.session_state["mensaje_exito_correo"] = f"🎉 ¡Cuenta `{direccion_in.strip().lower()}` actualizada exitosamente a estatus: **{estatus_nom}**!"
                                    st.rerun()
                else:
                    st.info("👆 Selecciona o escribe una cuenta en el buscador de arriba para cargar sus datos.")

        st.divider()
        st.markdown("### 📋 Directorio de Correos Registrados")
        
        if not df_correos.empty:
            f1, f2 = st.columns(2)
            with f1:
                txt_busqueda = st.text_input("🔍 Buscar correo o colaborador:", placeholder="Ej. Juan, 00595, agrocisa.com")
            with f2:
                estatus_opts = ["Todos"] + list(dict_est_correos.keys())
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
    # TAB 2: ALTA Y MODIFICACIÓN DE EMPLEADOS
    # --------------------------------------------------------------------------
    with tab_empleados:
        st.subheader("👤 Gestión de Colaboradores")

        df_emp_comp = obtener_empleados_completos_df(dict_est_emp_rev)
        dict_suc = obtener_catalogo_dict("sucursales", "id_sucursal", "nombre_sucursal")
        dict_dep = obtener_catalogo_dict("departamentos", "id_departamento", "nombre_departamento")
        dict_pue = obtener_catalogo_dict("puestos", "id_puesto", "nombre_puesto")

        c_accion_e, _ = st.columns([1, 2])
        modo_emp = c_accion_e.radio("Acción de Empleado:", ["➕ Registrar Nuevo Empleado", "✏️ Modificar Existente"], horizontal=True)

        if modo_emp == "➕ Registrar Nuevo Empleado":
            with st.form("form_empleado_nuevo"):
                c1, c2, c3 = st.columns(3)
                with c1:
                    cod_in = st.text_input("Código de Empleado (ID)*:", placeholder="Ej. 00849 o 849")
                    nom_in = st.text_input("Nombre(s)*:", placeholder="Ej. Juan Carlos")

                with c2:
                    pat_in = st.text_input("Apellido Paterno*:", placeholder="Ej. Pérez")
                    mat_in = st.text_input("Apellido Materno:", placeholder="Ej. López (Opcional)")

                with c3:
                    suc_nom = st.selectbox("Sucursal:", list(dict_suc.keys()))
                    dep_nom = st.selectbox("Departamento:", list(dict_dep.keys()))
                    pue_nom = st.selectbox("Puesto:", list(dict_pue.keys()))
                    est_e_nom = st.selectbox("Estatus del Empleado:", list(dict_est_emp.keys()))

                btn_guardar_emp = st.form_submit_button("💾 Guardar Nuevo Colaborador", type="primary")

                if btn_guardar_emp:
                    if not cod_in.strip():
                        st.warning("⚠️ El Código de Empleado es obligatorio.")
                    elif not nom_in.strip() or not pat_in.strip():
                        st.warning("⚠️ El Nombre y Apellido Paterno son obligatorios.")
                    elif existe_codigo_empleado(cod_in):
                        st.error(f"⛔ El código de empleado `{cod_in.strip()}` ya existe en la base de datos.")
                    else:
                        if guardar_nuevo_empleado_bdd(
                            codigo=cod_in,
                            nombre=nom_in,
                            ap_pat=pat_in,
                            ap_mat=mat_in,
                            id_suc=int(dict_suc[suc_nom]),
                            id_dep=int(dict_dep[dep_nom]),
                            id_pue=int(dict_pue[pue_nom]),
                            id_estatus=int(dict_est_emp[est_e_nom])
                        ):
                            st.session_state["mensaje_exito_correo"] = f"🎉 ¡Colaborador `{nom_in.strip()} {pat_in.strip()}` (Código: {cod_in.strip()}) dado de alta con éxito!"
                            st.rerun()

        else:
            if df_emp_comp.empty:
                st.info("No hay colaboradores registrados para modificar.")
            else:
                lista_e_opts = [f"{r['codigo_str']} - {r['nombre_completo']} ({r['sucursal']})" for _, r in df_emp_comp.iterrows()]
                emp_edit_sel = st.selectbox(
                    "Selecciona o teclea el colaborador a modificar:",
                    lista_e_opts,
                    index=None,
                    placeholder="🔍 Teclea aquí para buscar colaborador por nombre o código...",
                    key="sel_emp_edit_auto"
                )

                if emp_edit_sel:
                    cod_edit = emp_edit_sel.split(" - ")[0]
                    row_e = df_emp_comp[df_emp_comp["codigo_str"] == cod_edit].iloc[0]

                    cod_def = row_e["codigo_str"]
                    nom_def = row_e["nombre"]
                    pat_def = row_e["apellido_paterno"]
                    mat_def = row_e["apellido_materno"] or ""
                    suc_id_def = int(row_e["id_sucursal"]) if pd.notna(row_e["id_sucursal"]) else 1
                    dep_id_def = int(row_e["id_departamento"]) if pd.notna(row_e["id_departamento"]) else 1
                    pue_id_def = int(row_e["id_puesto"]) if pd.notna(row_e["id_puesto"]) else 1
                    est_id_def = int(row_e["id_estatus_empleado"]) if pd.notna(row_e["id_estatus_empleado"]) else 1

                    st.divider()

                    with st.form(f"form_empleado_edit_{cod_def}"):
                        st.caption("ℹ️ *Si corriges el Código de Empleado, se actualizará en automático en todos sus dispositivos, correos y responsivas asignadas.*")
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            cod_in = st.text_input("Código de Empleado (ID):", value=cod_def)
                            nom_in = st.text_input("Nombre(s)*:", value=nom_def)

                        with c2:
                            pat_in = st.text_input("Apellido Paterno*:", value=pat_def)
                            mat_in = st.text_input("Apellido Materno:", value=mat_def)

                        with c3:
                            idx_suc = list(dict_suc.values()).index(suc_id_def) if suc_id_def in dict_suc.values() else 0
                            suc_nom = st.selectbox("Sucursal:", list(dict_suc.keys()), index=idx_suc)

                            idx_dep = list(dict_dep.values()).index(dep_id_def) if dep_id_def in dict_dep.values() else 0
                            dep_nom = st.selectbox("Departamento:", list(dict_dep.keys()), index=idx_dep)

                            idx_pue = list(dict_pue.values()).index(pue_id_def) if pue_id_def in dict_pue.values() else 0
                            pue_nom = st.selectbox("Puesto:", list(dict_pue.keys()), index=idx_pue)

                            idx_est_e = list(dict_est_emp.values()).index(est_id_def) if est_id_def in dict_est_emp.values() else 0
                            est_e_nom = st.selectbox("Estatus del Empleado:", list(dict_est_emp.keys()), index=idx_est_e)

                        btn_actualizar_emp = st.form_submit_button("💾 Actualizar Datos del Empleado y Propagar Cascada", type="primary")

                        if btn_actualizar_emp:
                            if not cod_in.strip():
                                st.warning("⚠️ El Código de Empleado no puede quedar vacío.")
                            elif not nom_in.strip() or not pat_in.strip():
                                st.warning("⚠️ El Nombre y Apellido Paterno son obligatorios.")
                            elif cod_in.strip().zfill(5) != cod_def and existe_codigo_empleado(cod_in):
                                st.error(f"⛔ El nuevo código `{cod_in.strip()}` ya pertenece a otro colaborador.")
                            else:
                                if actualizar_empleado_en_cascada_bdd(
                                    codigo_viejo=cod_def,
                                    codigo_nuevo=cod_in,
                                    nombre=nom_in,
                                    ap_pat=pat_in,
                                    ap_mat=mat_in,
                                    id_suc=int(dict_suc[suc_nom]),
                                    id_dep=int(dict_dep[dep_nom]),
                                    id_pue=int(dict_pue[pue_nom]),
                                    id_estatus=int(dict_est_emp[est_e_nom])
                                ):
                                    st.session_state["mensaje_exito_correo"] = f"🎉 ¡Datos de `{nom_in.strip()} {pat_in.strip()}` actualizados con éxito! (Código: `{cod_in.strip().zfill(5)}` propagado en cascada a todos sus equipos y correos)."
                                    st.rerun()
                else:
                    st.info("👆 Selecciona o escribe un colaborador en el buscador de arriba para cargar sus datos.")

        st.divider()
        st.markdown("### 📋 Directorio General de Empleados")
        
        if not df_emp_comp.empty:
            f1, f2 = st.columns(2)
            with f1:
                txt_busq_emp = st.text_input("🔍 Buscar por Nombre, Código o Sucursal:", placeholder="Ej. Morelia, 00848, Abdiel")
            with f2:
                opts_est_emp = ["Todos"] + list(dict_est_emp.keys())
                sel_est_emp = st.selectbox("Filtrar por Estatus de Empleado:", opts_est_emp)

            df_filt_emp = df_emp_comp.copy()
            if sel_est_emp != "Todos":
                df_filt_emp = df_filt_emp[df_filt_emp["estatus_empleado"] == sel_est_emp]

            if txt_busq_emp.strip():
                term_e = txt_busq_emp.strip().lower()
                df_filt_emp = df_filt_emp[
                    df_filt_emp["nombre_completo"].astype(str).str.lower().str.contains(term_e) |
                    df_filt_emp["codigo_str"].astype(str).str.lower().str.contains(term_e) |
                    df_filt_emp["sucursal"].astype(str).str.lower().str.contains(term_e) |
                    df_filt_emp["departamento"].astype(str).str.lower().str.contains(term_e) |
                    df_filt_emp["puesto"].astype(str).str.lower().str.contains(term_e)
                ]

            st.dataframe(
                df_filt_emp[["codigo_str", "nombre_completo", "sucursal", "departamento", "puesto", "estatus_empleado"]],
                use_container_width=True,
                hide_index=True
            )
            st.caption(f"Mostrando **{len(df_filt_emp)}** de **{len(df_emp_comp)}** colaboradores.")

render_correos = render