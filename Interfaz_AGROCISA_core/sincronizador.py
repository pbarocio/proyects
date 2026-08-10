import streamlit as st
import mysql.connector
import os
from sshtunnel import SSHTunnelForwarder
from pathlib import Path
import paramiko
from dotenv import load_dotenv
import pandas as pd
from database import obtener_conexion

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = paramiko.PKey.PKey if hasattr(paramiko.PKey, 'PKey') else paramiko.RSAKey

def obtener_catalogo_dict(tabla, col_id, col_nombre):
    """Carga opciones de catálogo para los selectbox."""
    try:
        conn = obtener_conexion()
        query = f"SELECT {col_id}, {col_nombre} FROM {tabla} ORDER BY {col_nombre} ASC"
        df = pd.read_sql(query, conn)
        conn.close()
        return dict(zip(df[col_nombre], df[col_id]))
    except Exception as e:
        st.error(f"⚠️ Error al cargar catálogo {tabla}: {e}")
        return {}

def obtener_empleados_local_df():
    """Trae empleados activos locales junto con su Tipo de Contrato y Sucursal vía JOIN."""
    try:
        conexion = obtener_conexion()
        query = """
            SELECT e.codigo, e.nombre, e.apellido_paterno, e.apellido_materno, 
                   e.id_tipo_contrato, c.tipo_contrato AS tipo_contrato,
                   s.nombre_sucursal
            FROM empleados e
            JOIN tipo_contrato_empleados c ON e.id_tipo_contrato = c.id_tipo_contrato
            LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
            WHERE e.id_estatus_empleado = 1
        """
        df = pd.read_sql(query, conexion)
        conexion.close()
        
        df["codigo"] = df["codigo"].astype(str).str.strip()
        df["nombre"] = df["nombre"].fillna("").astype(str).str.strip().str.title()
        df["apellido_paterno"] = df["apellido_paterno"].fillna("").astype(str).str.strip().str.title()
        df["apellido_materno"] = df["apellido_materno"].fillna("").astype(str).str.strip().str.title()
        df["nombre_sucursal"] = df["nombre_sucursal"].fillna("Sin Sucursal").astype(str).str.strip()
        df["nombre_completo"] = (
            (df["nombre"] + " " + df["apellido_paterno"] + " " + df["apellido_materno"])
            .str.replace(r'\s+', ' ', regex=True)
        )
        return df
    except Exception as e:
        st.error(f"⚠️ Error al consultar MariaDB Local: {e}")
        return None

def obtener_empleados_vps_df():
    """Conecta por túnel SSH a MariaDB en GoDaddy y trae activos."""
    try:
        tunnel = SSHTunnelForwarder(
            (os.getenv("SSH_HOST"), int(os.getenv("SSH_PORT", 22))),
            ssh_username=os.getenv("SSH_USER"),
            ssh_password=os.getenv("SSH_PASS"),
            remote_bind_address=(os.getenv("VPS_HOST", "127.0.0.1"), int(os.getenv("VPS_DB_PORT", 3306))),
            allow_agent=False
        )
        tunnel.start()

        conexion = mysql.connector.connect(
            host="127.0.0.1",
            port=tunnel.local_bind_port,
            user=os.getenv("VPS_DB_USER"),
            password=os.getenv("VPS_DB_PASS"),
            database=os.getenv("VPS_DB")
        )

        query = "SELECT codigo, nombre, apellido_paterno, apellido_materno FROM empleados WHERE estatus = 'ACTIVO'"
        df = pd.read_sql(query, conexion)
        conexion.close()
        tunnel.stop()

        df["codigo"] = df["codigo"].astype(str).str.strip()
        df["nombre"] = df["nombre"].fillna("").astype(str).str.strip().str.title()
        df["apellido_paterno"] = df["apellido_paterno"].fillna("").astype(str).str.strip().str.title()
        df["apellido_materno"] = df["apellido_materno"].fillna("").astype(str).str.strip().str.title()
        df["nombre_completo"] = (
            (df["nombre"] + " " + df["apellido_paterno"] + " " + df["apellido_materno"])
            .str.replace(r'\s+', ' ', regex=True)
        )
        return df
    except Exception as e:
        st.error(f"⚠️ Error de conexión VPS: {e}")
        return None

