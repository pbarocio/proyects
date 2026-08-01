import streamlit as st
import pandas as pd

with st.sidebar:
    st.title("Menú Principal")
    
    opcion = st.radio(
        "Prueba",
        ["Dashborard", "Empleados", "Generar Responsiva", "Inventario de dispositivos"]
    )
    
    if opcion == "Empleados":
        opcion_empleado = st.selectbox("Elige una opcion", 
        ["Registrar empleado", "Modificar Empleado", "Baja Empleado"],
        index=None,
        placeholder="...",
        help="Selecciona una opción del menú"
        )
        
    if opcion == "Generar Responsiva":
        opcion_generar_responsivas = st.selectbox("Elige una opción",
        [""],
        index=None,
        placeholder="...",
        help="Selecciona una opción del menú"
    )
    
    if opcion == "Inventario de dispositivos":
        opcion_empleado = st.selectbox("Elige una opcion", 
        ["Registrar dispositivo", "Modificar dispositivo", "Baja dispositivo"],
        index=None,
        placeholder="...",
        help="Selecciona una opción del menú"
        )

st.title("AGROCISA CORE")

with st.form("Registro Empleado"):
    st.subheader("Registrar nuevo empleado")
    
    col1, col2 = st.columns(2)

st.write(f"Navegaste a la sección: **{opcion}**")

st.divider()  # Traza una línea horizontal (como un <hr>)

# 3. Simulamos datos como los que te va a entregar MariaDB
datos_demo = pd.DataFrame(
    {
        "Empleado": ["Pablo", "Alex", "Lucy"],
        "Equipo": ["Laptop Dell", "Monitor LG", "Teclado"],
        "Estatus": ["Asignado", "En Stock", "Asignado"],
    }
)

# Le aventamos el DataFrame a st.write directamente
st.write("### Inventario de prueba:")
st.write(datos_demo)