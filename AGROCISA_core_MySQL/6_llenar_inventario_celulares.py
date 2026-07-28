import pandas
from openpyxl import load_workbook
from pathlib import Path
import numpy as np
import re
import sqlite3

# Mostrar todas las filas
pandas.set_option('display.max_rows', None)

# Mostrar todas las columnas
pandas.set_option('display.max_columns', None)

# Mostrar texto completo (sin truncar)
pandas.set_option('display.max_colwidth', None)

def normalizar_fecha_iso(val):
    # Si es nulo o 'NULL', regresamos None para que SQL guarde un NULL real
    if pandas.isna(val) or val is None or str(val).strip() in ['', 'NULL', 'None', 'nan', 'NaT']:
        return None
    
    val_str = str(val).lower().strip()
    
    # 1. Corregir dedazos comunes de los meses
    correcciones = {
        'fecbrero': 'febrero',
        'setiembre': 'septiembre'
    }
    for error, correcto in correcciones.items():
        val_str = val_str.replace(error, correcto)
        
    meses_map = {
        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
    }
    
    # 2. Si viene en español largo: "jueves 18 de diciembre de 2025" -> 2025-12-18
    match_texto = re.search(r'(\d{1,2})\s+de\s+([a-zA-Z]+)\s+de\s+(\d{4})', val_str)
    if match_texto:
        dia = match_texto.group(1).zfill(2)
        mes_nombre = match_texto.group(2)
        anio = match_texto.group(3)
        if mes_nombre in meses_map:
            return f"{anio}-{meses_map[mes_nombre]}-{dia}"

    # 3. Si viene como "28/01/2025" -> 2025-01-28
    match_slash = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', val_str)
    if match_slash:
        dia = match_slash.group(1).zfill(2)
        mes = match_slash.group(2).zfill(2)
        anio = match_slash.group(3)
        return f"{anio}-{mes}-{dia}"

    # 4. Si viene como ISO con hora: "2026-05-04 00:00:00" -> 2026-05-04
    try:
        dt = pandas.to_datetime(val_str, errors='coerce')
        if not pandas.isna(dt):
            return dt.strftime('%Y-%m-%d')
    except Exception:
        pass
        
    return None

def limpiar_entero (valor):
    if pandas.isna(valor):
        return None
    if isinstance(valor, float):
        valor = int(valor)
    # Sacamos los números limpios
    digitos = ''.join(filter(str.isdigit, str(valor)))
    # Si la celda estaba vacía o con un espacio blanco, 'digitos' vale ''
    if not digitos:
        return None
        
    return int(digitos)

def limpiar_moneda(value):
    if value is None or str(value).strip() in ('N/A', ''):
        return None
    clean_val = str(value).replace('$', '').replace(',', '').strip()
    return float(clean_val)

def limpiar_gb(value):
    if value is None or str(value).strip() in ('N/A', ''):
        return None
    clean_val = str(value).replace(',', '.').strip()
    return float(clean_val)

#pandas.to_datetime(df_datos_celulares["Fecha de entrega"], errors='coerce') ,

#Aquí comienza el código
#DEFINIMOS LA RUTA DE LOS ARCHIVOS
dir_archivos = Path.home() / "git" / "proyects" / "AGROCISA_core"
#AGREGAMOS LA RUTA COMPLETA DEL ARCHIVO DE EXCEL
directorio = dir_archivos / "Directorio 2026-07-21 martes.xlsx"
directorio_nuevo = dir_archivos / "Estructura BDD.xlsx"
#LEEMOS la HOJA qué contiene los datos' SÓLO CON LAS COLUMNAS FUNCIONALES
df_datos_celulares = pandas.read_excel(
    directorio, 
    sheet_name='Inventario Celulares',
    usecols=["Renovación", "Número", "Marca-Modelo", "IMEI", "Número de Serie", "MacAddress", "Condición", "Cargador", "Caja", "Fecha de entrega", "Comentarios", "Observaciones", "Precio"]
    ).copy()

df_datos_asignaciones = pandas.read_excel(
    directorio_nuevo, 
    sheet_name='Asignaciones',
    usecols=["Celular", "codigo"]
    ).copy()

#LIMPIAMOS LOS NÚMEROS DE TELÉFONO DE ASIGNACIONES
df_datos_asignaciones["Celular"] = df_datos_asignaciones["Celular"].apply(limpiar_entero)


# Eliminar nulos y duplicados (solo para el mapeo)
df_asignaciones_unicos = df_datos_asignaciones.dropna(subset=['Celular']).drop_duplicates(subset=['Celular'], keep='first')

