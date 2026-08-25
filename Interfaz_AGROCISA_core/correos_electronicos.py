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

def generar_excel_bytes(df_exportar, nombre_hoja="Empleados"):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_exportar.to_excel(writer, index=False, sheet_name=nombre_hoja)
    buffer.seek(0)
    return buffer

def obtener_catalogo_dict(tabla, col_id, col_nombre):
    """Consulta catálogos directos sin diccionarios inventados."""
    try:
        conn = obtener_conexion()
        if not conn:
            return {}
        query = f"SELECT {col_id}, {col_nombre} FROM {tabla} ORDER BY {col_id} ASC"
        df = pd.read_sql(query, conn)
        conn.close()
        return {str(nom): int(cid) for nom, cid in zip(df[col_nombre], df[col_id])}
    except Exception as e:
        st.error(f"⚠️ Error al cargar catálogo '{tabla}': {e}")
        return {}

def verificar_correo_duplicado_info(direccion, id_correo_actual=None):
    """Retorna si existe un duplicado y los datos del registro en conflicto."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        dir_clean = direccion.strip().lower()
        if id_correo_actual is not None:
            cursor.execute("""
                SELECT ce.id_correo, ce.codigo_empleado, CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS empleado
                FROM correos_electronicos ce
                LEFT JOIN empleados e ON TRIM(LEADING '0' FROM CAST(ce.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR))
                WHERE LOWER(ce.direccion_correo) = %s AND ce.id_correo != %s
            """, (dir_clean, int(id_correo_actual)))
        else:
            cursor.execute("""
                SELECT ce.id_correo, ce.codigo_empleado, CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS empleado
                FROM correos_electronicos ce
                LEFT JOIN empleados e ON TRIM(LEADING '0' FROM CAST(ce.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR))
                WHERE LOWER(ce.direccion_correo) = %s
            """, (dir_clean,))
        
        row = cursor.fetchone()
        conn.close()
        if row:
            if isinstance(row, dict):
                return True, row.get('id_correo'), row.get('codigo_empleado'), row.get('empleado')
            return True, row[0], row[1], row[2]
        return False, None, None, None
    except Exception:
        return False, None, None, None

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
def obtener_correos_df():
    try:
        conn = obtener_conexion()
        query = """
            SELECT 
                ce.id_correo,
                ce.codigo_empleado,
                CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS empleado,
                ce.direccion_correo,
                COALESCE(ce.password, '') AS contrasena,
                COALESCE(ce.alias, '') AS alias,
                COALESCE(ce.comentarios, '') AS comentarios,
                ce.id_tipo_correo,
                tce.tipo_correo,
                ce.id_estatus_correo,
                ece.estatus_correo
            FROM correos_electronicos ce
            LEFT JOIN tipos_correos_electronicos tce ON ce.id_tipo_correo = tce.id_tipo_correo
            LEFT JOIN estatus_correos_electronicos ece ON ce.id_estatus_correo = ece.id_estatus_correo
            LEFT JOIN empleados e ON TRIM(LEADING '0' FROM CAST(ce.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR))
            ORDER BY e.nombre ASC, ce.id_correo DESC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error al consultar correos: {e}")
        return pd.DataFrame()

