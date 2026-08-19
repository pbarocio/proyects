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

# ==============================================================================
# CONFIGURACIÓN EXACTA DE CATÁLOGOS (ESQUEMA MARIADB REAL)
# ==============================================================================
CATALOGOS_CONFIG = {
    "Condición de Equipos": {
        "tabla": "condicion",
        "pk": "id_condicion",
        "col_nombre": "condicion_opcion",
        "label": "Nueva opción de Condición (ej. Excelente, Dañado):",
        "tipo": "simple"
    },
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
    "Tipo de Contrato Empleados": {
        "tabla": "tipo_contrato_empleados",
        "pk": "id_tipo_contrato",
        "col_nombre": "tipo_contrato",
        "label": "Tipo de Contrato (ej. INTERNO, EXTERNO):",
        "tipo": "simple"
    },
    "Cargadores": {
        "tabla": "cargadores",
        "pk": "id_cargador",
        "col_nombre": "cargador_opcion",
        "label": "Opción de Cargador (ej. CON Cargador Original y CON Cable):",
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
        "label": "Tipo de Disco (ej. SSD, M2VMe, HDD):",
        "tipo": "simple"
    },
    "Renovación": {
        "tabla": "renovacion",
        "pk": "id_renovacion",
        "col_nombre": "renovacion_opcion",
        "label": "Opción de Renovación (ej. SÍ, NO):",
        "tipo": "simple"
    },
    "Estatus Líneas Telefónicas": {
        "tabla": "estatus_linea_telefonica",
        "pk": "id_estatus_linea",
        "col_nombre": "estatus_linea",
        "label": "Estatus de Línea (ej. ASIGNADO, DISPONIBLE, V.I.P.):",
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
        "label": "Estatus CPU (ej. DISPONIBLE, ASIGNADO, BAJA):",
        "tipo": "simple"
    },
    "Estatus Monitores": {
        "tabla": "estatus_monitores",
        "pk": "id_estatus_monitor",
        "col_nombre": "estatus_monitor",
        "label": "Estatus Monitor (ej. DISPONIBLE, ASIGNADO):",
        "tipo": "simple"
    },
    "Estatus Tablets": {
        "tabla": "estatus_tablets",
        "pk": "id_estatus_tablet",
        "col_nombre": "estatus_tablet",
        "label": "Estatus Tablet (ej. DISPONIBLE, ASIGNADO):",
        "tipo": "simple"
    },
    "Estatus Empleados": {
        "tabla": "estatus_empleados",
        "pk": "id_estatus_empleado",
        "col_nombre": "estatus_empleado",
        "label": "Estatus de Empleado (ej. ACTIVO, INACTIVO, BAJA):",
        "tipo": "simple"
    },
    "Estatus Correos Electrónicos": {
        "tabla": "estatus_correos_electronicos",
        "pk": "id_estatus_correo",
        "col_nombre": "estatus_correo",
        "label": "Estatus de Cuenta de Correo (ej. ACTIVO, INACTIVO):",
        "tipo": "simple"
    },
    "Tipos de Correos": {
        "tabla": "tipos_correos_electronicos",
        "pk": "id_tipo_correo",
        "col_nombre": "tipo_correo",
        "label": "Tipo de Correo (ej. CORPORATIVO, GMAIL):",
        "tipo": "simple"
    },
    "Estatus Responsivas": {
        "tabla": "estatus_responsivas",
        "pk": "id_estatus_responsiva",
        "col_nombre": "estatus_responsiva",
        "label": "Estatus de Responsiva (ej. ACTIVO, INACTIVO):",
        "tipo": "simple"
    }
}

# ==============================================================================
# OPERACIONES BDD
# ==============================================================================
def consultar_tabla_catalogo(tabla, pk):
    try:
        conn = obtener_conexion()
        if not conn:
            return pd.DataFrame(), "No hay conexión con la base de datos."
        df = pd.read_sql(f"SELECT * FROM {tabla} ORDER BY {pk} ASC", conn)
        conn.close()
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

def existe_registro_simple(tabla, col_nombre, valor):
    """Verifica si ya existe el valor para evitar error de UNIQUE en MariaDB."""
    try:
        conn = obtener_conexion()
        if not conn:
            return False
        cursor = conn.cursor()
        query = f"SELECT COUNT(*) FROM {tabla} WHERE LOWER(TRIM({col_nombre})) = LOWER(TRIM(%s))"
        cursor.execute(query, (str(valor).strip(),))
        cnt = cursor.fetchone()[0]
        conn.close()
        return cnt > 0
    except Exception:
        return False

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
        cursor.execute("SELECT COUNT(*) FROM modelos_celulares WHERE LOWER(TRIM(marca_modelo)) = LOWER(TRIM(%s))", (str(marca_modelo).strip(),))
        if cursor.fetchone()[0] > 0:
            conn.close()
            return False, f"El modelo '{marca_modelo.strip()}' ya existe en el catálogo."

        query = """
            INSERT INTO modelos_celulares (marca_modelo, precio, ano_renovacion)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (
            str(marca_modelo).strip(),
            str(int(float(precio))),
            str(ano_renovacion).strip() if ano_renovacion else "2026"
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
    st.caption("Administración directa de tablas maestras de la base de datos.")

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
            st.error(f"Error al cargar el catálogo `{tabla_nom}`: {err}")
        elif not df_cat.empty:
            st.dataframe(df_cat, use_container_width=True, hide_index=True)
            st.caption(f"Total de registros en base de datos: **{len(df_cat)}**")
        else:
            st.info(f"La tabla `{tabla_nom}` no contiene registros actualmente.")

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

                btn_guardar_mod = st.form_submit_button(f"💾 Guardar en {cat_seleccionado}", type="primary", use_container_width=True)

                if btn_guardar_mod:
                    val_clean = marca_mod_in.strip()
                    if not val_clean:
                        st.warning("⚠️ El nombre de Marca / Modelo es obligatorio.")
                    else:
                        ok, err_msg = guardar_modelo_celular(val_clean, precio_in, ano_in)
                        if ok:
                            st.session_state["mensaje_exito_cat"] = f"🎉 ¡Modelo `{val_clean}` registrado exitosamente en `{tabla_nom}`!"
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
                    val_clean = valor_in.strip()
                    if not val_clean:
                        st.warning("⚠️ El campo no puede quedar vacío.")
                    elif existe_registro_simple(tabla_nom, col_nombre, val_clean):
                        st.warning(f"⚠️ El registro `{val_clean}` ya existe en el catálogo `{cat_seleccionado}`.")
                    else:
                        ok, err_msg = guardar_registro_simple(tabla_nom, col_nombre, val_clean)
                        if ok:
                            st.session_state["mensaje_exito_cat"] = f"🎉 ¡Registro `{val_clean}` agregado exitosamente a `{tabla_nom}`!"
                            st.rerun()
                        else:
                            st.error(f"⛔ Error al registrar en `{tabla_nom}`: {err_msg}")

render_catalogos = render