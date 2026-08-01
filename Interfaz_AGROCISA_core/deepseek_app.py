import streamlit as st
from sqlalchemy import create_engine, text
import pandas as pd

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="AGROCISA Dashboard",
    page_icon="🚜",
    layout="wide"
)

# --- CONEXIÓN A LA BASE DE DATOS ---
@st.cache_resource
def conectar_bdd():
    usuario = "agrocisa_admin"
    password = "4GR0C154#SIS"
    host = "servidor.agrocisa.corporativo"
    database = "agrocisa_core"
    
    url = f"mysql+pymysql://{usuario}:{password}@{host}/{database}"
    engine = create_engine(url)
    return engine

engine = conectar_bdd()

# --- FUNCIONES DE CONSULTA ---
@st.cache_data(ttl=300)
def contar_empleados_activos():
    query = "SELECT COUNT(*) FROM empleados WHERE id_estatus_empleado = 1"
    with engine.connect() as conn:
        resultado = conn.execute(text(query)).scalar()
    return resultado

@st.cache_data(ttl=300)
def contar_celulares_asignados():
    query = "SELECT COUNT(*) FROM inventario_celulares WHERE codigo_empleado IS NOT NULL"
    with engine.connect() as conn:
        resultado = conn.execute(text(query)).scalar()
    return resultado

@st.cache_data(ttl=300)
def contar_cpu_asignados():
    query = "SELECT COUNT(*) FROM inventario_cpu WHERE codigo_empleado IS NOT NULL"
    with engine.connect() as conn:
        resultado = conn.execute(text(query)).scalar()
    return resultado

@st.cache_data(ttl=300)
def contar_laptops_asignados():
    query = "SELECT COUNT(*) FROM inventario_laptops WHERE codigo_empleado IS NOT NULL"
    with engine.connect() as conn:
        resultado = conn.execute(text(query)).scalar()
    return resultado

@st.cache_data(ttl=300)
def contar_monitores_asignados():
    query = "SELECT COUNT(*) FROM inventario_monitores WHERE codigo_empleado IS NOT NULL"
    with engine.connect() as conn:
        resultado = conn.execute(text(query)).scalar()
    return resultado

@st.cache_data(ttl=300)
def contar_tablets_asignados():
    query = "SELECT COUNT(*) FROM inventario_tablets WHERE codigo_empleado IS NOT NULL"
    with engine.connect() as conn:
        resultado = conn.execute(text(query)).scalar()
    return resultado

@st.cache_data(ttl=300)
def contar_celulares_disponibles():
    query = "SELECT COUNT(*) FROM inventario_celulares WHERE codigo_empleado IS NULL"
    with engine.connect() as conn:
        resultado = conn.execute(text(query)).scalar()
    return resultado

@st.cache_data(ttl=300)
def contar_cpu_disponibles():
    query = "SELECT COUNT(*) FROM inventario_cpu WHERE codigo_empleado IS NULL"
    with engine.connect() as conn:
        resultado = conn.execute(text(query)).scalar()
    return resultado

@st.cache_data(ttl=300)
def contar_laptops_disponibles():
    query = "SELECT COUNT(*) FROM inventario_laptops WHERE codigo_empleado IS NULL"
    with engine.connect() as conn:
        resultado = conn.execute(text(query)).scalar()
    return resultado

@st.cache_data(ttl=300)
def contar_monitores_disponibles():
    query = "SELECT COUNT(*) FROM inventario_monitores WHERE codigo_empleado IS NULL"
    with engine.connect() as conn:
        resultado = conn.execute(text(query)).scalar()
    return resultado

@st.cache_data(ttl=300)
def contar_tablets_disponibles():
    query = "SELECT COUNT(*) FROM inventario_tablets WHERE codigo_empleado IS NULL"
    with engine.connect() as conn:
        resultado = conn.execute(text(query)).scalar()
    return resultado

# --- BARRA LATERAL ---
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=AGROCISA", use_container_width=True)
    st.title("🚜 AGROCISA")
    
    menu = st.radio(
        "Navegación",
        ["📊 Dashboard", "👥 Empleados", "📱 Inventario", "📄 Responsivas"],
        index=0
    )
    
    st.divider()
    st.caption("v1.0.0 - Pipeline estable")

