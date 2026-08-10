import streamlit as st
import pandas as pd
from database import obtener_empleados_vps
from consultas import (
    obtener_sucursales,
    obtener_departamentos,
    obtener_puestos,
    existe_empleado,
    guardar_empleado,
)

def registrar_empleado():
    
    mapa_empleados = obtener_empleados_vps()
    mapa_sucursales = obtener_sucursales()
    mapa_departamentos = obtener_departamentos()
    mapa_puestos = obtener_puestos()
    
    with st.form(key="Registrar_Empleado"):
        
        opcion_empleado_vps = st.selectbox(
            "Buscar Empleado (Fuente: VPS agrocisa.com.mx)",
            options=list(mapa_empleados.keys()),
            index=None,
            placeholder="Escribe el código o nombre para buscar ... "
        )
        
        opcion_sucursales_nombre = st.selectbox(
            "Sucursal",
            options=list(mapa_sucursales.keys()),
            index=None,
            placeholder="Seleccione una Sucursal... "
        )
        
        opcion_departamentos_nombre = st.selectbox(
            "Departamento",
            options=list(mapa_departamentos.keys()),
            index=None,
            placeholder="Seleccione un Departamento... "
        )
        
        opcion_puestos_nombre = st.selectbox(
            "Puesto",
            options=list(mapa_puestos.keys()),
            index=None,
            placeholder="Seleccione un Puesto... "
        )
        
        boton_empleado = st.form_submit_button("Enviar")
        
        if boton_empleado:
            errores = False
            
            if not opcion_empleado_vps:
                st.error("Debes seleccionar un empleado de la lista...")
                errores = True
            
            if not opcion_sucursales_nombre:
                st.error("Debes seleccionar una sucursal de la lista...")
                errores = True
                
            if not opcion_departamentos_nombre:
                st.error("Debes seleccionar un departamento de la lista...")
                errores = True
                
            if not errores:
                datos_emp = mapa_empleados.get(opcion_empleado_vps)
                
                codigo = datos_emp["codigo"]
                ap_paterno = datos_emp["apellido_paterno"]
                ap_materno = datos_emp["apellido_materno"]
                nombre = datos_emp["nombre"]
                id_sucursal_seleccionada = mapa_sucursales.get(opcion_sucursales_nombre)
                id_departamento_seleccionado = mapa_departamentos.get(opcion_departamentos_nombre)
                id_puesto_seleccionado = mapa_puestos.get(opcion_puestos_nombre)
                
                if existe_empleado(codigo):
                    st.warning(f"⚠️ {opcion_empleado_vps} ya está registrado (a)...")
                else:
                    exito = guardar_empleado(
                        codigo, 
                        ap_paterno, 
                        ap_materno, 
                        nombre, 
                        id_sucursal_seleccionada, 
                        id_departamento_seleccionado, 
                        id_puesto_seleccionado, 
                    )
                    
                    if exito:
                        st.success("Empleado capturado con éxito!")
                        st.write(
                            "**Datos Guardados:**", 
                            f"{codigo} - {nombre} {ap_paterno} {ap_materno} |" 
                            f"Sucursal: {opcion_sucursales_nombre} |" 
                            f"Departamento: {opcion_departamentos_nombre} |"
                            f"Puesto: {opcion_puestos_nombre} |"
                        )
                    else:
                        st.error("Ocurrió un error al guardar el empleado")
            else:
                st.error("Completa los campos pendientes... ")
                

# ==========================================
# 1. SIDEBAR: Menú Principal
# ==========================================

with st.sidebar:
    st.title("Menú Principal")
    
    opcion = st.radio(
        "Prueba",
        [
            "Dashboard", 
            "Empleados", 
            "Generar Responsiva", 
            "Inventario de dispositivos",
        ]
    )
    
    opcion_sub_menu = None
    
    if opcion == "Empleados":
        opcion_sub_menu = st.selectbox(
            "Elige una opcion", 
            ["Registrar Empleado", "Modificar Empleado", "Baja Empleado"],
            index=None,
            placeholder="...",
            help="Selecciona..."
        )
        
    if opcion == "Generar Responsiva":
        opcion_sub_menu = st.selectbox(
            "Elige una opción",
            [""],
            index=None,
            placeholder="...",
            help="Selecciona una opción del menú"
    )
    
    if opcion == "Inventario de dispositivos":
        opcion_sub_menu = st.selectbox(
            "Elige una opcion", 
        [
            "Registrar dispositivo", 
            "Modificar dispositivo", 
            "Baja dispositivo"
        ],
            index=None,
            placeholder="...",
            help="Selecciona una opción del menú"
        )
        
# ==========================================
# 2. CUERPO PRINCIPAL (PANTALLA)
# ==========================================

st.title("AGROCISA CORE")

if opcion == "Dashboard":
    st.write("### Bienvenida al Dashboard")
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

elif opcion == "Empleados":
    if opcion_sub_menu == "Registrar Empleado":
        registrar_empleado()
    else:
        st.info("Sección Empleados")

elif opcion == "Generar Responsiva":
    st.write("Módulo de responsivas en construcción...")
    
elif opcion == "Inventario de dispositivos":
    st.write("Módulo de Inventario en construcción..")