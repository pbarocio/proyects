import streamlit as st
import os
from dotenv import load_dotenv
import sincronizador
import catalogos
import inventario
import responsivas

load_dotenv()

st.set_page_config(
    page_title = 'AGROCISA CORE',
    page_icon = "⚙️",
    layout='wide'
)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

def validar_login(user_ingresado, pass_ingresado):
    # Usuarios y contraseñas desde el .env
    credenciales = {
        os.getenv("USER_PABLO", "pablo"): os.getenv("PASS_PABLO", "admin123"),
        os.getenv("USER_LUCY", "lucy"): os.getenv("PASS_LUCY", "luci123")
    }
    
    # Valida si el usuario existe y si la contraseña coincide
    if user_ingresado in credenciales and pass_ingresado == credenciales[user_ingresado]:
        return True
    return False

if not st.session_state["autenticado"]:
    st.title("🔒 AGROCISA CORE")
    st.subheader("Acceso Sistema TI")
    
    with st.form("form_login"):
        st.subheader("Iniciar Sesión")
        usuario_input = st.text_input("Usuario", type="default") # Quitamos type="password" para ver el nombre al teclear
        pass_input = st.text_input("Contraseña", type="password")
        submit = st.form_submit_button("Entrar al Sistema")
        
        if submit:
            if validar_login(usuario_input, pass_input):
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = usuario_input
                st.success("¡Bienvenido Bicho!")
                st.rerun()
            else:
                st.error("⚠️ Credenciales incorrectas...")
    st.stop()

# ---------------------------------------------------------
# INTERFAZ PRINCIPAL (Solo se ve si ya se autenticó)
# ---------------------------------------------------------

# Panel Lateral (Sidebar)
st.sidebar.title("⚙️ AGROCISA_core")
st.sidebar.write(f"👤 Operador: **{st.session_state['usuario']}**")

# Botón para salir del sistema
if st.sidebar.button("Cerrar Sesión"):
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None
    st.rerun()

st.sidebar.divider()

# Menú de opciones (Módulos)
opcion_menu = st.sidebar.radio(
    "Módulos del Sistema:",
    [
        "🔄 Sincronizador VPS",
        "🗂️ Gestor de Catálogos",
        "📄 Generar Responsivas",
        "📱💻 Inventario de Equipos"
    ]
)

# ---------------------------------------------------------
# ENRUTADOR DE MÓDULOS (El cerebro del menú)
# ---------------------------------------------------------

if opcion_menu == "🔄 Sincronizador VPS":
    st.header("🔄 Sincronización Automática con VPS")
    sincronizador.render()

elif opcion_menu == "🗂️ Gestor de Catálogos":
    catalogos.render()

elif opcion_menu == "📄 Generar Responsivas":
    responsivas.render()

elif opcion_menu == "📱💻 Inventario de Equipos":
    inventario.render()