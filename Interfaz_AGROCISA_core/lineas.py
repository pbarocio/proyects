import io
import streamlit as st
import pandas as pd
import mysql.connector
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

def obtener_lineas_completas_df():
    try:
        conn = obtener_conexion()
        query = """
            SELECT 
                lt.numero,
                lt.plan_2026 AS plan,
                COALESCE(lt.gb_promocion_2026, lt.gb_2026, 0) AS gb,
                lt.is_mpp,
                lt.knox,
                lt.id_estatus_linea,
                el.estatus_linea,
                lt.codigo_empleado,
                COALESCE(CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno), 'SIN ASIGNAR') AS titular,
                lt.comentarios
            FROM lineas_telefonicas lt
            LEFT JOIN estatus_linea_telefonica el ON lt.id_estatus_linea = el.id_estatus_linea
            LEFT JOIN empleados e ON TRIM(LEADING '0' FROM CAST(lt.codigo_empleado AS CHAR)) = TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR))
            ORDER BY lt.numero ASC
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error al consultar líneas telefónicas: {e}")
        return pd.DataFrame()

def generar_excel_bytes(df_exportar):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_exportar.to_excel(writer, index=False, sheet_name='Lineas_Telefonicas')
    buffer.seek(0)
    return buffer

def guardar_nueva_linea_bdd(numero, plan_2026, is_mpp, knox, id_estatus_linea, comentarios):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            INSERT INTO lineas_telefonicas (numero, plan_2026, is_mpp, knox, id_estatus_linea, comentarios)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            numero.strip(), 
            plan_2026.strip() or None, 
            1 if is_mpp else 0, 
            1 if knox else 0, 
            id_estatus_linea, 
            comentarios.strip() or None
        ))
        conn.commit()
        conn.close()
        return True, "OK"
    except mysql.connector.Error as err:
        if err.errno == 1062:
            return False, f"⛔ La línea `{numero}` ya existe en la base de datos."
        return False, f"Error en MariaDB: {err}"
    except Exception as e:
        return False, str(e)

def actualizar_linea_bdd(numero, plan_2026, is_mpp, knox, id_estatus_linea, comentarios):
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        query = """
            UPDATE lineas_telefonicas 
            SET plan_2026 = %s, is_mpp = %s, knox = %s, id_estatus_linea = %s, comentarios = %s
            WHERE numero = %s
        """
        cursor.execute(query, (
            plan_2026.strip() or None, 
            1 if is_mpp else 0, 
            1 if knox else 0, 
            id_estatus_linea, 
            comentarios.strip() or None, 
            numero
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al actualizar la línea {numero}: {e}")
        return False

def render():
    aplicar_estilos_pantalla()
    st.title("📞 Gestión y Edición de Líneas Telefónicas")

    df_lineas = obtener_lineas_completas_df()
    dict_estatus = obtener_catalogo_dict("estatus_linea_telefonica", "id_estatus_linea", "estatus_linea")

    tab1, tab2, tab3 = st.tabs([
        "📋 Catálogo General de Líneas", 
        "➕ Registrar Nueva Línea", 
        "✏️ Editar Línea / Cambiar Estatus VIP"
    ])

    # --------------------------------------------------------------------------
    # TAB 1: CONSULTA GENERAL CON FILTROS Y EXPORTACIÓN A EXCEL
    # --------------------------------------------------------------------------
    with tab1:
        if not df_lineas.empty:
            df_mostrar = df_lineas.copy()
            df_mostrar["MPP"] = df_mostrar["is_mpp"].apply(lambda x: "✅" if x == 1 else "")
            df_mostrar["Knox"] = df_mostrar["knox"].apply(lambda x: "🔒 Sí" if x == 1 else "🔓 No")
            
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                busqueda_txt = st.text_input("🔍 Buscar por Empleado / Titular o Número:", placeholder="Ej. Juan, 3931234567, SIN ASIGNAR", key="busq_tab1")
            with c_f2:
                opts_estatus = ["Todos"] + list(dict_estatus.keys())
                estatus_sel_filtro = st.selectbox("Filtrar por Estatus de Línea:", opts_estatus, key="est_tab1")

            if estatus_sel_filtro != "Todos":
                df_mostrar = df_mostrar[df_mostrar["estatus_linea"] == estatus_sel_filtro]

            if busqueda_txt.strip():
                term = busqueda_txt.strip().lower()
                df_mostrar = df_mostrar[
                    df_mostrar["titular"].astype(str).str.lower().str.contains(term) |
                    df_mostrar["numero"].astype(str).str.lower().str.contains(term) |
                    df_mostrar["codigo_empleado"].astype(str).str.lower().str.contains(term)
                ]

            st.dataframe(
                df_mostrar[["numero", "plan", "gb", "MPP", "Knox", "estatus_linea", "titular", "comentarios"]],
                use_container_width=True,
                hide_index=True
            )

            c_info, c_exp = st.columns([3, 1])
            with c_info:
                st.caption(f"Mostrando **{len(df_mostrar)}** de **{len(df_lineas)}** líneas encontradas.")
            with c_exp:
                df_excel = df_mostrar[["numero", "plan", "gb", "MPP", "Knox", "estatus_linea", "titular", "comentarios"]].copy()
                df_excel.columns = ["Número", "Plan 2026", "GB Promo", "MPP", "Samsung Knox", "Estatus", "Titular / Empleado", "Comentarios"]
                
                excel_bytes = generar_excel_bytes(df_excel)
                
                st.download_button(
                    label="📊 Exportar a Excel (.xlsx)",
                    data=excel_bytes,
                    file_name="Reporte_Lineas_Telefonicas_AGROCISA.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True
                )
        else:
            st.info("No hay líneas telefónicas registradas en la base de datos.")

    # --------------------------------------------------------------------------
    # TAB 2: ALTA DE NUEVA LÍNEA
    # --------------------------------------------------------------------------
    with tab2:
        st.subheader("➕ Registrar Nueva Línea Telefónica")
        
        with st.form(key="form_alta_nueva_linea"):
            c1, c2, c3 = st.columns([1.5, 1.5, 1])
            
            with c1:
                num_nuevo = st.text_input("Número Telefónico (10 dígitos)*:", placeholder="Ej. 3931234567")
                plan_nuevo = st.text_input("Plan Telcel (2026):", placeholder="Ej. Plan Telcel Plus 4")

            with c2:
                idx_disp = list(dict_estatus.keys()).index("DISPONIBLE") if "DISPONIBLE" in dict_estatus else 0
                est_nuevo_nom = st.selectbox("Estatus Inicial:", list(dict_estatus.keys()), index=idx_disp)
                st.caption("💡 *Si es para Dirección/Familia, selecciónala como **V.I.P.** aquí mismo.*")

            with c3:
                st.write("**Seguridad & Planes:**")
                mpp_nuevo_chk = st.checkbox("Línea MPP", value=False, key="add_mpp")
                knox_nuevo_chk = st.checkbox("Samsung Knox", value=False, key="add_knox")

            com_nuevo = st.text_area("Comentarios / Observaciones:", placeholder="Ej. Chip nuevo recibido de Telcel / Reserva Dirección")

            btn_crear_linea = st.form_submit_button("💾 Dar de Alta Línea en BDD", type="primary")

            if btn_crear_linea:
                if not num_nuevo.strip():
                    st.warning("⚠️ Debes ingresar un número telefónico válido.")
                else:
                    exito, msg = guardar_nueva_linea_bdd(
                        numero=num_nuevo,
                        plan_2026=plan_nuevo,
                        is_mpp=mpp_nuevo_chk,
                        knox=knox_nuevo_chk,
                        id_estatus_linea=dict_estatus[est_nuevo_nom],
                        comentarios=com_nuevo
                    )
                    if exito:
                        st.toast(f"¡Línea {num_nuevo.strip()} dada de alta con éxito!", icon="🎉")
                        st.rerun()
                    else:
                        st.error(msg)

    # --------------------------------------------------------------------------
    # TAB 3: EDICIÓN DE LÍNEAS CON FILTROS PREVIOS
    # --------------------------------------------------------------------------
    with tab3:
        if not df_lineas.empty:
            st.markdown("### 🔍 Filtrar Línea a Modificar")
            
            fe1, fe2 = st.columns(2)
            with fe1:
                busq_ed_txt = st.text_input("Buscar por Empleado o Número:", placeholder="Ej. Vidal, 393..., V.I.P.", key="busq_tab3")
            with fe2:
                opts_estatus_ed = ["Todos"] + list(dict_estatus.keys())
                estatus_ed_filtro = st.selectbox("Filtrar por Estatus:", opts_estatus_ed, key="est_tab3")

            df_ed_filtrado = df_lineas.copy()

            if estatus_ed_filtro != "Todos":
                df_ed_filtrado = df_ed_filtrado[df_ed_filtrado["estatus_linea"] == estatus_ed_filtro]

            if busq_ed_txt.strip():
                term_ed = busq_ed_txt.strip().lower()
                df_ed_filtrado = df_ed_filtrado[
                    df_ed_filtrado["titular"].astype(str).str.lower().str.contains(term_ed) |
                    df_ed_filtrado["numero"].astype(str).str.lower().str.contains(term_ed) |
                    df_ed_filtrado["codigo_empleado"].astype(str).str.lower().str.contains(term_ed)
                ]

            if df_ed_filtrado.empty:
                st.warning("No se encontraron líneas con los filtros seleccionados.")
            else:
                lista_lineas_opts = [f"{r['numero']} ({r['estatus_linea']}) - {r['titular']}" for _, r in df_ed_filtrado.iterrows()]
                linea_sel_str = st.selectbox("Selecciona la línea a editar:", lista_lineas_opts, key="sel_linea_tab3")
                
                num_sel = linea_sel_str.split(" ")[0]
                row_l = df_ed_filtrado[df_ed_filtrado["numero"] == num_sel].iloc[0]

                st.divider()

                with st.form(key=f"form_ed_linea_{num_sel}"):
                    st.markdown(f"### 📱 Modificando Línea: `{num_sel}`")
                    
                    c1, c2, c3 = st.columns([1.5, 1.5, 1])
                    with c1:
                        plan_in = st.text_input("Plan Telcel (2026):", value=str(row_l['plan'] or ''))

                    with c2:
                        idx_est = list(dict_estatus.values()).index(row_l['id_estatus_linea']) if row_l['id_estatus_linea'] in dict_estatus.values() else 0
                        est_nom = st.selectbox("Estatus de la Línea:", list(dict_estatus.keys()), index=idx_est)

                    with c3:
                        st.write("**Seguridad & Planes:**")
                        mpp_chk = st.checkbox("Línea MPP", value=bool(row_l['is_mpp']))
                        knox_chk = st.checkbox("Samsung Knox", value=bool(row_l['knox']))

                    com_in = st.text_area("Comentarios / Observaciones:", value=str(row_l['comentarios'] or ''), placeholder="Ej. Línea reservada para Dirección / Familia Don Luis")

                    btn_guardar_linea = st.form_submit_button("💾 Guardar Cambios de la Línea", type="primary")

                    if btn_guardar_linea:
                        if actualizar_linea_bdd(
                            numero=num_sel,
                            plan_2026=plan_in,
                            is_mpp=mpp_chk,
                            knox=knox_chk,
                            id_estatus_linea=dict_estatus[est_nom],
                            comentarios=com_in
                        ):
                            st.toast(f"¡Línea {num_sel} actualizada correctamente!", icon="🎉")
                            st.rerun()