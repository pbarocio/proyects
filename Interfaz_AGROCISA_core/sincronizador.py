import streamlit as st
import sqlite3
import pandas as pd
import os

def obtener_conexion_local():
    """Abre conexión con la base de datos SQLite local."""
    db_path = os.getenv("DB_LOCAL_PATH", "agrocisa.db")
    return sqlite3.connect(db_path)

def obtener_personal_local():
    """Consulta la tabla de personal local y la regresa como DataFrame de Pandas."""
    try:
        conn = obtener_conexion_local()
        # Leemos la tabla usando pandas para mostrarla limpia en Streamlit
        query = "SELECT id, nombre, departamento, estatus FROM personal"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as error:
        st.error(f"⚠️ Error al consultar SQLite local: {error}")
        return None

def render():
    st.subheader("⚙️ Panel de Control de Sincronización")
    st.write("Compara el estado del personal en el VPS contra tu base de datos local.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Consultar Cambios en VPS", type="primary"):
            st.session_state["busqueda_vps"] = True
            
    with col2:
        st.caption("Estado: **Conexión a SQLite lista**")

    # Si el operador dio clic en consultar
    if st.session_state.get("busqueda_vps", False):
        st.divider()
        st.markdown("### 📋 Personal en BDD Local")
        
        df_personal = obtener_personal_local()
        
        if df_personal is not None and not df_personal.empty:
            # Dibujamos una tabla interactiva
            st.dataframe(df_personal, use_container_width=True)
            
            # Métrica rápida de total de empleados
            total = len(df_personal)
            st.metric(label="Total Registrados", value=f"{total} empleados")
        else:
            st.warning("No se encontraron registros en la tabla 'personal' o la tabla aún no existe.")