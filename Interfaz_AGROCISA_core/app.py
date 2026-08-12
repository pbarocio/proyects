import streamlit as st
import os
from dotenv import load_dotenv
import sincronizador
import catalogos
import inventario
import responsivas
import correos_electronicos
import reporteria
import sync_drive
import lineas
import consulta_responsivas

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

def aplicar_estilo_global_sb_admin():
    st.markdown("""
        <style>
            /* Fondo global y contenedores principales */
            .stApp { background-color: #0f172a !important; }
            .block-container {
                padding-top: 1.5rem !important;
                padding-bottom: 2rem !important;
                max-width: 95% !important;
            }

            /* Sidebar estilo SB Admin */
            section[data-testid="stSidebar"] {
                background-color: #1e293b !important;
                border-right: 1px solid #334155 !important;
            }
            section[data-testid="stSidebar"] * {
                color: #f8fafc !important;
            }

            /* Botones estilo Bootstrap / Admin */
            div.stButton > button[kind="primary"] {
                background-color: #2563eb !important;
                color: #ffffff !important;
                border: none !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
                transition: all 0.2s ease-in-out !important;
            }
            div.stButton > button[kind="primary"]:hover {
                background-color: #1d4ed8 !important;
                box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
            }

            /* Inputs y Selectbox encajados en el tema oscuro */
            div[data-baseweb="select"] > div, input {
                background-color: #1e293b !important;
                border-color: #334155 !important;
                color: #f8fafc !important;
                border-radius: 6px !important;
            }

            /* Tablas y Dataframes */
            div[data-testid="stDataFrame"] {
                border: 1px solid #334155 !important;
                border-radius: 8px !important;
            }
        </style>
    """, unsafe_allow_html=True)

# Llama la función al mero inicio de tu app.py:
aplicar_estilo_global_sb_admin()

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
        "🏠 Inicio",
        "🔄 Sincronizador VPS",
        "✉️ Correos y Empleados",
        "🗂️ Gestor de Catálogos",
        "📄 Generar Responsivas",
        "🔍 Consultar Responsivas",
        "📞 Control de Líneas Telefónicas",
        "📱💻 Inventario de Equipos",
        "📊 Reportería y Métricas",
    ]
)

# ---------------------------------------------------------
# ENRUTADOR DE MÓDULOS (El cerebro del menú)
# ---------------------------------------------------------

if opcion_menu == "🏠 Inicio":
    st.title("⚙️ AGROCISA_core")
    st.caption("Sistema Central de Infraestructura, Inventarios y Automatización de TI")

    # Si tienes un archivo de imagen en la carpeta, lo cargas así:
    # st.image("logo.png", width=280)

    st.markdown("---")
    st.markdown(f"### 👋 ¡Bienvenido de vuelta, **{st.session_state['usuario']}**!")
    st.write("Selecciona un módulo en la barra lateral para empezar a trabajar o realizar consultas.")

    st.write("")

    # Accesos rápidos visuales tipo Tarjeta
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info("🔄 **Sincronizador VPS**\n\nGestiona los Colaboradores sincronizando con app.agrocisa.com.mx. para Altas/Bajas")
    
    with col2:
        st.info("📊 **Reportería & Drive**\n\nConsulta el inventario general, gráficas de distribución y sincroniza con Google Sheets.")
        
    with col3:
        st.info("📄 **Gestión de Responsivas**\n\nAsigna hardware a colaboradores y genera cartas responsivas automáticas en Word.")

    with col4:
        st.info("💻📱 **Control de Inventario**\n\nRegistra y edita celulares, computadoras, monitores, tablets y redes.")

elif opcion_menu == "🔄 Sincronizador VPS":
    st.header("🔄 Sincronización Automática con VPS")
    sincronizador.render()

elif opcion_menu == "🗂️ Gestor de Catálogos":
    catalogos.render()

elif opcion_menu == "📄 Generar Responsivas":
    responsivas.render()

elif opcion_menu == "🔍 Consultar Responsivas":
    consulta_responsivas.render_consulta()

elif opcion_menu == "📞 Control de Líneas Telefónicas":
    lineas.render()

elif opcion_menu == "📱💻 Inventario de Equipos":
    inventario.render()
    
elif opcion_menu == "✉️ Correos y Empleados":
    correos_electronicos.render()

elif opcion_menu == "📊 Reportería y Métricas":
    reporteria.render()