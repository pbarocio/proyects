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
df_datos_cpu = pandas.read_excel(
    directorio, 
    sheet_name='Inventario CPU',
    usecols=["HOST", "Condición", "Costo", "Observaciones", "Fecha de entrega", "Sistema Operativo", "Procesador", "RAM", "Chipset", "Almacenamiento", "Tipo HD", "Renovar", "Componentes", "MAC LAN", "MAC WIFI", "Fecha Mantenimiento"]
    ).copy()

df_datos_cpu.rename(columns={
    'HOST' : 'hostname',
    'Condición' : 'condicion',
    'Costo' : 'precio',
    'Observaciones' : 'observaciones',
    'Fecha de entrega' : 'fecha_entrega',
    'Sistema Operativo' : 'sistema_operativo',
    'Procesador' : 'procesador',
    'RAM' : 'memoria_ram',
    "Chipset" : 'motherboard',
    'Almacenamiento' : 'almacenamiento',
    'Tipo HD' : 'tipo_hdd',
    'Renovar' : 'renovar',
    'Componentes' : 'comentarios',
    'MAC LAN' : 'mac_address_lan',
    'MAC WIFI' : 'mac_address_wifi',
    'Fecha Mantenimiento' : 'fecha_mantenimiento'
}, inplace=True)

df_datos_empleados = pandas.read_excel(
    directorio_nuevo, 
    sheet_name='Asignaciones',
    usecols=["CPU", "codigo"]
    ).copy()

# Eliminar nulos y duplicados (solo para el mapeo)
df_datos_empleados = df_datos_empleados.dropna(subset=['codigo']).dropna(subset=['CPU'])

#Añadimos la columna de estatus
df_datos_cpu["id_estatus_cpu"] = 1
#MAPEAMOS EL CÓDIGO DE EMPLEADO PARA AÑADIRLO A LOS DATOS DEL CPU
map_codigo = dict(zip(df_datos_empleados['CPU'], df_datos_empleados['codigo']))
df_datos_cpu["codigo_empleado"] = df_datos_cpu['hostname'].map(map_codigo)
df_datos_cpu["datos_memoria_ram"] = ""
df_datos_cpu["datos_almacenamiento"] = ""

columnas_cpu = [
    'hostname',
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
    'condicion',
    'observaciones',
    'precio',
    'renovar',
    'comentarios',
    'fecha_mantenimiento',
    'fecha_entrega',
    'id_estatus_cpu',
    'codigo_empleado',
]
df_datos_cpu = df_datos_cpu[columnas_cpu]

#LEEMOS LAS TABLAS BÁSICAS
db_name = "agrocisa_core.db"
conexion = sqlite3.connect(db_name)

df_hdd_tipo = pandas.read_sql_query("SELECT id_hdd_tipo, hdd_opcion FROM hdd_tipo", conexion)
df_condicion = pandas.read_sql_query("SELECT id_condicion, condicion_opcion FROM condicion", conexion)
df_renovacion = pandas.read_sql_query("SELECT id_renovacion, renovacion_opcion FROM renovacion", conexion)

conexion.commit()
conexion.close()

df_inventario_cpu = df_datos_cpu.merge(
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
)


columnas_cpu = [
    'hostname',
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
    'id_condicion',
    'precio',
    'id_renovacion',
    'comentarios',
    'observaciones',
    'fecha_mantenimiento',
    'fecha_entrega',
    'id_estatus_cpu',
    'codigo_empleado',
]
df_inventario_cpu = df_inventario_cpu[columnas_cpu]


#Escribimos la hoja de empleados
with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_inventario_cpu.to_excel(writer, sheet_name='Inventario CPU', index=False)
    
print(f"\"{len(df_datos_cpu)}\" CPU's listos para exportar ...")

conexion = sqlite3.connect("agrocisa_core.db")

df_inventario_cpu.to_sql(
    name='inventario_cpu',
    con=conexion,
    if_exists='append',
    index=False
)

conexion.commit()
conexion.close()

print(f"Se importó correctamente la tabla ")