def procesar_sincronizacion(df_local, df_vps):
    """Compara arreglos en memoria y filtra candidatos."""
    codigos_vps_clean = {c.lstrip('0') for c in df_vps["codigo"]}
    
    df_local["codigo_clean"] = df_local["codigo"].str.lstrip('0')
    candidatos_baja = df_local[~df_local["codigo_clean"].isin(codigos_vps_clean)].copy()
    
    bajas_reales = candidatos_baja[candidatos_baja["id_tipo_contrato"] == 1]
    externos_protegidos = candidatos_baja[candidatos_baja["id_tipo_contrato"] == 2]
    
    codigos_local_clean = {c.lstrip('0') for c in df_local["codigo"]}
    df_vps["codigo_clean"] = df_vps["codigo"].str.lstrip('0')
    altas_nuevas = df_vps[~df_vps["codigo_clean"].isin(codigos_local_clean)].copy()
    
    return bajas_reales, externos_protegidos, altas_nuevas

def obtener_equipos_asignados(codigo_empleado):
    """Consulta las 5 tablas de inventario haciendo MATCH tolerante a ceros iniciales."""
    equipos = []
    conn = obtener_conexion()
    if not conn:
        return equipos

    codigo_sin_ceros = str(codigo_empleado).lstrip('0')

    tablas_inventario = [
        ("inventario_celulares", "imei", "id_estatus_celular", "Celular"),
        ("inventario_laptops", "numero_serie", "id_estatus_laptops", "Laptop"),
        ("inventario_cpu", "hostname", "id_estatus_cpu", "CPU"),
        ("inventario_monitores", "numero_serie", "id_estatus_monitor", "Monitor"),
        ("inventario_tablets", "numero_serie", "id_estatus_tablet", "Tablet"),
    ]

    for tabla, col_id, col_estatus, tipo in tablas_inventario:
        try:
            query = f"""
                SELECT i.{col_id} AS identificador, i.observaciones, i.{col_estatus} AS id_estatus
                FROM {tabla} i
                WHERE TRIM(LEADING '0' FROM CAST(i.codigo_empleado AS CHAR)) = %s
            """
            df = pd.read_sql(query, conn, params=(codigo_sin_ceros,))
            for _, row in df.iterrows():
                equipos.append({
                    "tabla": tabla,
                    "col_id": col_id,
                    "identificador": str(row["identificador"]),
                    "col_estatus": col_estatus,
                    "id_estatus_actual": row["id_estatus"],
                    "observaciones_actuales": row["observaciones"] or "",
                    "tipo": tipo
                })
        except Exception:
            pass
            
    conn.close()
    return equipos

