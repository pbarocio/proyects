import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title = 'AGROCISA CORE',
    page_icon = "⚙️",
    #layout='wide'
)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

# Función para validar credenciales
def validar_login(user_ingresado, pass_ingresado):
    USER_CORRECTO = os.getenv("APP_USER", "admin")
    PASS_CORRECTO = os.getenv("APP_PASS", "admin123")
    
    return user_ingresado == USER_CORRECTO and pass_ingresado == PASS_CORRECTO

if not st.session_state["autenticado"]:
    st.title("🔒 AGROCISA CORE")
    st.subheader("Acceso Sistema TI")
    
    with st.form("form_login"):
        st.subheader("Iniciar Sesión")
        usuario_input = st.text_input("Usuario", type="password")
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