# --- ÁREA PRINCIPAL ---
if menu == "📊 Dashboard":
    st.title("📊 Dashboard AGROCISA")
    st.caption("Estado general del sistema")
    
    # Obtener todos los datos
    with st.spinner("Cargando datos..."):
        empleados_activos = contar_empleados_activos()
        celulares_asignados = contar_celulares_asignados()
        cpu_asignados = contar_cpu_asignados()
        laptops_asignados = contar_laptops_asignados()
        monitores_asignados = contar_monitores_asignados()
        tablets_asignados = contar_tablets_asignados()
        celulares_disponibles = contar_celulares_disponibles()
        cpu_disponibles = contar_cpu_disponibles()
        laptops_disponibles = contar_laptops_disponibles()
        monitores_disponibles = contar_monitores_disponibles()
        tablets_disponibles = contar_tablets_disponibles()
    
    total_equipos = (
        celulares_asignados + celulares_disponibles +
        cpu_asignados + cpu_disponibles +
        laptops_asignados + laptops_disponibles +
        monitores_asignados + monitores_disponibles +
        tablets_asignados + tablets_disponibles
    )
    total_asignados = (
        celulares_asignados + cpu_asignados + laptops_asignados + 
        monitores_asignados + tablets_asignados
    )
    total_disponibles = (
        celulares_disponibles + cpu_disponibles + laptops_disponibles + 
        monitores_disponibles + tablets_disponibles
    )
    
    # --- FUNCIÓN PARA DIBUJAR TARJETA CON BARRA DE PROGRESO ---
    def tarjeta_con_barra(label, value, max_value, color, icon):
        porcentaje = (value / max_value * 100) if max_value > 0 else 0
        porcentaje = min(porcentaje, 100)  # Cap en 100%
        
        # Contenedor con estilo
        st.markdown(
            f"""
            <div style="
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 15px 20px;
                border-left: 5px solid {color};
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                height: 100%;
            ">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <span style="font-size: 28px;">{icon}</span>
                    <div style="flex: 1;">
                        <div style="font-size: 14px; color: #666; font-weight: 500;">{label}</div>
                        <div style="font-size: 28px; font-weight: 700; color: {color}; line-height: 1.2;">
                            {value:,}
                        </div>
                    </div>
                </div>
                <div style="margin-top: 8px;">
                    <div style="
                        height: 6px;
                        background-color: #e9ecef;
                        border-radius: 3px;
                        overflow: hidden;
                        position: relative;
                    ">
                        <div style="
                            width: {porcentaje}%;
                            height: 100%;
                            background-color: {color};
                            border-radius: 3px;
                            transition: width 0.3s ease;
                        "></div>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 11px; color: #999; margin-top: 3px;">
                        <span>{porcentaje:.0f}%</span>
                        <span>de {max_value:,}</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # --- TARJETAS (5 columnas) ---
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        tarjeta_con_barra("Empleados Activos", empleados_activos, 200, "#2E86C1", "👥")
    
    with col2:
        tarjeta_con_barra("Celulares Asignados", celulares_asignados, 150, "#28B463", "📱")
    
    with col3:
        tarjeta_con_barra("Equipos Asignados", total_asignados, total_equipos, "#F39C12", "💻")
    
    with col4:
        tarjeta_con_barra("Celulares Disponibles", celulares_disponibles, 150, "#E74C3C", "📱")
    
    with col5:
        tarjeta_con_barra("Equipos Disponibles", total_disponibles, total_equipos, "#8E44AD", "💻")
    
    # --- DETALLE DE EQUIPOS ---
    st.divider()
    st.subheader("📋 Detalle de Equipos")
    
    data = {
        "Tipo": ["Celulares", "CPUs", "Laptops", "Monitores", "Tablets"],
        "Asignados": [celulares_asignados, cpu_asignados, laptops_asignados, monitores_asignados, tablets_asignados],
        "Disponibles": [celulares_disponibles, cpu_disponibles, laptops_disponibles, monitores_disponibles, tablets_disponibles],
        "Total": [
            celulares_asignados + celulares_disponibles,
            cpu_asignados + cpu_disponibles,
            laptops_asignados + laptops_disponibles,
            monitores_asignados + monitores_disponibles,
            tablets_asignados + tablets_disponibles
        ]
    }
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

else:
    st.title(f"🚧 {menu} - En construcción")
    st.info("Esta sección estará disponible pronto. Por ahora, usa el Dashboard para ver el estado general del sistema.")

st.divider()
st.caption("AGROCISA Core v1.0 - Dashboard desarrollado con Streamlit")