def aplicar_baja_empleado(codigo_empleado, actualizaciones_equipos):
    """Ejecuta la baja completa en MariaDB: inventario, responsivas, correos y estatus del empleado."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        codigo_sin_ceros = str(codigo_empleado).lstrip('0')

        for eq in actualizaciones_equipos:
            query_eq = f"""
                UPDATE {eq['tabla']}
                SET {eq['col_estatus']} = %s,
                    observaciones = %s,
                    codigo_empleado = NULL
                WHERE {eq['col_id']} = %s
            """
            cursor.execute(query_eq, (eq['nuevo_estatus_id'], eq['nuevas_observaciones'], eq['identificador']))

        tablas_responsivas = [
            "responsivas_celulares",
            "responsivas_cpu",
            "responsivas_laptops",
            "responsivas_monitores",
            "responsivas_tablets"
        ]
        for t_resp in tablas_responsivas:
            try:
                query_resp = f"""
                    UPDATE {t_resp} 
                    SET id_status = 2 
                    WHERE TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) = %s
                """
                cursor.execute(query_resp, (codigo_sin_ceros,))
            except Exception:
                pass

        query_correos = """
            UPDATE correos_electronicos 
            SET id_estatus_correo = 2 
            WHERE TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) = %s
        """
        cursor.execute(query_correos, (codigo_sin_ceros,))

        query_emp = "UPDATE empleados SET id_estatus_empleado = 2 WHERE TRIM(LEADING '0' FROM CAST(codigo AS CHAR)) = %s"
        cursor.execute(query_emp, (codigo_sin_ceros,))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al procesar baja en MariaDB: {e}")
        return False

def guardar_empleado_completo(codigo, nombre, p_paterno, p_materno, id_sucursal, id_depto, id_puesto, id_contrato, 
                              user_corp="", pass_corp="", user_gmail="", pass_gmail="", id_estatus=1):
    """Inserta al empleado con sus FKs y construye los correos automáticamente con sus dominios."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        
        query_emp = """
            INSERT INTO empleados 
            (codigo, nombre, apellido_paterno, apellido_materno, id_sucursal, id_departamento, id_puesto, id_tipo_contrato, id_estatus_empleado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                id_sucursal=VALUES(id_sucursal),
                id_departamento=VALUES(id_departamento),
                id_puesto=VALUES(id_puesto),
                id_tipo_contrato=VALUES(id_tipo_contrato),
                id_estatus_empleado=VALUES(id_estatus_empleado);
        """
        cursor.execute(query_emp, (codigo, nombre, p_paterno, p_materno, id_sucursal, id_depto, id_puesto, id_contrato, id_estatus))

        # 1. Correo Corporativo (@agrocisa.com.mx) - id_tipo_correo = 1
        if user_corp.strip():
            # Limpiamos si metieron por error el @
            u_clean = user_corp.strip().split("@")[0]
            correo_corp_full = f"{u_clean}@agrocisa.com.mx"
            
            query_correo_corp = """
                INSERT INTO correos_electronicos (direccion_correo, password, id_tipo_correo, id_estatus_correo, codigo_empleado)
                VALUES (%s, %s, 1, 1, %s)
                ON DUPLICATE KEY UPDATE password=VALUES(password), id_estatus_correo=1, codigo_empleado=VALUES(codigo_empleado);
            """
            cursor.execute(query_correo_corp, (correo_corp_full, pass_corp.strip(), codigo))

        # 2. Correo Gmail (@gmail.com) - id_tipo_correo = 2
        if user_gmail.strip():
            u_g_clean = user_gmail.strip().split("@")[0]
            correo_gmail_full = f"{u_g_clean}@gmail.com"
            
            query_correo_gmail = """
                INSERT INTO correos_electronicos (direccion_correo, password, id_tipo_correo, id_estatus_correo, codigo_empleado)
                VALUES (%s, %s, 2, 1, %s)
                ON DUPLICATE KEY UPDATE password=VALUES(password), id_estatus_correo=1, codigo_empleado=VALUES(codigo_empleado);
            """
            cursor.execute(query_correo_gmail, (correo_gmail_full, pass_gmail.strip(), codigo))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar empleado y correos: {e}")
        return False

