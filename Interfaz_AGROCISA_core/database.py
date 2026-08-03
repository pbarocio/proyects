import mysql.connector
import os
from sshtunnel import SSHTunnelForwarder
from pathlib import Path
import paramiko
from dotenv import load_dotenv #Cargar variables de entorno
import pandas as pd

env_path = Path(__file__).parent / ".env"
load_dotenv(env_path) # === CARGAR .env ===

# --- PARCHE PARA PYTHON 3.14 / PARAMIKO Y SSHTUNNEL ---
if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = paramiko.PKey.PKey if hasattr(paramiko.PKey, 'PKey') else paramiko.RSAKey
# ------------------------------------------------------

def obtener_conexion():
    try:
        conexion = mysql.connector.connect(
            host=str(os.getenv("LOCAL_HOST")),
            user=str(os.getenv("LOCAL_DB_USER")),
            password=str(os.getenv("LOCAL_DB_PASSWORD")),
            database=str(os.getenv("LOCAL_DATABASE")),
        )
        
        return conexion
    except Exception as e:
        print(f"Error al conectar a MariaDB: {e}")
        return None

def obtener_empleados_vps():
    """
    Abre un túnel SSH seguro al VPS de GoDaddy, lee la tabla de empleados
    de la base de datos central y la regresa como un DataFrame de Pandas.
    """
    # 1. Configurar y arrancar el Túnel SSH
    tunnel = SSHTunnelForwarder(
        (os.getenv("SSH_HOST"), int(os.getenv("SSH_PORT"))),                    # Host SSH / IP del VPS
        ssh_username=os.getenv("SSH_USER"),         # 'agrocisa'
        ssh_password=os.getenv("SSH_PASS"),         # Tu clave de SSH / GoDaddy
        remote_bind_address=(os.getenv("VPS_HOST"), int(os.getenv("VPS_DB_PORT"))),     # Apunta al MariaDB dentro del VPS
        allow_agent=False
    )
    
    tunnel.start()
    print("🔓 Túnel SSH abierto con éxito.")

    try:
        # 2. Conectar a MariaDB a través del puerto local que asignó el túnel
        conexion = mysql.connector.connect(
            host=os.getenv("VPS_HOST"),
            port=tunnel.local_bind_port,            # Puerto dinámico del túnel
            user=os.getenv("VPS_DB_USER"),          # 'agrocisa' o el usuario de MariaDB
            password=os.getenv("VPS_DB_PASS"),      # Clave de la BD
            database=os.getenv("VPS_DB")            # La base de datos de César
        )

        # 3. Traerte los datos directo a Pandas
        query = "SELECT codigo, nombre, apellido_materno, apellido_paterno FROM empleados WHERE estatus = 'ACTIVO'"
        
        df_empleados = pd.read_sql(query, conexion)
        
        conexion.close()
        
        df_empleados["nombre"] = df_empleados["nombre"].fillna("").astype(str).str.strip().str.title()
        df_empleados["apellido_paterno"] = df_empleados["apellido_paterno"].fillna("").astype(str).str.strip().str.title()
        df_empleados["apellido_materno"] = df_empleados["apellido_materno"].fillna("").astype(str).str.strip().str.title()
        
        df_empleados["nombre_completo"] = (
            (df_empleados["nombre"] + " " + df_empleados["apellido_paterno"] + " " + df_empleados["apellido_materno"])
            .str.replace(r'\s+', ' ', regex=True)
        )
        
        mapa_empleados = {}
        
        for _, row in df_empleados.iterrows():
            nombre_completo = f"{row["nombre"]} {row["apellido_paterno"]} {row["apellido_materno"]}".strip()
            label = f"{row["codigo"]} - {nombre_completo}"
            
            mapa_empleados[label] = {
                "codigo": row["codigo"],
                "nombre": row["nombre"],
                "apellido_paterno": row["apellido_paterno"],
                "apellido_materno": row["apellido_materno"],
            }
        
        return mapa_empleados

    finally:
        # 4. SIEMPRE cerrar el túnel para no dejar conexiones colgadas en el servidor
        tunnel.stop()
        print("🔒 Túnel SSH cerrado.")

obtener_empleados_vps()