import pandas as pd
import streamlit as st

# ==========================================
# 1. BACKEND: SIMULACIÓN DE CONSULTAS A BDD
# (Aquí es donde irán tus consultas con SQLAlchemy/MariaDB)
# ==========================================


def obtener_datos_dashboard():
    # Simulamos una consulta pesada del Dashboard
    return {
        "total_empleados": 120,
        "celulares_asignados": 85,
        "laptops_asignadas": 40,
    }


def obtener_tabla_empleados():
    # Simulamos un SELECT * FROM empleados
    return pd.DataFrame(
        {
            "Código": [101, 102, 103],
            "Nombre": ["Pablo", "Alex", "Lucy"],
            "Puesto": ["TI & Infraestructura", "Soporte", "Asistente BDD"],
        }
    )


# ==========================================
# 2. FRONT-END: INTERFAZ Y NAVEGACIÓN
# ==========================================

# Dibujamos la barra lateral
with st.sidebar:
    st.title("🌾 AGROCISA")
    st.caption("Control de Activos")
    st.divider()

    # Guardamos la opción seleccionada en la variable 'modulo'
    modulo = st.radio(
        "Navegación:", ["Dashboard", "Empleados", "Responsivas"]
    )

# ==========================================
# 3. EL ENLACE (IF / ELIF / ELSE)
# ==========================================

if modulo == "Dashboard":
    st.title("📊 Dashboard General")
    st.write("Resumen ejecutivo de activos en tiempo real.")

    # LLAMAMOS AL BACKEND
    datos = obtener_datos_dashboard()

    # Dibujamos 3 tarjetas de métricas usando los datos del Backend
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Empleados", datos["total_empleados"])
    col2.metric("Celulares Asignados", datos["celulares_asignados"])
    col3.metric("Laptops Asignadas", datos["laptops_asignadas"])

elif modulo == "Empleados":
    st.title("👥 Directorio de Empleados")

    # LLAMAMOS AL BACKEND
    df_empleados = obtener_tabla_empleados()

    # Pintamos la tabla
    st.write("Lista completa del personal registrado:")
    st.dataframe(df_empleados, use_container_width=True)

elif modulo == "Responsivas":
    st.title("📄 Generador de Responsivas")
    st.write("Módulo para emitir cartas responsivas individuales.")

    # Un selector dinámico
    empleado_select = st.selectbox(
        "Selecciona un empleado:", ["Pablo", "Alex", "Lucy"]
    )

    if st.button("Generar PDF"):
        st.success(f"¡Responsiva lista para descargar para: {empleado_select}!")