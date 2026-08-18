import streamlit as st
import pandas as pd
from database import obtener_conexion

def aplicar_estilos_pantalla():
    st.markdown("""
        <style>
            .appview-container .main .block-container {
                max-width: 100% !important;
                padding-left: 2rem !important;
                padding-right: 2rem !important;
            }
        </style>
    """, unsafe_allow_html=True)

def obtener_columnas_tabla(cursor, tabla):
    try:
        cursor.execute(f"SHOW COLUMNS FROM {tabla}")
        return [row[0] for row in cursor.fetchall()]
    except Exception:
        return []

# Configuración y mapeo de tablas maestras
CATALOGOS_CONFIG = {
    "Modelos Celulares": {
        "tabla": "modelos_celulares",
        "pk": "id_modelo",
        "tipo": "modelo_celular"
    },
    "Sucursales": {
        "tabla": "sucursales",
        "pk": "id_sucursal",
        "col_nombre": "nombre_sucursal",
        "label": "Nombre de la Sucursal (ej. La Barca, Morelia):",
        "tipo": "simple"
    },
    "Departamentos": {
        "tabla": "departamentos",
        "pk": "id_departamento",
        "col_nombre": "nombre_departamento",
        "label": "Nombre del Departamento (ej. Sistemas, Contabilidad):",
        "tipo": "simple"
    },
    "Puestos": {
        "tabla": "puestos",
        "pk": "id_puesto",
        "col_nombre": "nombre_puesto",
        "label": "Nombre del Puesto (ej. Asesor de Ventas, Chofer):",
        "tipo": "simple"
    },
    "Condición de Equipos": {
        "tabla": "condicion",
        "pk": "id_condicion",
        "col_nombre": "condicion_opcion",
        "label": "Opción de Condición (ej. Excelente, Buenas condiciones):",
        "tipo": "simple"
    },
    "Cargadores": {
        "tabla": "cargadores",
        "pk": "id_cargador",
        "col_nombre": "cargador_opcion",
        "label": "Opción de Cargador (ej. CON Cargador y CON Cable):",
        "tipo": "simple"
    },
    "Cajas": {
        "tabla": "caja",
        "pk": "id_caja",
        "col_nombre": "caja_opcion",
        "label": "Opción de Caja (ej. Con caja, Sin caja):",
        "tipo": "simple"
    },
    "Tipos de Almacenamiento (HDD / SSD)": {
        "tabla": "hdd_tipo",
        "pk": "id_hdd_tipo",
        "col_nombre": "hdd_opcion",
        "label": "Tipo de Disco (ej. SSD, M.2 NVMe, HDD):",
        "tipo": "simple"
    },
    "Renovación": {
        "tabla": "renovacion",
        "pk": "id_renovacion",
        "col_nombre": "renovacion_opcion",
        "label": "Opción de Renovación (ej. SÍ, NO):",
        "tipo": "simple"
    },
    "Estatus Celulares": {
        "tabla": "estatus_celulares",
        "pk": "id_estatus_celular",
        "col_nombre": "estatus_celular",
        "label": "Estatus Celular (ej. DISPONIBLE, ASIGNADO, BAJA):",
        "tipo": "simple"
    },
    "Estatus Laptops": {
        "tabla": "estatus_laptops",
        "pk": "id_estatus_laptops",
        "col_nombre": "estatus_laptop",
        "label": "Estatus Laptop (ej. DISPONIBLE, ASIGNADO, EN REPARACIÓN):",
        "tipo": "simple"
    },
    "Estatus CPUs": {
        "tabla": "estatus_cpu",
        "pk": "id_estatus_cpu",
        "col_nombre": "estatus_cpu",
        "label": "Estatus CPU:",
        "tipo": "simple"
    },
    "Estatus Monitores": {
        "tabla": "estatus_monitores",
        "pk": "id_estatus_monitor",
        "col_nombre": "estatus_monitor",
        "label": "Estatus Monitor:",
        "tipo": "simple"
    },
    "Estatus Tablets": {
        "tabla": "estatus_tablets",
        "pk": "id_estatus_tablet",
        "col_nombre": "estatus_tablet",
        "label": "Estatus Tablet:",
        "tipo": "simple"
    },
    "Estatus Empleados": {
        "tabla": "estatus_empleados",
        "pk": "id_estatus_empleado",
        "col_nombre": "estatus_empleado",
        "label": "Estatus de Empleado (ej. ACTIVO, BAJA):",
        "tipo": "simple"
    },
    "Tipos de Correos": {
        "tabla": "tipos_correos_electronicos",
        "pk": "id_tipo_correo",
        "col_nombre": "tipo_correo",
        "label": "Tipo de Correo (ej. Corporativo, Gmail):",
        "tipo": "simple"
    }
}

def consultar_tabla_catalogo(tabla, pk):
    try:
        conn = obtener_conexion()
        df = pd.read_sql(f"SELECT * FROM {tabla} ORDER BY {pk} ASC", conn)
        conn.close()
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

