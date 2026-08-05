import streamlit as st
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración inicial de la página
st.set_page_config(
    page_title="AGROCISA Core",
    page_icon="⚙️",
    layout="wide"
)

# ---------------------------------------------------------
# 1. ESTADO DE LA SESIÓN (LOGIN)
# ---------------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

def validar_login(user, password):
    # Aquiles metes credenciales del .env o tu validación simple
    USER_ADMIN = os.getenv("APP_USER", "admin")
    PASS_ADMIN = os.getenv("APP_PASS", "admin123")
    return user == USER_ADMIN and password == PASS_ADMIN

# ---------------------------------------------------------
# 2. PANTALLA DE BLOQUEO (SI NO HAY LOGIN)
# ---------------------------------------------------------
if not st.session_state["autenticado"]:
    st.title("🔒 AGROCISA CORE | Acceso Sistema TI")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_login"):
            st.subheader("Iniciar Sesión")
            usuario_input = st.text_input("Usuario")
            pass_input = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Entrar al Sistema")
            
            if submit:
                if validar_login(usuario_input, pass_input):
                    st.session_state["autenticado"] = True
                    st.session_state["usuario"] = usuario_input
                    st.success("¡Bienvenido, bicho!")
                    st.rerun()
                else:
                    st.error("⚠️ Credenciales no válidas. Acceso denegado.")
    st.stop()  # Detiene todo el renderizado si no se ha autenticado

# ---------------------------------------------------------
# 3. INTERFAZ PRINCIPAL (SOLO SI YA SE AUTENTICÓ)
# ---------------------------------------------------------
st.sidebar.title("⚙️ AGROCISA_core")
st.sidebar.write(f"👤 Operador: **{st.session_state['usuario']}**")

if st.sidebar.button("Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None
    st.rerun()

st.sidebar.divider()

# Menú lateral con TU nuevo orden lógico
opcion_menu = st.sidebar.radio(
    "Módulos del Sistema:",
    [
        "🔄 Sincronizador VPS",
        "📄 Generar Responsivas",
        "📱💻 Inventario de Equipos"
    ]
)

# ---------------------------------------------------------
# 4. ENRUTADOR DE MÓDULOS
# ---------------------------------------------------------
if opcion_menu == "🔄 Sincronizador VPS":
    st.header("🔄 Sincronización Automática con VPS")
    st.info("Módulo para actualizar personal y procesar bajas/liberación de equipos automáticamente.")
    # Aquí mandaremos llamar la función de sync

elif opcion_menu == "📄 Generar Responsivas":
    st.header("📄 Generador de Responsivas (.docx)")
    st.info("Módulo para asignar equipos disponibles a empleados activos y empaquetar el documento.")

elif opcion_menu == "📱💻 Inventario de Equipos":
    st.header("📱💻 Gestión de Inventario de TI")
    st.info("Módulo para alta de hardware, consulta de estados y bitácora de observaciones.")