def guardar_correo_bdd(id_correo, codigo_emp, direccion, pass_val, id_tipo, id_estatus, alias_val="", comentarios_val=""):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        codigo_emp_str = str(codigo_emp).strip()
        direccion_clean = str(direccion).strip().lower()
        pass_clean = str(pass_val).strip() if pass_val else None
        alias_clean = str(alias_val).strip() if alias_val else None
        com_clean = str(comentarios_val).strip() if comentarios_val else None
        id_tipo_val = int(id_tipo)
        id_estatus_val = int(id_estatus)

        if id_correo is not None:
            query = """
                UPDATE correos_electronicos 
                SET codigo_empleado = %s, direccion_correo = %s, password = %s, alias = %s, comentarios = %s, id_tipo_correo = %s, id_estatus_correo = %s 
                WHERE id_correo = %s
            """
            cursor.execute(query, (codigo_emp_str, direccion_clean, pass_clean, alias_clean, com_clean, id_tipo_val, id_estatus_val, int(id_correo)))
        else:
            query = """
                INSERT INTO correos_electronicos (codigo_empleado, direccion_correo, password, alias, comentarios, id_tipo_correo, id_estatus_correo) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (codigo_emp_str, direccion_clean, pass_clean, alias_clean, com_clean, id_tipo_val, id_estatus_val))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error en la base de datos al guardar correo: {e}")
        return False

# ==============================================================================
# OPERACIONES: EMPLEADOS Y ACTUALIZACIÓN EN CASCADA
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
                e.id_tipo_contrato, tce.tipo_contrato,
                e.id_estatus_empleado, ee.estatus_empleado
            FROM empleados e
            LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
            LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento
            LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
            LEFT JOIN tipo_contrato_empleados tce ON e.id_tipo_contrato = tce.id_tipo_contrato
            LEFT JOIN estatus_empleados ee ON e.id_estatus_empleado = ee.id_estatus_empleado
            ORDER BY nombre_completo ASC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        
        if not df.empty:
            df["codigo_str"] = df["codigo"].astype(str).str.strip().str.zfill(5)
        return df
    except Exception as e:
        st.error(f"⚠️ Error al cargar empleados: {e}")
        return pd.DataFrame()

def guardar_nuevo_empleado_bdd(codigo, nombre, ap_pat, ap_mat, id_suc, id_dep, id_pue, id_contrato, id_estatus):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        codigo_clean = str(codigo).strip().zfill(5)

        query = """
            INSERT INTO empleados (codigo, nombre, apellido_paterno, apellido_materno, id_sucursal, id_departamento, id_puesto, id_tipo_contrato, id_estatus_empleado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            codigo_clean, 
            str(nombre).strip().title(), 
            str(ap_pat).strip().title(), 
            str(ap_mat).strip().title() if ap_mat and str(ap_mat).strip() else None,
            int(id_suc), 
            int(id_dep), 
            int(id_pue),
            int(id_contrato),
            int(id_estatus)
        ))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error en la base de datos al guardar empleado: {e}")
        return False

