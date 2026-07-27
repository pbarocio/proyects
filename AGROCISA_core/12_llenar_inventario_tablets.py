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
df_datos_tablets = pandas.read_excel(
    directorio,
    sheet_name='Inventario Tablet',
    usecols=["No.", "Marca", "Modelo", "IMEI", "No. Serie", "MAC-Address", "Cargador", "Observaciones", "Fecha de entrega", "Precio Equipo"]
).copy()

df_datos_tablets.rename(columns={
    'No' : 'no',
    'Marca' : 'marca',
    'Modelo' : 'modelo',
    'IMEI' : 'imei',
    'No. Serie' : 'numero_serie',
    'MAC-Address' : 'mac_address',
    'Cargador' : 'cargador',
    'Observaciones' : 'observaciones',
    'Fecha de entrega' : 'fecha_entrega',
    'Precio Equipo' : 'precio',
}, inplace=True)

df_datos_empleados = pandas.read_excel(
    directorio_nuevo,
    sheet_name='Asignaciones',
    usecols=['Tablet', 'codigo']
).copy()

# Eliminar nulos y duplicados (solo para el mapeo)
df_datos_empleados = df_datos_empleados.dropna(subset=['codigo']).dropna(subset=['Tablet'])

map_codigo = dict(zip(df_datos_empleados['Tablet'], df_datos_empleados['codigo']))

#LEEMOS LAS TABLAS BÁSICAS
db_name = "agrocisa_core.db"
conexion = sqlite3.connect(db_name)

df_cargadores = pandas.read_sql_query("SELECT id_cargador, cargador_opcion FROM cargadores", conexion)

conexion.commit()
conexion.close()


df_inventario_tablets = df_datos_tablets.merge(
    df_cargadores,
    left_on='cargador',
    right_on='cargador_opcion',
    how='left'
)

df_inventario_tablets["id_condicion"] = int(2)
df_inventario_tablets["comentarios"] =""

columnas_tablets = [
    'marca',
    'modelo',
    'imei',
    'numero_serie',
    'mac_address',
    'id_condicion',
    'id_cargador',
    'precio',
    'comentarios',
    'observaciones',
    'fecha_entrega',
]
df_inventario_tablets = df_inventario_tablets[columnas_tablets]

df_inventario_tablets["id_estatus_tablet"] = int(1)
df_inventario_tablets['codigo_empleado'] = df_datos_tablets["No."].map(map_codigo)

#Escribimos la hoja de empleados
with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_inventario_tablets.to_excel(writer, sheet_name='Inventario Tablets', index=False)

print(f"\"{len(df_inventario_tablets)}\" registros listos para inyectar")

conexion = sqlite3.connect("agrocisa_core.db")

df_inventario_tablets.to_sql(
    name='inventario_tablets',
    con=conexion,
    if_exists='append',
    index=False
)

conexion.commit()
conexion.close()

print(f"Se inyectó correctamente la tabla 'inventario_tablets'")