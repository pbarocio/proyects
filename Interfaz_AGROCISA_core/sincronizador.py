import streamlit as st
import mysql.connector
import os
from sshtunnel import SSHTunnelForwarder
from pathlib import Path
import paramiko
from dotenv import load_dotenv
import pandas as pd

# Cargar .env de la raíz
env_path = Path(__file__).parent.parent / ".env" if (Path(__file__).parent.parent / ".env").exists() else Path(__file__).parent / ".env"
load_dotenv(env_path)

# Parche para Python 3.14 / Paramiko y SSHTunnel
if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = paramiko.PKey.PKey if hasattr(paramiko.PKey, 'PKey') else paramiko.RSAKey

def obtener_conexion_local():
    """Conexión a MariaDB Local."""
    try:
        conexion = mysql.connector.connect(
            host=str(os.getenv("LOCAL_HOST")),
            user=str(os.getenv("LOCAL_DB_USER")),
            password=str(os.getenv("LOCAL_DB_PASSWORD")),
            database=str(os.getenv("LOCAL_DATABASE")),
        )
        return conexion
    except Exception as e:
        st.error(f"⚠️ Error al conectar a MariaDB Local: {e}")
        return None

def obtener_empleados_vps_df():
    """
    Abre el túnel SSH al VPS, lee los empleados activos de MariaDB
    y regresa el DataFrame de Pandas formateado.
    """
    try:
        tunnel = SSHTunnelForwarder(
            (os.getenv("SSH_HOST"), int(os.getenv("SSH_PORT"))),
            ssh_username=os.getenv("SSH_USER"),
            ssh_password=os.getenv("SSH_PASS"),
            remote_bind_address=(os.getenv("VPS_HOST"), int(os.getenv("VPS_DB_PORT"))),
            allow_agent=False
        )
        tunnel.start()

        conexion = mysql.connector.connect(
            host=os.getenv("VPS_HOST"),
            port=tunnel.local_bind_port,
            user=os.getenv("VPS_DB_USER"),
            password=os.getenv("VPS_DB_PASS"),
            database=os.getenv("VPS_DB")
        )

        query = "SELECT codigo, nombre, apellido_paterno, apellido_materno FROM empleados WHERE estatus = 'ACTIVO'"
        df = pd.read_sql(query, conexion)
        
        conexion.close()
        tunnel.stop()

        # Limpieza y formato de strings con Pandas
        df["nombre"] = df["nombre"].fillna("").astype(str).str.strip().str.title()
        df["apellido_paterno"] = df["apellido_paterno"].fillna("").astype(str).str.strip().str.title()
        df["apellido_materno"] = df["apellido_materno"].fillna("").astype(str).str.strip().str.title()
        
        df["nombre_completo"] = (
            (df["nombre"] + " " + df["apellido_paterno"] + " " + df["apellido_materno"])
            .str.replace(r'\s+', ' ', regex=True)
        )
        
        return df

    except Exception as e:
        st.error(f"⚠️ Error de conexión SSH/MariaDB VPS: {e}")
        return None

def render():
    st.subheader("⚙️ Panel de Control de Sincronización")
    st.write("Conexión en vivo a MariaDB (GoDaddy VPS) a través de túnel SSH.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Consultar Cambios en VPS", type="primary"):
            st.session_state["busqueda_vps"] = True
            
    with col2:
        st.caption("Motor de BDD: **MariaDB + SSH Tunnel**")

    # Si le picaron al botón de consultar
    if st.session_state.get("busqueda_vps", False):
        st.divider()
        
        # Muestra un spinner animado mientras abre el túnel SSH y consulta
        with st.spinner("🔓 Abriendo túnel SSH y consultando MariaDB en el VPS..."):
            df_vps = obtener_empleados_vps_df()
            
        if df_vps is not None and not df_vps.empty:
            st.markdown("### 📋 Empleados Activos en VPS")
            
            # Mostramos la tabla limpia en Streamlit
            st.dataframe(
                df_vps[["codigo", "nombre_completo"]],
                use_container_width=True
            )
            
            st.metric(label="Total Empleados Activos VPS", value=f"{len(df_vps)} registros")
        else:
            st.warning("No se encontraron datos o falló la consulta a MariaDB.")