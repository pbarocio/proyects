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
df_datos_laptops = pandas.read_excel(
    directorio,
    sheet_name='Inventario Laptop',
    usecols=["Nombre de Host", "Costo", "Condicion", "Cargador", "Comentarios", "Fecha de entrega", "Marca", "Modelo", "No. Serie", "Sistema Operativo", "Procesador", 
             "RAM", "Chipset", "Almacenamiento", "Tipo HD", "Renovar", "MAC LAN", "MAC WIFI"]
    ).copy()

df_datos_empleados = pandas.read_excel(
    directorio_nuevo,
    sheet_name='Asignaciones',
    usecols=["Laptop", "codigo"]
).copy()

# Eliminar nulos y duplicados (solo para el mapeo)
df_datos_empleados = df_datos_empleados.dropna(subset=['codigo']).dropna(subset=['Laptop'])

map_codigo = dict(zip(df_datos_empleados["Laptop"], df_datos_empleados["codigo"]))

df_datos_laptops.rename(columns={
    'Nombre de Host' : 'hostname',
    'Costo' : 'precio',
    'Condicion' : 'condicion',
    'Cargador' : 'cargador',
    'Comentarios' : 'comentarios',
    'Fecha de entrega' : 'fecha_entrega',
    'Marca' : 'marca',
    'Modelo' : 'modelo',
    'No. Serie' : 'numero_serie',
    'Sistema Operativo' : 'sistema_operativo',
    'Procesador' : 'procesador',
    'RAM' : 'memoria_ram',
    'Chipset' : 'motherboard',
    'Almacenamiento' : 'almacenamiento',
    'Tipo HD' : 'tipo_hdd',
    'Renovar' : 'renovar',
    'MAC LAN' : 'mac_address_lan',
    'MAC WIFI' : 'mac_address_wifi',
}, inplace=True)

df_datos_laptops["datos_memoria_ram"] = ""
df_datos_laptops["datos_almacenamiento"] = ""
df_datos_laptops["observaciones"] = ""

columnas_laptops = [
    'hostname',
    'marca',
    'modelo',
    'numero_serie',
    'procesador',
    'datos_memoria_ram',
    'memoria_ram',
    'tipo_hdd',
    'datos_almacenamiento',
    'almacenamiento',
    'motherboard',
    'sistema_operativo',
    'mac_address_lan',
    'mac_address_wifi',
    'cargador',
    'condicion',
    'precio',
    'renovar',
    'comentarios',
    'observaciones',
    'fecha_entrega',
]

df_datos_laptops = df_datos_laptops[columnas_laptops]

df_datos_laptops["codigo_empleado"] = df_datos_laptops["hostname"].map(map_codigo)

#LEEMOS LAS TABLAS BÁSICAS
db_name = "agrocisa_core.db"
conexion = sqlite3.connect(db_name)

df_hdd_tipo = pandas.read_sql_query("SELECT id_hdd_tipo, hdd_opcion FROM hdd_tipo", conexion)
df_condicion = pandas.read_sql_query("SELECT id_condicion, condicion_opcion FROM condicion", conexion)
df_renovacion = pandas.read_sql_query("SELECT id_renovacion, renovacion_opcion FROM renovacion", conexion)
df_cargadores = pandas.read_sql_query("SELECT id_cargador, cargador_opcion FROM cargadores", conexion)

conexion.commit()
conexion.close()

df_inventario_laptops = df_datos_laptops.merge(
    df_hdd_tipo,
    left_on='tipo_hdd',
    right_on='hdd_opcion',
    how='left'
).merge(
    df_condicion,
    left_on='condicion',
    right_on='condicion_opcion',
    how='left'
).merge(
    df_renovacion,
    left_on='renovar',
    right_on='renovacion_opcion',
    how='left'
).merge(
    df_cargadores,
    left_on='cargador',
    right_on='cargador_opcion',
    how='left'
)

df_datos_laptops["id_estatus_laptops"] = 1

columnas_laptops = [
    'hostname',
    'marca',
    'modelo',
    'numero_serie',
    'procesador',
    'datos_memoria_ram',
    'memoria_ram',
    'id_hdd_tipo',
    'datos_almacenamiento',
    'almacenamiento',
    'motherboard',
    'sistema_operativo',
    'mac_address_lan',
    'mac_address_wifi',
    'id_cargador',
    'id_condicion',
    'precio',
    'id_renovacion',
    'comentarios',
    'observaciones',
    'fecha_entrega',
    'codigo_empleado'
]

df_inventario_laptops = df_inventario_laptops[columnas_laptops]

#Escribimos la hoja de empleados
with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_inventario_laptops.to_excel(writer, sheet_name='Inventario Laptops', index=False)

print(f"\"{len(df_datos_laptops)}\" registros listos para inyectar")

conexion = sqlite3.connect("agrocisa_core.db")

df_inventario_laptops.to_sql(
    name='inventario_laptops',
    con=conexion,
    if_exists='append',
    index=False
)

conexion.commit()
conexion.close()

print(f"Se importó correctamente la tabla ")