def actualizar_empleado_en_cascada_bdd(codigo_viejo, codigo_nuevo, nombre, ap_pat, ap_mat, id_suc, id_dep, id_pue, id_contrato, id_estatus):
    conn = obtener_conexion()
    if not conn:
        return False
        
    cursor = conn.cursor()
    c_viejo = str(codigo_viejo).strip()
    c_nuevo = str(codigo_nuevo).strip().zfill(5)
    id_estatus_int = int(id_estatus)

    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        query_emp = """
            UPDATE empleados
            SET codigo = %s, nombre = %s, apellido_paterno = %s, apellido_materno = %s,
                id_sucursal = %s, id_departamento = %s, id_puesto = %s, id_tipo_contrato = %s, id_estatus_empleado = %s
            WHERE TRIM(LEADING '0' FROM CAST(codigo AS CHAR)) = TRIM(LEADING '0' FROM CAST(%s AS CHAR))
        """
        cursor.execute(query_emp, (
            c_nuevo, 
            str(nombre).strip().title(), 
            str(ap_pat).strip().title(), 
            str(ap_mat).strip().title() if ap_mat and str(ap_mat).strip() else None,
            int(id_suc), 
            int(id_dep), 
            int(id_pue),
            int(id_contrato),
            id_estatus_int, 
            c_viejo
        ))

        # Liberación automática de líneas y responsivas si el empleado pasa a INACTIVO/BAJA
        if id_estatus_int != 1:
            cursor.execute("""
                UPDATE lineas_telefonicas 
                SET codigo_empleado = NULL, id_estatus_linea = 4 
                WHERE TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(%s AS CHAR))
            """, (c_nuevo,))

            cursor.execute("""
                UPDATE responsivas_celulares 
                SET id_status = 2 
                WHERE TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(%s AS CHAR))
            """, (c_nuevo,))

        # Propagación en cascada si cambia el código
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
                q_cascade = f"""
                    UPDATE {tabla}
                    SET {col} = %s
                    WHERE TRIM(LEADING '0' FROM CAST({col} AS CHAR)) = TRIM(LEADING '0' FROM CAST(%s AS CHAR))
                """
                cursor.execute(q_cascade, (c_nuevo, c_viejo))

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

    dict_tipo_correo = obtener_catalogo_dict("tipos_correos_electronicos", "id_tipo_correo", "tipo_correo")
    dict_est_correos = obtener_catalogo_dict("estatus_correos_electronicos", "id_estatus_correo", "estatus_correo")
    dict_est_emp = obtener_catalogo_dict("estatus_empleados", "id_estatus_empleado", "estatus_empleado")
    dict_contratos = obtener_catalogo_dict("tipo_contrato_empleados", "id_tipo_contrato", "tipo_contrato")

    tab_correos, tab_empleados = st.tabs(["📧 Gestión de Correos Electrónicos", "👤 Registro y Modificación de Empleados"])

    # --------------------------------------------------------------------------
    # TAB 1: CORREOS ELECTRÓNICOS
    # --------------------------------------------------------------------------
    with tab_correos:
        st.subheader("✉️ Registro y Edición de Cuentas de Correo")

        df_emp = obtener_empleados_completos_df()
        df_correos = obtener_correos_df()

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

                    direccion_in = st.text_input("Dirección de Correo Electrónico*:", placeholder="ejemplo@agrocisa.com o usuario@gmail.com")
                    alias_in = st.text_input("Alias del Correo (Opcional):", placeholder="Ej. ventas, compras, aux.contable")

                with c2:
                    tipo_nom = st.selectbox("Tipo de Correo:", list(dict_tipo_correo.keys()))
                    estatus_nom = st.selectbox("Estatus de la Cuenta:", list(dict_est_correos.keys()))
                    pass_in = st.text_input("Contraseña del Correo:", type="password", placeholder="Ingresa la contraseña del correo")

                comentarios_in = st.text_input("Comentarios / Observaciones adicionales:", placeholder="Ej. Correo compartido, redireccionado a gerencia...")

                btn_guardar_correo = st.form_submit_button("💾 Guardar Nueva Cuenta de Correo", type="primary")

                if btn_guardar_correo:
                    dir_limpia = direccion_in.strip().lower()
                    if not dir_limpia or "@" not in dir_limpia:
                        st.warning("⚠️ Ingresa una dirección de correo válida.")
                    else:
                        hay_dup, dup_id, dup_cod, dup_nom = verificar_correo_duplicado_info(dir_limpia)
                        if hay_dup:
                            colab_txt = f" a {dup_nom} (Cód: {dup_cod})" if dup_nom else ""
                            st.error(f"⛔ El correo `{dir_limpia}` ya está registrado bajo el ID {dup_id}{colab_txt}.")
                        else:
                            if guardar_correo_bdd(
                                id_correo=None,
                                codigo_emp=cod_emp_final,
                                direccion=dir_limpia,
                                pass_val=pass_in.strip(),
                                id_tipo=int(dict_tipo_correo[tipo_nom]),
                                id_estatus=int(dict_est_correos[estatus_nom]),
                                alias_val=alias_in.strip(),
                                comentarios_val=comentarios_in.strip()
                            ):
                                st.session_state["mensaje_exito_correo"] = f"🎉 ¡Cuenta `{dir_limpia}` registrada exitosamente!"
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
                    alias_def = str(row_c["alias"]) if pd.notna(row_c["alias"]) else ""
                    comentarios_def = str(row_c["comentarios"]) if pd.notna(row_c["comentarios"]) else ""
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

                            direccion_in = st.text_input("Dirección de Correo Electrónico*:", value=dir_correo_def)
                            alias_in = st.text_input("Alias del Correo:", value=alias_def, placeholder="Ej. ventas, compras, aux.contable")

                        with c2:
                            idx_tipo_def = list(dict_tipo_correo.values()).index(tipo_id_def) if tipo_id_def in dict_tipo_correo.values() else 0
                            tipo_nom = st.selectbox("Tipo de Correo:", list(dict_tipo_correo.keys()), index=idx_tipo_def)

                            idx_est_def = list(dict_est_correos.values()).index(estatus_id_def) if estatus_id_def in dict_est_correos.values() else 0
                            estatus_nom = st.selectbox("Estatus de la Cuenta:", list(dict_est_correos.keys()), index=idx_est_def)

                            pass_in = st.text_input("Contraseña del Correo:", value=pass_correo_def, type="password")

                        comentarios_in = st.text_input("Comentarios / Observaciones adicionales:", value=comentarios_def, placeholder="Ej. Correo compartido, redireccionado...")

                        btn_actualizar_correo = st.form_submit_button("💾 Actualizar Cuenta de Correo", type="primary")

                        if btn_actualizar_correo:
                            dir_limpia = direccion_in.strip().lower()
                            if not dir_limpia or "@" not in dir_limpia:
                                st.warning("⚠️ Ingresa una dirección de correo válida.")
                            else:
                                es_duplicado = False
                                if dir_limpia != dir_correo_def.strip().lower():
                                    hay_dup, dup_id, dup_cod, dup_nom = verificar_correo_duplicado_info(dir_limpia, id_correo_edit)
                                    if hay_dup:
                                        es_duplicado = True
                                        colab_txt = f" a {dup_nom} (Cód: {dup_cod})" if dup_nom else ""
                                        st.error(f"⛔ El correo `{dir_limpia}` ya está asignado en la cuenta ID {dup_id}{colab_txt}.")

                                if not es_duplicado:
                                    if guardar_correo_bdd(
                                        id_correo=id_correo_edit,
                                        codigo_emp=cod_emp_final,
                                        direccion=dir_limpia,
                                        pass_val=pass_in.strip(),
                                        id_tipo=int(dict_tipo_correo[tipo_nom]),
                                        id_estatus=int(dict_est_correos[estatus_nom]),
                                        alias_val=alias_in.strip(),
                                        comentarios_val=comentarios_in.strip()
                                    ):
                                        st.session_state["mensaje_exito_correo"] = f"🎉 ¡Cuenta `{dir_limpia}` actualizada exitosamente!"
                                        st.rerun()
                else:
                    st.info("👆 Selecciona o escribe una cuenta en el buscador de arriba para cargar sus datos.")

        st.divider()
        st.markdown("### 📋 Directorio de Correos Registrados")
        
        if not df_correos.empty:
            f1, f2 = st.columns(2)
            with f1:
                txt_busqueda = st.text_input("🔍 Buscar correo, alias o colaborador:", placeholder="Ej. Juan, ventas, 00595, agrocisa.com")
            with f2:
                estatus_opts = ["Todos"] + list(dict_est_correos.keys())
                estatus_sel = st.selectbox("Filtrar por Estatus de Correo:", estatus_opts)

            df_filt = df_correos.copy()

            if txt_busqueda.strip():
                term = txt_busqueda.strip().lower()
                df_filt = df_filt[
                    df_filt["empleado"].astype(str).str.lower().str.contains(term) |
                    df_filt["codigo_empleado"].astype(str).str.lower().str.contains(term) |
                    df_filt["direccion_correo"].astype(str).str.lower().str.contains(term) |
                    df_filt["alias"].astype(str).str.lower().str.contains(term) |
                    df_filt["comentarios"].astype(str).str.lower().str.contains(term)
                ]

            if estatus_sel != "Todos":
                df_filt = df_filt[df_filt["estatus_correo"] == estatus_sel]

            cols_mostrar = ["id_correo", "codigo_empleado", "empleado", "direccion_correo", "alias", "tipo_correo", "estatus_correo", "comentarios"]
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

        df_emp_comp = obtener_empleados_completos_df()
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
                    
                c4, c5 = st.columns(2)
                with c4:
                    contrato_nom = st.selectbox("Tipo de Contrato:", list(dict_contratos.keys()))
                with c5:
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
                        nom_t = nom_in.strip().title()
                        pat_t = pat_in.strip().title()
                        if guardar_nuevo_empleado_bdd(
                            codigo=cod_in,
                            nombre=nom_in,
                            ap_pat=pat_in,
                            ap_mat=mat_in,
                            id_suc=int(dict_suc[suc_nom]),
                            id_dep=int(dict_dep[dep_nom]),
                            id_pue=int(dict_pue[pue_nom]),
                            id_contrato=int(dict_contratos[contrato_nom]),
                            id_estatus=int(dict_est_emp[est_e_nom])
                        ):
                            st.session_state["mensaje_exito_correo"] = f"🎉 ¡Colaborador `{nom_t} {pat_t}` (Código: {cod_in.strip().zfill(5)}) dado de alta con éxito!"
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
                    contrato_id_def = int(row_e["id_tipo_contrato"]) if pd.notna(row_e["id_tipo_contrato"]) else list(dict_contratos.values())[0]
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

                        c4, c5 = st.columns(2)
                        with c4:
                            idx_con = list(dict_contratos.values()).index(contrato_id_def) if contrato_id_def in dict_contratos.values() else 0
                            contrato_nom = st.selectbox("Tipo de Contrato:", list(dict_contratos.keys()), index=idx_con)
                        with c5:
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
                                nom_t = nom_in.strip().title()
                                pat_t = pat_in.strip().title()
                                if actualizar_empleado_en_cascada_bdd(
                                    codigo_viejo=cod_def,
                                    codigo_nuevo=cod_in,
                                    nombre=nom_in,
                                    ap_pat=pat_in,
                                    ap_mat=mat_in,
                                    id_suc=int(dict_suc[suc_nom]),
                                    id_dep=int(dict_dep[dep_nom]),
                                    id_pue=int(dict_pue[pue_nom]),
                                    id_contrato=int(dict_contratos[contrato_nom]),
                                    id_estatus=int(dict_est_emp[est_e_nom])
                                ):
                                    st.session_state["mensaje_exito_correo"] = f"🎉 ¡Datos de `{nom_t} {pat_t}` actualizados con éxito! (Código: `{cod_in.strip().zfill(5)}` propagado en cascada)."
                                    st.rerun()
                else:
                    st.info("👆 Selecciona o escribe un colaborador en el buscador de arriba para cargar sus datos.")

        # ----------------------------------------------------------------------
        # DIRECTORIO GENERAL DE EMPLEADOS CON FILTROS AVANZADOS 4x1
        # ----------------------------------------------------------------------
        st.divider()
        st.subheader("📋 Directorio General de Empleados")

        if not df_emp_comp.empty:
            c_busq, f_suc, f_dep, f_pue, f_est = st.columns([1.5, 1, 1, 1, 1])

            with c_busq:
                txt_busq_emp = st.text_input("🔍 Buscar:", placeholder="Ej. Morelia, 00848, Abdiel...", key="filtro_txt_emp")
            with f_suc:
                opts_s = ["Todas"] + sorted(list(df_emp_comp["sucursal"].dropna().unique()))
                sel_s = st.selectbox("Sucursal:", opts_s, key="filtro_suc_emp")
            with f_dep:
                opts_d = ["Todos"] + sorted(list(df_emp_comp["departamento"].dropna().unique()))
                sel_d = st.selectbox("Departamento:", opts_d, key="filtro_dep_emp")
            with f_pue:
                opts_p = ["Todos"] + sorted(list(df_emp_comp["puesto"].dropna().unique()))
                sel_p = st.selectbox("Puesto:", opts_p, key="filtro_pue_emp")
            with f_est:
                opts_e = ["Todos"] + sorted(list(df_emp_comp["estatus_empleado"].dropna().unique()))
                sel_e = st.selectbox("Estatus:", opts_e, key="filtro_est_emp")

            df_filt_emp = df_emp_comp.copy()

            if sel_s != "Todas":
                df_filt_emp = df_filt_emp[df_filt_emp["sucursal"] == sel_s]
            if sel_d != "Todos":
                df_filt_emp = df_filt_emp[df_filt_emp["departamento"] == sel_d]
            if sel_p != "Todos":
                df_filt_emp = df_filt_emp[df_filt_emp["puesto"] == sel_p]
            if sel_e != "Todos":
                df_filt_emp = df_filt_emp[df_filt_emp["estatus_empleado"] == sel_e]

            if txt_busq_emp.strip():
                term_e = txt_busq_emp.strip().lower()
                cols_eval = ["codigo_str", "nombre_completo", "sucursal", "departamento", "puesto", "tipo_contrato", "estatus_empleado"]
                mascara_emp = pd.Series(False, index=df_filt_emp.index)
                for col in cols_eval:
                    mascara_emp |= df_filt_emp[col].astype(str).str.lower().str.contains(term_e, na=False)
                df_filt_emp = df_filt_emp[mascara_emp]

            v_cols_emp = ["codigo_str", "nombre_completo", "sucursal", "departamento", "puesto", "tipo_contrato", "estatus_empleado"]
            st.dataframe(
                df_filt_emp[v_cols_emp].rename(columns={
                    "codigo_str": "Código",
                    "nombre_completo": "Nombre Colaborador",
                    "sucursal": "Sucursal",
                    "departamento": "Departamento",
                    "puesto": "Puesto",
                    "tipo_contrato": "Contrato",
                    "estatus_empleado": "Estatus"
                }),
                use_container_width=True,
                hide_index=True
            )

            col_inf_e, col_btn_e = st.columns([3, 1])
            with col_inf_e:
                st.caption(f"Mostrando **{len(df_filt_emp)}** de **{len(df_emp_comp)}** colaboradores.")
            with col_btn_e:
                st.download_button(
                    label="📊 Exportar Empleados (.xlsx)",
                    data=generar_excel_bytes(df_filt_emp[v_cols_emp], "Directorio_Empleados"),
                    file_name="Directorio_Empleados_AGROCISA.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )
        else:
            st.info("No hay colaboradores registrados en la base de datos.")

render_correos = render