def render():
    st.subheader("⚙️ Panel de Control de Sincronización")
    st.write("Cruza de información entre MariaDB VPS (GoDaddy) y BDD Local.")

    if st.button("🔄 Ejecutar Sincronización y Diagnóstico", type="primary"):
        st.session_state["ejecutado_sync"] = True

    if st.session_state.get("ejecutado_sync", False):
        with st.spinner("🔓 Abriendo túnel SSH y analizando bases de datos..."):
            df_local = obtener_empleados_local_df()
            df_vps = obtener_empleados_vps_df()

            if df_local is not None and df_vps is not None:
                bajas, protegidos, altas = procesar_sincronizacion(df_local, df_vps)

                st.divider()

                c1, c2, c3 = st.columns(3)
                c1.metric("🚨 Bajas Reales (Internos)", f"{len(bajas)} empleados")
                c2.metric("🛡️ Externos Protegidos", f"{len(protegidos)} empleados")
                c3.metric("✨ Altas Detectadas", f"{len(altas)} empleados")

                tab1, tab2, tab3 = st.tabs(["🚨 Bajas a Procesar", "🛡️ Externos Omitidos", "✨ Nuevas Altas"])

                # TAB 1: BAJAS
                with tab1:
                    if not bajas.empty:
                        st.error("Los siguientes empleados internos ya no están activos en VPS central. Procesa sus equipos:")
                        
                        lista_bajas = [f"{row['codigo']} - {row['nombre_completo']}" for _, row in bajas.iterrows()]
                        emp_baja_sel = st.selectbox("Selecciona colaborador para procesar salida:", lista_bajas)
                        
                        codigo_baja = emp_baja_sel.split(" - ")[0]
                        row_baja = bajas[bajas["codigo"] == codigo_baja].iloc[0]
                        nombre_baja = row_baja["nombre_completo"]
                        sucursal_baja = row_baja["nombre_sucursal"]

                        equipos_asignados = obtener_equipos_asignados(codigo_baja)

                        st.divider()
                        st.markdown(f"### 📦 Equipos Asignados a `{codigo_baja}` ({sucursal_baja})")

                        if equipos_asignados:
                            dict_estatus_equipos = obtener_catalogo_dict("estatus_celulares", "id_estatus_celular", "estatus_celular")
                            
                            with st.form(key=f"form_baja_{codigo_baja}"):
                                dict_inputs = {}
                                for idx, eq in enumerate(equipos_asignados):
                                    with st.expander(f"📱💻 {eq['tipo']}: `{eq['identificador']}`", expanded=True):
                                        col_a, col_b = st.columns(2)
                                        with col_a:
                                            nuevo_est = st.selectbox(
                                                f"Nuevo estatus para {eq['tipo']}:",
                                                list(dict_estatus_equipos.keys()),
                                                index=2 if "DISPONIBLE" in dict_estatus_equipos else 0,
                                                key=f"est_{codigo_baja}_{idx}"
                                            )
                                        with col_b:
                                            obs_user = st.text_input(
                                                "Observaciones / Destino del equipo:",
                                                value=eq['observaciones_actuales'],
                                                placeholder="Ej. Se queda en sucursal con el Gerente",
                                                key=f"obs_{codigo_baja}_{idx}"
                                            )
                                        
                                        dict_inputs[idx] = {
                                            "eq": eq,
                                            "nuevo_estatus_id": dict_estatus_equipos[nuevo_est],
                                            "obs_user": obs_user
                                        }

                                btn_baja = st.form_submit_button("🛑 Confirmar Baja, Liberar Inventario e Inactivar Responsivas/Correos", type="primary")

                                if btn_baja:
                                    actualizaciones = []
                                    prefix = f"[VACANTE - Ant: {nombre_baja} | Suc: {sucursal_baja}]"
                                    
                                    for idx, data in dict_inputs.items():
                                        eq = data["eq"]
                                        raw_text = data["obs_user"].strip()
                                        
                                        if prefix in raw_text:
                                            obs_final = raw_text
                                        else:
                                            obs_final = f"{prefix} {raw_text}".strip()

                                        actualizaciones.append({
                                            "tabla": eq['tabla'],
                                            "col_id": eq['col_id'],
                                            "identificador": eq['identificador'],
                                            "col_estatus": eq['col_estatus'],
                                            "nuevo_estatus_id": data["nuevo_estatus_id"],
                                            "nuevas_observaciones": obs_final
                                        })

                                    if aplicar_baja_empleado(codigo_baja, actualizaciones):
                                        st.toast(f"✅ Baja procesada y responsivas inactivadas para {emp_baja_sel}", icon="🎉")
                                        st.rerun()
                        else:
                            st.info("Este colaborador no tiene ningún equipo registrado a su nombre.")
                            if st.button("🛑 Marcar Empleado como Inactivo e Inactivar Responsivas/Correos", key=f"btn_inactivo_{codigo_baja}", type="primary"):
                                if aplicar_baja_empleado(codigo_baja, []):
                                    st.toast(f"✅ {emp_baja_sel}, sus correos y responsivas marcados como INACTIVOS.", icon="🎉")
                                    st.rerun()
                    else:
                        st.success("No hay bajas pendientes de procesar.")

                # TAB 2: EXTERNOS
                with tab2:
                    if not protegidos.empty:
                        st.info("Detectados inactivos en VPS pero ignorados automáticamente por ser EXTERNOS.")
                        st.dataframe(protegidos[["codigo", "nombre_completo", "tipo_contrato", "nombre_sucursal"]], use_container_width=True)
                    else:
                        st.write("No hay externos con estatus especial.")

                # TAB 3: ALTAS
                with tab3:
                    if not altas.empty:
                        st.warning(f"Se encontraron **{len(altas)}** empleados nuevos en el VPS. Asigna sus datos para registrarlos:")
                        
                        dict_sucursales = obtener_catalogo_dict("sucursales", "id_sucursal", "nombre_sucursal")
                        dict_deptos = obtener_catalogo_dict("departamentos", "id_departamento", "nombre_departamento")
                        dict_puestos = obtener_catalogo_dict("puestos", "id_puesto", "nombre_puesto")
                        dict_contratos = obtener_catalogo_dict("tipo_contrato_empleados", "id_tipo_contrato", "tipo_contrato")

                        lista_emp = [f"{row['codigo']} - {row['nombre_completo']}" for _, row in altas.iterrows()]
                        emp_sel = st.selectbox("Selecciona un colaborador para dar de alta:", lista_emp)
                        
                        codigo_sel = emp_sel.split(" - ")[0]
                        emp_row = altas[altas["codigo"] == codigo_sel].iloc[0]

                        with st.form(key=f"form_alta_{codigo_sel}"):
                            st.markdown(f"**Registrando a:** `{emp_row['codigo']}` - {emp_row['nombre_completo']}")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                suc_nom = st.selectbox("Sucursal:", list(dict_sucursales.keys()))
                                dep_nom = st.selectbox("Departamento:", list(dict_deptos.keys()))
                            with col_b:
                                pue_nom = st.selectbox("Puesto:", list(dict_puestos.keys()))
                                con_nom = st.selectbox("Tipo de Contrato:", list(dict_contratos.keys()))

                            st.markdown("#### 📧 Cuentas de Correo (Opcional)")
                            col_c, col_d = st.columns(2)
                            with col_c:
                                u_corp = st.text_input("Usuario Corporativo:", placeholder="ej. pablo.barocio")
                                st.caption("Se guardará como: `usuario@agrocisa.com.mx`")
                                p_corp = st.text_input("Password Corporativo:", type="password")
                            with col_d:
                                u_gmail = st.text_input("Usuario Gmail:", placeholder="ej. pablo.agro")
                                st.caption("Se guardará como: `usuario@gmail.com`")
                                p_gmail = st.text_input("Password Gmail:", type="password")

                            btn_guardar = st.form_submit_button("💾 Guardar Empleado y Credenciales", type="primary")

                            if btn_guardar:
                                exito = guardar_empleado_completo(
                                    codigo=emp_row['codigo'],
                                    nombre=emp_row['nombre'],
                                    p_paterno=emp_row['apellido_paterno'],
                                    p_materno=emp_row['apellido_materno'],
                                    id_sucursal=dict_sucursales[suc_nom],
                                    id_depto=dict_deptos[dep_nom],
                                    id_puesto=dict_puestos[pue_nom],
                                    id_contrato=dict_contratos[con_nom],
                                    user_corp=u_corp,
                                    pass_corp=p_corp,
                                    user_gmail=u_gmail,
                                    pass_gmail=p_gmail
                                )
                                if exito:
                                    st.toast(f"¡{emp_row['nombre_completo']} registrado con éxito!", icon="🎉")
                                    st.rerun()
                    else:
                        st.success("Tu base de datos local está 100% al día con las altas del VPS.")