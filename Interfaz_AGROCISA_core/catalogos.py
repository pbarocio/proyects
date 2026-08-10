import streamlit as st
import mysql.connector
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

def obtener_conexion():
    """Conexión a MariaDB Local."""
    return mysql.connector.connect(
        host=str(os.getenv("LOCAL_HOST")),
        user=str(os.getenv("LOCAL_DB_USER")),
        password=str(os.getenv("LOCAL_DB_PASSWORD")),
        database=str(os.getenv("LOCAL_DATABASE")),
    )

def obtener_tabla_completa(tabla):
    """Jala todas las columnas del catálogo para visualización completa."""
    try:
        conn = obtener_conexion()
        query = f"SELECT * FROM {tabla}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"⚠️ Error al cargar tabla {tabla}: {e}")
        return pd.DataFrame()

def agregar_registro_catalogo(tabla, columnas, valores):
    """Ejecuta un INSERT dinámico con N columnas según la tabla."""
    try:
        conn = obtener_conexion()
        cursor = conn.cursor()
        cols_str = ", ".join(columnas)
        placeholders = ", ".join(["%s"] * len(valores))
        query = f"INSERT IGNORE INTO {tabla} ({cols_str}) VALUES ({placeholders})"
        cursor.execute(query, valores)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"⚠️ Error al guardar en {tabla}: {e}")
        return False

def render():
    st.subheader("🗂️ Gestor de Catálogos (`agrocisa_core`)")
    st.write("Administración de tablas maestras y opciones de llenado.")

    # MAPEO DE TABLAS
    catalogos_map = {
        "Modelos Celulares": "modelos_celulares",
        "Planes Telcel": "planes_telcel_2026",
        "Sucursales": "sucursales",
        "Departamentos": "departamentos",
        "Puestos": "puestos",
        "Tipo de Contrato": "tipo_contrato_empleados",
        "Estatus Empleados": "estatus_empleados",
        "Caja": "caja",
        "Condición": "condicion",
        "Tipos de HDD": "hdd_tipo",
        "Renovación": "renovacion",
        "Cargadores": "cargadores",
        "Tipos de Correo": "tipos_correos_electronicos",
        "Estatus Correo": "estatus_correos_electronicos",
        "Estatus Celulares": "estatus_celulares",
        "Estatus Línea": "estatus_linea_telefonica",
        "Estatus CPU": "estatus_cpu",
        "Estatus Laptops": "estatus_laptops",
        "Estatus Monitores": "estatus_monitores",
        "Estatus Tablets": "estatus_tablets",
    }

    cat_seleccionado = st.selectbox("Selecciona el catálogo que deseas consultar o ampliar:", list(catalogos_map.keys()))
    tabla = catalogos_map[cat_seleccionado]

    df_catalogo = obtener_tabla_completa(tabla)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"### 📋 Tabla `{tabla}`")
        if not df_catalogo.empty:
            st.dataframe(df_catalogo, use_container_width=True, hide_index=True)
            st.caption(f"Total de registros: **{len(df_catalogo)}**")
        else:
            st.info("Catálogo vacío o no inicializado.")

    with col2:
        st.markdown(f"### ➕ Agregar a `{cat_seleccionado}`")
        
        # FORMULARIO ESPECIAL: Modelos Celulares
        if tabla == "modelos_celulares":
            with st.form(key="form_modelos_celulares"):
                marca_modelo = st.text_input("Marca / Modelo (ej. iPhone 17 256GB):")
                precio = st.number_input("Precio ($ MXN):", min_value=0.0, step=500.0)
                ano_renovacion = st.text_input("Año de Renovación (ej. 2026):", value="2026")
                btn_guardar = st.form_submit_button("💾 Guardar Modelo", type="primary")

                if btn_guardar:
                    if marca_modelo.strip():
                        if agregar_registro_catalogo(
                            tabla, 
                            ["marca_modelo", "precio", "ano_renovacion"], 
                            [marca_modelo.strip(), str(precio), ano_renovacion.strip()]
                        ):
                            st.success(f"¡Modelo '{marca_modelo}' guardado correctamente!")
                            st.rerun()
                    else:
                        st.warning("Escribe una marca/modelo válido.")

        # FORMULARIO ESPECIAL: Planes Telcel
        elif tabla == "planes_telcel_2026":
            with st.form(key="form_planes_telcel"):
                nombre_plan = st.text_input("Nombre del Plan (ej. Plan 4):")
                mensualidad = st.number_input("Mensualidad ($ MXN):", min_value=0.0, step=50.0)
                datos_incluidos = st.number_input("GB Incluidos:", min_value=0.0, step=0.5)
                btn_guardar = st.form_submit_button("💾 Guardar Plan", type="primary")

                if btn_guardar:
                    if nombre_plan.strip():
                        if agregar_registro_catalogo(
                            tabla, 
                            ["nombre_plan", "mensualidad", "datos_incluidos"], 
                            [nombre_plan.strip(), mensualidad, datos_incluidos]
                        ):
                            st.success(f"¡Plan '{nombre_plan}' guardado correctamente!")
                            st.rerun()
                    else:
                        st.warning("Escribe un nombre de plan válido.")

        # FORMULARIO GENÉRICO: Catálogos de 1 sola columna
        else:
            # Mapeo de columna de texto según la tabla
            columnas_unicas = {
                "sucursales": "nombre_sucursal",
                "departamentos": "nombre_departamento",
                "puestos": "nombre_puesto",
                "tipo_contrato_empleados": "tipo_contrato",
                "estatus_empleados": "estatus_empleado",
                "caja": "caja_opcion",
                "condicion": "condicion_opcion",
                "hdd_tipo": "hdd_opcion",
                "renovacion": "renovacion_opcion",
                "cargadores": "cargador_opcion",
                "tipos_correos_electronicos": "tipo_correo",
                "estatus_correos_electronicos": "estatus_correo",
                "estatus_celulares": "estatus_celular",
                "estatus_linea_telefonica": "estatus_linea",
                "estatus_cpu": "estatus_cpu",
                "estatus_laptops": "estatus_laptop",
                "estatus_monitores": "estatus_monitor",
                "estatus_tablets": "estatus_tablet",
            }
            col_target = columnas_unicas.get(tabla, "nombre")
            
            with st.form(key=f"form_{tabla}"):
                nuevo_valor = st.text_input(f"Nuevo registro para {cat_seleccionado}:")
                btn_guardar = st.form_submit_button("💾 Guardar en BDD", type="primary")

                if btn_guardar:
                    if nuevo_valor.strip():
                        if agregar_registro_catalogo(tabla, [col_target], [nuevo_valor.strip()]):
                            st.success(f"¡'{nuevo_valor}' agregado correctamente!")
                            st.rerun()
                    else:
                        st.warning("Escribe una opción válida.")