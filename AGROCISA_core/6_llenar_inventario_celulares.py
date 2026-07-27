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
    'fecha_entrega' : pandas.to_datetime(df_datos_celulares["Fecha de entrega"], errors='coerce') ,
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
    'codigo_empleado',
]
df_inventaio_celulares = df_inventaio_celulares[columnas_inventario_celulares]

df_inventaio_celulares["id_estatus_celular"] = 1

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