df_celulares = pandas.DataFrame({
    'numero_renovacion' : df_datos_celulares["Renovación"].apply(limpiar_entero),
    'numero' : df_datos_celulares["Número"].apply(limpiar_entero),
    'imei' : df_datos_celulares["IMEI"].apply(limpiar_entero),
    'numero_serie': df_datos_celulares["Número de Serie"],
    'mac_address' : df_datos_celulares["MacAddress"],
    'fecha_entrega' : df_datos_celulares["Fecha de entrega"] ,
    'comentarios': df_datos_celulares["Comentarios"],
    'observaciones' : df_datos_celulares["Observaciones"],
    'marca_modelo_df' : df_datos_celulares["Marca-Modelo"],
    'precio_df' : df_datos_celulares["Precio"].apply(limpiar_moneda),
    'condicion' : df_datos_celulares["Condición"],
    'cargador' : df_datos_celulares["Cargador"],
    'caja' : df_datos_celulares["Caja"]
})

# Crear diccionario de mapeo
map_codigo = dict(zip(df_asignaciones_unicos['Celular'], df_asignaciones_unicos['codigo']))
# --- APLICAR MAPAS (SIN DUPLICAR FILAS) ---
df_celulares['codigo_empleado'] = df_celulares['numero'].map(map_codigo)
    
print(f"\"{len(df_datos_celulares)}\" equipos listos para importar...")
print(f"Hay \"{len(map_codigo)}\" códigos...")
print(f"Al final inventario tiene \"{df_celulares["codigo_empleado"].count()}\" códigos asignados...")

sin_codigo = df_celulares[df_celulares['numero'].notna() & df_celulares['codigo_empleado'].isna()]

# Exportar los que no tienen código
sin_codigo = df_celulares[df_celulares['numero'].notna() & df_celulares['codigo_empleado'].isna()]
#Escribimos la hoja de empleados
with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    sin_codigo.to_excel(writer, sheet_name='Celulares sin codigo', index=False)

#LEEMOS LA TABLA DE estatus_correos_electronicos
db_name = "agrocisa_core.db"
conexion = sqlite3.connect(db_name)

df_equipos_2026 = pandas.read_sql_query("SELECT id_equipo, marca_modelo, precio FROM equipos_2026", conexion)
df_condicion = pandas.read_sql_query("SELECT id_condicion, condicion_opcion FROM condicion", conexion)
df_cargador = pandas.read_sql_query("SELECT id_cargador, cargador_opcion FROM cargadores", conexion)
df_caja = pandas.read_sql_query("SELECT id_caja, caja_opcion FROM caja", conexion)

conexion.commit()
conexion.close()

df_inventaio_celulares = df_celulares.merge(
    df_equipos_2026,
    left_on='marca_modelo_df',
    right_on='marca_modelo',
    how='left'
).merge(
    df_condicion,
    left_on='condicion',
    right_on='condicion_opcion',
    how='left'
).merge(
    df_caja,
    left_on='caja',
    right_on='caja_opcion',
    how='left'
)

df_inventaio_celulares["id_cargador"] = 7

columnas_inventario_celulares = [
    'numero_renovacion',
    'imei',
    'numero_serie',
    'mac_address',
    'fecha_entrega',
    'comentarios',
    'observaciones',
    'numero',
    'id_equipo',
    'id_condicion',
    'id_cargador',
    'id_caja',
    'codigo_empleado',
]
df_inventaio_celulares = df_inventaio_celulares[columnas_inventario_celulares]

#Escribimos la hoja de empleados
with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_inventaio_celulares.to_excel(writer, sheet_name='Inventario Celulares', index=False)

df_inventaio_celulares["id_estatus_celular"] = 1

df_inventaio_celulares["fecha_entrega"] = df_inventaio_celulares['fecha_entrega'].apply(normalizar_fecha_iso)

columnas_inventario_celulares = [
    'numero_renovacion',
    'imei',
    'numero_serie',
    'mac_address',
    'comentarios',
    'observaciones',
    'numero',
    'id_equipo',
    'id_condicion',
    'id_cargador',
    'id_caja',
    'fecha_entrega',
    'codigo_empleado',
    'id_estatus_celular',
]
df_inventaio_celulares = df_inventaio_celulares[columnas_inventario_celulares]

conexion = sqlite3.connect("agrocisa_core.db")

df_inventaio_celulares.to_sql(
    name='inventario_celulares',
    con=conexion,
    if_exists='append',
    index=False
)

conexion.commit()
conexion.close()

print(f"Se importó correctamente la tabla inventario_celulares")
