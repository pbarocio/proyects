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
directorio_nuevo = dir_archivos / "Estructura BDD.xlsx"

df_inventario_celulares = pandas.read_excel(directorio_nuevo, sheet_name='Inventario Celulares').copy()

df_inventario_celulares = df_inventario_celulares.dropna(subset=['codigo_empleado']).dropna(subset=['fecha_entrega'])

columnas_responsiva = [
    'fecha_entrega',
    'codigo_empleado',
    'numero',
    'imei',
]

df_responsiva = df_inventario_celulares[columnas_responsiva]

print(f"\"{len(df_responsiva)}\" Responsivas listas para inyectar ...")

#Escribimos la hoja de empleados
with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_responsiva.to_excel(writer, sheet_name='Responsivas Celulares', index=False)

conexion = sqlite3.connect("agrocisa_core.db")

df_responsiva.to_sql(
    name='responsivas_celulares',
    con=conexion,
    if_exists='append',
    index=False
)

conexion.commit()
conexion.close()

print(f"Se exportó correctamente la tabla 'responsivas_celulares'")