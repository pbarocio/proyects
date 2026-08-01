import streamlit as st
import pandas as pd

with st.sidebar:
    st.title("Menú Principal")
    
    opcion = st.radio(
        "Selecciona una opción:",
        ["Dashborard", "Empleados", "Responsivas"]
    )
    
    st.title("PUTA")

st.title("Hola qleros, les saluda el anticristo")

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