import streamlit as st
import mysql.connector
import os
from sshtunnel import SSHTunnelForwarder
from pathlib import Path
import paramiko
from dotenv import load_dotenv
import pandas as pd

# Cargar .env
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

if not hasattr(paramiko, 'DSSKey'):
    paramiko.DSSKey = paramiko.PKey.PKey if hasattr(paramiko.PKey, 'PKey') else paramiko.RSAKey

def obtener_empleados_local_df():
    """Trae empleados locales con el nombre de su tipo de contrato vía JOIN (3NF)."""
    try:
        conexion = mysql.connector.connect(
            host=str(os.getenv("LOCAL_HOST")),
            user=str(os.getenv("LOCAL_DB_USER")),
            password=str(os.getenv("LOCAL_DB_PASSWORD")),
            database=str(os.getenv("LOCAL_DATABASE")),
        )
        query = """
            SELECT e.codigo, e.nombre, e.apellido_paterno, e.apellido_materno, 
                   e.id_tipo_contrato, c.tipo_contrato AS tipo_contrato
            FROM empleados e
            JOIN tipo_contrato_empleados c ON e.id_tipo_contrato = c.id_tipo_contrato
        """
        df = pd.read_sql(query, conexion)
        conexion.close()
        
        # Limpieza básica
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
        st.error(f"⚠️ Error al consultar MariaDB Local: {e}")
        return None

def obtener_empleados_vps_df():
    """Conecta por túnel SSH a MariaDB en GoDaddy y trae activos."""
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
    """Aplica la lógica de conjuntos en Pandas y filtra las excepciones."""
    codigos_vps = set(df_vps["codigo"])
    
    # 1. Candidatos a baja: Existen en local pero YA NO están en VPS activo
    candidatos_baja = df_local[~df_local["codigo"].isin(codigos_vps)].copy()
    
    # Bajas reales (Solo INTERNO / id_tipo_contrato == 1)
    bajas_reales = candidatos_baja[candidatos_baja["id_tipo_contrato"] == 1]
    
    # Omitidos por excepción (EXTERNO / id_tipo_contrato == 2)
    externos_protegidos = candidatos_baja[candidatos_baja["id_tipo_contrato"] == 2]
    
    # 2. Altas nuevas: Existen en VPS pero AÚN NO están en local
    codigos_local = set(df_local["codigo"])
    altas_nuevas = df_vps[~df_vps["codigo"].isin(codigos_local)].copy()
    
    return bajas_reales, externos_protegidos, altas_nuevas

def importar_altas_locales(df_altas):
    """Inserta los empleados nuevos del VPS a MariaDB Local con contrato INTERNO (1)."""
    try:
        conexion = obtener_conexion_local()
        cursor = conexion.cursor()
        
        # Asignamos el id_tipo_contrato = 1 (INTERNO) por defecto
        df_altas["id_tipo_contrato"] = 1
        
        # Preparamos la consulta masiva
        query = """
            INSERT INTO empleados (codigo, nombre, apellido_paterno, apellido_materno, id_tipo_contrato)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                nombre=VALUES(nombre),
                apellido_paterno=VALUES(apellido_paterno),
                apellido_materno=VALUES(apellido_materno);
        """
        
        datos = [
            (row["codigo"], row["nombre"], row["apellido_paterno"], row["apellido_materno"], row["id_tipo_contrato"])
            for _, row in df_altas.iterrows()
        ]
        
        cursor.executemany(query, datos)
        conexion.commit()
        conexion.close()
        st.success(f"✅ Se importaron {len(df_altas)} nuevos empleados a MariaDB Local.")
    except Exception as e:
        st.error(f"⚠️ Error al importar altas: {e}")

def render():
    st.subheader("⚙️ Panel de Control de Sincronización")
    st.write("Cruza de información entre MariaDB VPS (GoDaddy) y BDD Local.")

    if st.button("🔄 Ejecutar Sincronización y Diagnóstico", type="primary"):
        with st.spinner("🔓 Abriendo túnel SSH y analizando bases de datos..."):
            df_local = obtener_empleados_local_df()
            df_vps = obtener_empleados_vps_df()

            if df_local is not None and df_vps is not None:
                bajas, protegidos, altas = procesar_sincronizacion(df_local, df_vps)

                st.divider()

                # Métricas rápidas
                c1, c2, c3 = st.columns(3)
                c1.metric("🚨 Bajas Reales (Internos)", f"{len(bajas)} empleados")
                c2.metric("🛡️ Externos Protegidos", f"{len(protegidos)} empleados")
                c3.metric("✨ Altas Detectadas", f"{len(altas)} empleados")

                # Pestañas organizadas
                tab1, tab2, tab3 = st.tabs(["🚨 Bajas a Procesar", "🛡️ Externos Omitidos", "✨ Nuevas Altas"])

                with tab1:
                    if not bajas.empty:
                        st.error("Los siguientes empleados internos ya no están activos en VPS. Se requiere liberar sus equipos.")
                        st.dataframe(bajas[["codigo", "nombre_completo", "tipo_contrato"]], use_container_width=True)
                    else:
                        st.success("No hay bajas pendientes de procesar.")

                with tab2:
                    if not protegidos.empty:
                        st.info("Detectados inactivos en VPS pero ignorados automáticamente por ser EXTERNOS.")
                        st.dataframe(protegidos[["codigo", "nombre_completo", "tipo_contrato"]], use_container_width=True)
                    else:
                        st.write("No hay externos con estatus especial.")

                with tab3:
                    if not altas.empty:
                        st.warning("Empleados activos en VPS que no existen en la base de datos local.")
                        st.dataframe(altas[["codigo", "nombre_completo"]], use_container_width=True)
                    else:
                        st.success("Tu base de datos local está 100% al día con las altas del VPS.")