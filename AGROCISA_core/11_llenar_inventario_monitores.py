import pandas
from openpyxl import load_workbook
from pathlib import Path
import numpy as np
import sqlite3

# Mostrar todas las filas
pandas.set_option('display.max_rows', None)

# Mostrar todas las columnas
pandas.set_option('display.max_columns', None)

# Mostrar texto completo (sin truncar)
pandas.set_option('display.max_colwidth', None)

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
    'Marca-Modelo' : 'marca_modelo',
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
    'marca_modelo',
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

columnas_monitores = [
    'hostname',
    'marca_modelo',
    'numero_serie',
    'resolucion',
    'id_condicion',
    'precio',
    'id_renovacion',
    'comentarios',
    'observaciones',
    'fecha_entrega',
]
df_inventario_monitores = df_inventario_monitores[columnas_monitores]

df_inventario_monitores["id_estatus_monitor"] = 1
df_inventario_monitores['codigo_empleado'] = df_datos_monitores["hostname"].map(map_codigo)

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