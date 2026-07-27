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

#LEEMOS LAS TABLAS BÁSICAS
db_name = "agrocisa_core.db"
conexion = sqlite3.connect(db_name)

query_celulares = """
    SELECT fecha_entrega, codigo_empleado, numero, imei FROM inventario_celulares 
    WHERE codigo_empleado IS NOT NULL AND fecha_entrega IS NOT NULL
"""

df_responsivas_celualres = pandas.read_sql_query(query_celulares, conexion)

df_responsivas_celualres.to_sql(
    name='responsivas_celulares',
    con=conexion,
    if_exists='append',
    index=False
)

print(f"Se inyectó correctamente la tabla 'responsivas_celulares'")

query_cpu = """
    SELECT fecha_entrega, codigo_empleado, hostname FROM inventario_cpu
    WHERE codigo_empleado IS NOT NULL AND fecha_entrega IS NOT NULL
"""

df_responsivas_cpu = pandas.read_sql_query(query_cpu, conexion)

df_responsivas_cpu.to_sql(
    name='responsivas_cpu',
    con=conexion,
    if_exists='append',
    index=False
)

print(f"Se inyectó correctamente la tabla 'responsivas_cpu'")

query_laptops = """
    SELECT fecha_entrega, codigo_empleado, numero_serie FROM inventario_laptops
    WHERE codigo_empleado IS NOT NULL AND fecha_entrega IS NOT NULL
"""

df_responsivas_laptops = pandas.read_sql_query(query_laptops, conexion)

df_responsivas_laptops.to_sql(
    name='responsivas_laptops',
    con=conexion,
    if_exists='append',
    index=False
)

print(f"Se inyectó correctamente la tabla 'responsivas_laptops'")

query_monitores = """
    SELECT fecha_entrega, codigo_empleado, numero_serie FROM inventario_monitores
    WHERE codigo_empleado IS NOT NULL AND fecha_entrega IS NOT NULL
"""

df_responsivas_monitores = pandas.read_sql_query(query_monitores, conexion)

df_responsivas_monitores.to_sql(
    name='responsivas_monitores',
    con=conexion,
    if_exists='append',
    index=False
)

print(f"Se inyectó correctamente la tabla 'responsivas_monitores'")

query_tablets = """
    SELECT fecha_entrega, codigo_empleado, numero_serie FROM inventario_tablets
    WHERE codigo_empleado IS NOT NULL AND fecha_entrega IS NOT NULL
"""

df_responsivas_tablets = pandas.read_sql_query(query_tablets, conexion)

df_responsivas_tablets.to_sql(
    name='responsivas_tablets',
    con=conexion,
    if_exists='append',
    index=False
)

print(f"Se inyectó correctamente la tabla 'responsivas_tablets'")

query_delete_fecha_entrega_celuares = """
    ALTER TABLE inventario_celulares 
    DROP COLUMN fecha_entrega;
"""

#pandas.read_sql_query(query_delete_fecha_entrega_celuares, conexion)

conexion.commit()
conexion.close()

#DEFINIMOS LA RUTA DE LOS ARCHIVOS
dir_archivos = Path.home() / "git" / "proyects" / "AGROCISA_core"
#AGREGAMOS LA RUTA COMPLETA DEL ARCHIVO DE EXCEL
directorio_nuevo = dir_archivos / "Estructura BDD.xlsx"
#Escribimos la hoja de empleados
with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_responsivas_celualres.to_excel(writer, sheet_name='Responsiva Celulares', index=False)

print(f"\"{len(df_responsivas_celualres)}\" responsivas celulares listas para inyectar...")

with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_responsivas_cpu.to_excel(writer, sheet_name='Responsivas CPU', index=False)

print(f"\"{len(df_responsivas_cpu)}\" responsivas_cpu listas para inyectar...")

with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_responsivas_laptops.to_excel(writer, sheet_name='Responsivas Laptops', index=False)

print(f"\"{len(df_responsivas_laptops)}\" responsivas_laptops listas para inyectar...")

with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_responsivas_monitores.to_excel(writer, sheet_name='Responsivas Monitores', index=False)

print(f"\"{len(df_responsivas_monitores)}\" responsivas_monitores listas para inyectar...")

with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_responsivas_tablets.to_excel(writer, sheet_name='Responsivas Tablets', index=False)

print(f"\"{len(df_responsivas_laptops)}\" responsivas_tablets listas para inyectar...")