def guardar_registro_simple(tabla, col_nombre, valor):
    conn = obtener_conexion()
    if not conn:
        return False, "No se pudo abrir la conexión a la base de datos."
    cursor = conn.cursor()
    try:
        query = f"INSERT INTO {tabla} ({col_nombre}) VALUES (%s)"
        cursor.execute(query, (str(valor).strip(),))
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def guardar_modelo_celular(marca_modelo, precio, ano_renovacion):
    conn = obtener_conexion()
    if not conn:
        return False, "No se pudo abrir la conexión a la base de datos."
    cursor = conn.cursor()
    try:
        cols = obtener_columnas_tabla(cursor, "modelos_celulares")
        col_ano = next((c for c in ['ano_renovacion', 'anio_renovacion', 'anio', 'ano'] if c in cols), 'ano_renovacion')
        
        query = f"""
            INSERT INTO modelos_celulares (marca_modelo, precio, {col_ano})
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (
            str(marca_modelo).strip(),
            float(precio),
            str(ano_renovacion).strip() if ano_renovacion else None
        ))
        conn.commit()
        conn.close()
        return True, None
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

# ==============================================================================
# RENDER PRINCIPAL
# ==============================================================================
def render():
    aplicar_estilos_pantalla()

    # Header
    st.markdown("### 📁 Gestor de Catálogos (`agrocisa_core`)")
    st.caption("Administración de tablas maestras y opciones de llenado.")

    # Banner persistente de éxito tras el rerun
    if "mensaje_exito_cat" in st.session_state:
        st.success(st.session_state["mensaje_exito_cat"])
        del st.session_state["mensaje_exito_cat"]

    cat_seleccionado = st.selectbox(
        "Selecciona el catálogo que deseas consultar o ampliar:",
        list(CATALOGOS_CONFIG.keys()),
        index=0
    )

    config = CATALOGOS_CONFIG[cat_seleccionado]
    tabla_nom = config["tabla"]
    pk_nom = config["pk"]

    df_cat, err = consultar_tabla_catalogo(tabla_nom, pk_nom)

    st.divider()

    col_tabla, col_form = st.columns([1.3, 1])

    # --------------------------------------------------------------------------
    # COLUMNA IZQUIERDA: VISTA DE LA TABLA
    # --------------------------------------------------------------------------
    with col_tabla:
        st.markdown(f"#### 📋 Tabla `{tabla_nom}`")
        if err:
            st.error(f"Error al cargar el catálogo: {err}")
        elif not df_cat.empty:
            st.dataframe(df_cat, use_container_width=True, hide_index=True)
            st.caption(f"Total de registros: **{len(df_cat)}**")
        else:
            st.info("La tabla no contiene registros actualmente.")

    # --------------------------------------------------------------------------
    # COLUMNA DERECHA: FORMULARIO DE ALTA
    # --------------------------------------------------------------------------
    with col_form:
        st.markdown(f"#### ➕ Agregar a `{cat_seleccionado}`")

        if config["tipo"] == "modelo_celular":
            with st.form("form_alta_modelo_celular"):
                marca_mod_in = st.text_input("Marca / Modelo (ej. iPhone 17 256GB)*:", placeholder="Ej. Samsung Galaxy S26 Ultra 512GB")
                precio_in = st.number_input("Precio ($ MXN):", min_value=0.0, value=0.0, step=500.0)
                ano_in = st.text_input("Año de Renovación (ej. 2026):", value="2026")

                btn_guardar_mod = st.form_submit_button("💾 Guardar Modelo", type="primary", use_container_width=True)

                if btn_guardar_mod:
                    if not marca_mod_in.strip():
                        st.warning("⚠️ El nombre de Marca / Modelo es obligatorio.")
                    else:
                        ok, err_msg = guardar_modelo_celular(marca_mod_in, precio_in, ano_in)
                        if ok:
                            st.session_state["mensaje_exito_cat"] = f"🎉 ¡Modelo `{marca_mod_in.strip()}` registrado exitosamente en el catálogo!"
                            st.rerun()
                        else:
                            st.error(f"⛔ Error al registrar modelo: {err_msg}")

        else:
            col_nombre = config["col_nombre"]
            label_input = config.get("label", f"Nuevo valor para `{col_nombre}`*:")

            with st.form(f"form_alta_cat_{tabla_nom}"):
                valor_in = st.text_input(label_input, placeholder="Ingresa el nuevo registro...")

                btn_guardar_simple = st.form_submit_button(f"💾 Guardar en {cat_seleccionado}", type="primary", use_container_width=True)

                if btn_guardar_simple:
                    if not valor_in.strip():
                        st.warning("⚠️ El campo no puede quedar vacío.")
                    else:
                        ok, err_msg = guardar_registro_simple(tabla_nom, col_nombre, valor_in)
                        if ok:
                            st.session_state["mensaje_exito_cat"] = f"🎉 ¡Registro `{valor_in.strip()}` agregado exitosamente a `{cat_seleccionado}`!"
                            st.rerun()
                        else:
                            st.error(f"⛔ Error al registrar en `{tabla_nom}`: {err_msg}")

render_catalogos = render