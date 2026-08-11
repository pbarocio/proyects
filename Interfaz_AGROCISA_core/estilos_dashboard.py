import streamlit as st

def aplicar_estilo_sb_admin():
    st.markdown("""
        <style>
            /* Fondo de la app */
            .stApp {
                background-color: #0f172a;
            }
            
            /* Contenedor principal con margen amplio */
            .block-container {
                padding-top: 1.5rem !important;
                padding-bottom: 2rem !important;
                max-width: 95% !important;
            }

            /* TARJETAS ESTILO SB ADMIN 2 */
            div[data-testid="stMetric"] {
                background-color: #1e293b !important;
                border-radius: 8px !important;
                padding: 15px 20px !important;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.1) !important;
                border-left: 5px solid #3b82f6 !important; /* Azul por defecto */
            }

            /* Asignación de colores por columna tipo SB Admin */
            div[data-testid="column"]:nth-child(1) div[data-testid="stMetric"] {
                border-left-color: #3b82f6 !important; /* Total: Azul */
            }
            div[data-testid="column"]:nth-child(2) div[data-testid="stMetric"] {
                border-left-color: #10b981 !important; /* Asignados: Verde */
            }
            div[data-testid="column"]:nth-child(3) div[data-testid="stMetric"] {
                border-left-color: #06b6d4 !important; /* Disponibles: Cyan */
            }
            div[data-testid="column"]:nth-child(4) div[data-testid="stMetric"] {
                border-left-color: #f59e0b !important; /* Taller: Amarillo */
            }

            /* Tipografía de las Tarjetas */
            div[data-testid="stMetricLabel"] > div {
                color: #94a3b8 !important;
                font-size: 0.85rem !important;
                font-weight: 700 !important;
                text-transform: uppercase !important;
                letter-spacing: 0.05em !important;
            }

            div[data-testid="stMetricValue"] > div {
                color: #f8fafc !important;
                font-size: 1.8rem !important;
                font-weight: 800 !important;
            }

            /* Contenedores de Gráficas y Tablas */
            div[data-testid="stForm"], div.element-container:has(iframe) {
                background-color: #1e293b;
                border-radius: 10px;
                padding: 10px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            }
        </style>
    """, unsafe_allow_html=True)