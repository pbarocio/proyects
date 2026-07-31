import streamlit as st
from db_querys import obtener_metricas_generales, obtener_resumen_inventario

# Configuración básica de la página
st.set_page_config(page_title="AGROCISA_core", layout="wide")

# --- BARRA LATERAL (Sidebar) ---
st.sidebar.title("AGROCISA_core")
opcion_menu = st.sidebar.radio(
    "Menú Principal",
    ["Dashboard Principal", "Generar Responsiva", "Gestión de Activos", "Directorio de Empleados"]
)

# --- PÁGINA PRINCIPAL / DASHBOARD ---
if opcion_menu == "Dashboard Principal":
    st.title("Panel de Control - Infraestructura y TI")
    st.markdown("---")
    
    # Obtenemos los datos de la DB
    emp_activos, resp_activas = obtener_metricas_generales()
    df_inventario = obtener_resumen_inventario()
    
    # 1. TARJETAS DE MÉTRICAS GENERALES (En 2 columnas)
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Empleados Activos", value=emp_activos)
    with col2:
        st.metric(label="Responsivas Activas (Equipos Asignados)", value=resp_activas)
        
    st.markdown("### ") # Espaciador
    
    # 2. TABLA DE RESUMEN DE INVENTARIO Y DISPONIBILIDAD
    st.subheader("Estado General del Inventario por Tipo de Equipo")
    st.dataframe(df_inventario, use_container_width=True, hide_index=True)