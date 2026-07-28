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


#Aquí comienza el código
#DEFINIMOS LA RUTA DE LOS ARCHIVOS
dir_archivos = Path.home() / "git" / "proyects" / "AGROCISA_core"
#AGREGAMOS LA RUTA COMPLETA DEL ARCHIVO DE EXCEL
directorio = dir_archivos / "Directorio 2026-07-21 martes.xlsx"
directorio_nuevo = dir_archivos / "Estructura BDD.xlsx"
#LEEMOS la HOJA qué contiene los datos' SÓLO CON LAS COLUMNAS FUNCIONALES
df_datos_monitores = pandas.read_excel(
    directorio,
    sheet_name='Inventario Monitores',
    usecols=['HOST', 'Condición', 'Costo', 'Observaciones', 'Fecha de entrega', 'Marca-Modelo', 'Número de Serie', 'Resolución', 'Renovar', 'Condiciones']
).copy()

df_datos_monitores.rename(columns={
    'HOST' : 'hostname',
    'Condición' : 'condicion',
    'Costo' : 'precio',
    'Observaciones' : 'comentarios',
    'Fecha de entrega' : 'fecha_entrega',
    'Marca-Modelo' : 'modelo',
    'Número de Serie' : 'numero_serie',
    'Resolución' : 'resolucion',
    'Renovar' : 'renovar',
    'Condiciones' : 'observaciones',
}, inplace=True)

df_datos_empleados = pandas.read_excel(
    directorio_nuevo,
    sheet_name='Asignaciones',
    usecols=['codigo', 'Monitor']
).copy()

# Eliminar nulos y duplicados (solo para el mapeo)
df_datos_empleados = df_datos_empleados.dropna(subset=['codigo']).dropna(subset=['Monitor'])

map_codigo = dict(zip(df_datos_empleados['Monitor'], df_datos_empleados['codigo']))

columnas_monitores = [
    'hostname',
    'modelo',
    'numero_serie',
    'resolucion',
    'condicion',
    'precio',
    'renovar',
    'comentarios',
    'observaciones',
    'fecha_entrega',
]
df_datos_monitores = df_datos_monitores[columnas_monitores]

#LEEMOS LAS TABLAS BÁSICAS
db_name = "agrocisa_core.db"
conexion = sqlite3.connect(db_name)

df_condicion = pandas.read_sql_query("SELECT id_condicion, condicion_opcion FROM condicion", conexion)
df_renovacion = pandas.read_sql_query("SELECT id_renovacion, renovacion_opcion FROM renovacion", conexion)

conexion.commit()
conexion.close()

df_inventario_monitores = df_datos_monitores.merge(
    df_condicion,
    left_on='condicion',
    right_on='condicion_opcion',
    how='left'
).merge(
    df_renovacion,
    left_on='renovar',
    right_on='renovacion_opcion',
    how='left'
)

df_inventario_monitores['marca'] = ""
df_inventario_monitores['codigo_empleado'] = df_datos_monitores["hostname"].map(map_codigo)
df_inventario_monitores["id_estatus_monitor"] = 1

df_inventario_monitores['fecha_entrega'] = df_inventario_monitores['fecha_entrega'].apply(normalizar_fecha_iso)

columnas_monitores = [
    'hostname',
    'marca',
    'modelo',
    'numero_serie',
    'resolucion',
    'precio',
    'comentarios',
    'observaciones',
    'id_condicion',
    'id_renovacion',
    'fecha_entrega',
    'codigo_empleado',
    'id_estatus_monitor',
]
df_inventario_monitores = df_inventario_monitores[columnas_monitores]

#Escribimos la hoja de empleados
with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_inventario_monitores.to_excel(writer, sheet_name='Inventario Monitores', index=False)

print(f"\"{len(df_datos_monitores)}\" registros listos para inyectar")

conexion = sqlite3.connect("agrocisa_core.db")

df_inventario_monitores.to_sql(
    name='inventario_monitores',
    con=conexion,
    if_exists='append',
    index=False
)

conexion.commit()
conexion.close()

print(f"Se inyectó correctamente la tabla 'inventario_monitores'")