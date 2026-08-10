import mysql.connector
import os
from sshtunnel import SSHTunnelForwarder
from pathlib import Path
import paramiko
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

# Cargar .env de la raíz
env_path = Path(__file__).parent.parent / ".env" if (Path(__file__).parent.parent / ".env").exists() else Path(__file__).parent / ".env"
load_dotenv(env_path)

# Parche para Python 3.14 / Paramiko y SSHTunnel
if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = paramiko.PKey.PKey if hasattr(paramiko.PKey, 'PKey') else paramiko.RSAKey

# Cache del túnel SSH en memoria para reutilizar la sesión
_tunnel = None

def obtener_conexion():
    """
    Punto ÚNICO de conexión a la Base de Datos.
    Lee la variable ENTORNO_BD ("LOCAL" o "VPS") del .env.
    """
    global _tunnel
    entorno = os.getenv("ENTORNO_BD", "LOCAL").upper()

    try:
        if entorno == "VPS":
            if _tunnel is None or not _tunnel.is_active:
                _tunnel = SSHTunnelForwarder(
                    (os.getenv("SSH_HOST"), int(os.getenv("SSH_PORT", 22))),
                    ssh_username=os.getenv("SSH_USER"),
                    ssh_password=os.getenv("SSH_PASS"),
                    remote_bind_address=(os.getenv("VPS_HOST", "127.0.0.1"), int(os.getenv("VPS_DB_PORT", 3306))),
                    allow_agent=False
                )
                _tunnel.start()

            return mysql.connector.connect(
                host="127.0.0.1",
                port=_tunnel.local_bind_port,
                user=os.getenv("VPS_DB_USER"),
                password=os.getenv("VPS_DB_PASS"),
                database=os.getenv("VPS_DB")
            )
        else:
            # Conexión Local (Windows Server / Dev)
            return mysql.connector.connect(
                host=str(os.getenv("LOCAL_HOST", "localhost")),
                user=str(os.getenv("LOCAL_DB_USER", "root")),
                password=str(os.getenv("LOCAL_DB_PASSWORD", "")),
                database=str(os.getenv("LOCAL_DATABASE", "agrocisa_core")),
            )
    except Exception as e:
        st.error(f"⚠️ Error al conectar a la Base de Datos [{entorno}]: {e}")
        return None

# Alias de compatibilidad para no romper funciones anteriores
obtener_conexion_local = obtener_conexion

def obtener_empleados_vps_df():
    """
    Abre el túnel SSH al VPS, lee los empleados activos de GoDaddy
    y regresa el DataFrame de Pandas formateado para el sincronizador.
    """
    global _tunnel
    try:
        if _tunnel is None or not _tunnel.is_active:
            _tunnel = SSHTunnelForwarder(
                (os.getenv("SSH_HOST"), int(os.getenv("SSH_PORT", 22))),
                ssh_username=os.getenv("SSH_USER"),
                ssh_password=os.getenv("SSH_PASS"),
                remote_bind_address=(os.getenv("VPS_HOST", "127.0.0.1"), int(os.getenv("VPS_DB_PORT", 3306))),
                allow_agent=False
            )
            _tunnel.start()

        conexion = mysql.connector.connect(
            host="127.0.0.1",
            port=_tunnel.local_bind_port,
            user=os.getenv("VPS_DB_USER"),
            password=os.getenv("VPS_DB_PASS"),
            database=os.getenv("VPS_DB")
        )

        query = "SELECT codigo, nombre, apellido_paterno, apellido_materno FROM empleados WHERE estatus = 'ACTIVO'"
        df = pd.read_sql(query, conexion)
        conexion.close()

        # Limpieza y formato de strings
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