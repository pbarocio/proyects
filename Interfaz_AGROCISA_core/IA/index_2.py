import streamlit as st

st.set_page_config(
    page_title="AGROCISA",
    page_icon="",
    layout="wide"
)

with st.sidebar:
    st.title("AGROCISA")
    st.write("Menú de navegación")
    menu = st.radio(
        "Navegación",
        ["Empleado", 
         "Asignaciones", 
         "Inventario",
         ""]
    )

if menu == "Inicio":
    st.title("Hola qleros, les saluda el anticristo")
elif menu == "Empleados":
    st.title("👥 Empleados")
    st.write("Aquí van los empleados")
elif menu == "Inventario":
    st.title("📱 Inventario")
    st.write("📱 Aquí va el inventario")
    
st.divider()
st.caption("AGROCISA Core v1.0 - Hecho con Streamlit")