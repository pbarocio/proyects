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
    page_title='AGROCISA CORE',
    page_icon="⚙️",
    layout='wide'
)

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
    
if "usuario" not in st.session_state:
    st.session_state["usuario"] = None

def validar_login(user_ingresado, pass_ingresado):
    credenciales = {
        os.getenv("USER_PABLO", "pablo"): os.getenv("PASS_PABLO", "admin123"),
        os.getenv("USER_LUCY", "lucy"): os.getenv("PASS_LUCY", "luci123")
    }
    if user_ingresado in credenciales and pass_ingresado == credenciales[user_ingresado]:
        return True
    return False

if not st.session_state["autenticado"]:
    st.title("🔒 AGROCISA CORE")
    st.subheader("Acceso Sistema TI")
    
    with st.form("form_login"):
        st.subheader("Iniciar Sesión")
        usuario_input = st.text_input("Usuario", type="default")
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
# INTERFAZ PRINCIPAL Y ESTILOS AVANZADOS DEL SIDEBAR
# ---------------------------------------------------------

def aplicar_estilo_global_sb_admin():
    st.markdown("""
        <style>
            /* Fondo global */
            .stApp { background-color: #0f172a !important; }
            .block-container {
                padding-top: 1.5rem !important;
                padding-bottom: 2rem !important;
                max-width: 95% !important;
            }

            /* Sidebar */
            section[data-testid="stSidebar"] {
                background-color: #0f172a !important;
                border-right: 1px solid #1e293b !important;
            }

            /* Tarjeta de usuario */
            .user-card {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
                padding: 10px 14px;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 10px;
            }

            /* Título del menú */
            .sidebar-section-title {
                font-size: 0.72rem;
                text-transform: uppercase;
                letter-spacing: 1px;
                color: #64748b;
                font-weight: 700;
                margin-top: 12px;
                margin-bottom: 8px;
            }

            /* TUNEADO DE RADIO BUTTONS DE STREAMLIT */
            /* Ocultar ÚNICAMENTE el círculo/radio button nativo */
            section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
                font-size: 0.9rem !important;
                font-weight: 600 !important;
            }

            section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label > div:first-child {
                display: none !important;
            }

            /* Contenedor tipo Tarjeta para las opciones */
            section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label {
                background-color: #1e293b !important;
                border: 1px solid #334155 !important;
                border-radius: 8px !important;
                padding: 10px 14px !important;
                margin-bottom: 6px !important;
                width: 100% !important;
                cursor: pointer !important;
                transition: all 0.2s ease-in-out !important;
            }

            /* Forzar texto visible */
            section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label * {
                color: #cbd5e1 !important;
            }

            /* Hover */
            section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover {
                background-color: #334155 !important;
                border-color: #38bdf8 !important;
                transform: translateX(4px);
            }
            section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label:hover * {
                color: #ffffff !important;
            }

            /* Opción Seleccionada / Activa */
            section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] {
                background: linear-gradient(90deg, #0284c7 0%, #0369a1 100%) !important;
                border-color: #38bdf8 !important;
                box-shadow: 0px 4px 12px rgba(56, 189, 248, 0.25) !important;
            }
            section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] > label[data-checked="true"] * {
                color: #ffffff !important;
                font-weight: 700 !important;
            }

            /* Botón primario */
            div.stButton > button[kind="primary"] {
                background-color: #2563eb !important;
                color: #ffffff !important;
                border: none !important;
                border-radius: 6px !important;
                font-weight: 600 !important;
            }

            /* Inputs y Selects */
            div[data-baseweb="select"] > div, input {
                background-color: #1e293b !important;
                border-color: #334155 !important;
                color: #f8fafc !important;
                border-radius: 6px !important;
            }

            /* Dataframes */
            div[data-testid="stDataFrame"] {
                border: 1px solid #334155 !important;
                border-radius: 8px !important;
            }
        </style>
    """, unsafe_allow_html=True)

aplicar_estilo_global_sb_admin()

# Panel Lateral (Sidebar)
with st.sidebar:
    st.title("⚙️ AGROCISA_core")
    
    st.markdown(f"""
        <div class="user-card">
            <span style="color: #38bdf8; font-size: 1.1rem;">👤</span>
            <div>
                <div style="font-size: 0.7rem; color: #64748b; text-transform: uppercase;">Operador Activo</div>
                <div style="font-weight: bold; color: #f8fafc;">{st.session_state['usuario']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.session_state["usuario"] = None
        st.rerun()

    st.markdown('<div class="sidebar-section-title">Módulos del Sistema</div>', unsafe_allow_html=True)

    opcion_menu = st.radio(
        "Módulos:",
        [
            "🏠 Inicio",
            "🔄 Sincronizador VPS",
            "✉️ Correos y Empleados",
            "🗂️ Gestor de Catálogos",
            "📄 Generar Responsivas / Desvincular Dispositivos",
            "🔍 Consultar Responsivas",
            "📞 Control de Líneas Telefónicas",
            "📱💻 Inventario de Equipos",
            "📊 Reportería y Métricas",
        ],
        label_visibility="collapsed"
    )

# ---------------------------------------------------------
# ENRUTADOR DE MÓDULOS
# ---------------------------------------------------------

if opcion_menu == "🏠 Inicio":
    st.title("⚙️ AGROCISA_core")
    st.caption("Sistema Central de Infraestructura, Inventarios y Automatización de TI")

    st.markdown("---")
    st.markdown(f"### 👋 ¡Bienvenido de vuelta, **{st.session_state['usuario']}**!")
    st.write("Selecciona un módulo en la barra lateral para empezar a trabajar o realizar consultas.")

    st.write("")

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info("🔄 **Sincronizador VPS**\n\nGestiona los Colaboradores sincronizando con app.agrocisa.com.mx para Altas/Bajas.")
    
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

elif opcion_menu == "📄 Generar Responsivas / Desvincular Dispositivos":
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