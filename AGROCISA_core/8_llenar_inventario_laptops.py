import pandas
from openpyxl import load_workbook
from pathlib import Path
import numpy as np
import re
from db_config import get_files_path, get_engine

# Mostrar todas las filas
pandas.set_option('display.max_rows', None)

# Mostrar todas las columnas
pandas.set_option('display.max_columns', None)

# Mostrar texto completo (sin truncar)
pandas.set_option('display.max_colwidth', None)

def normalizar_fecha_iso(val):
    # 1. Si es nulo o vacío, devolvemos None para que pase a MariaDB como NULL
    if (
        pandas.isna(val)
        or val is None
        or str(val).strip() in ['', 'NULL', 'None', 'nan', 'NaT']
    ):
        return None

    val_str = str(val).lower().strip()

    # 2. Corregir errores comunes de captura en los meses
    correcciones = {'fecbrero': 'febrero', 'setiembre': 'septiembre'}
    for error, correcto in correcciones.items():
        val_str = val_str.replace(error, correcto)

    meses_map = {
        'enero': '01',
        'febrero': '02',
        'marzo': '03',
        'abril': '04',
        'mayo': '05',
        'junio': '06',
        'julio': '07',
        'agosto': '08',
        'septiembre': '09',
        'octubre': '10',
        'noviembre': '11',
        'diciembre': '12',
    }

    # 3. Fecha en texto largo (ej: "viernes 05 de junio de 2024" o "martes 23 de julio 2024")
    # El (?:de\s+)? hace que el segundo "de" sea opcional
    match_texto = re.search(
        r'(\d{1,2})\s+de\s+([a-zA-Z]+)\s+(?:de\s+)?(\d{4})', val_str
    )
    if match_texto:
        dia = match_texto.group(1).zfill(2)
        mes_nombre = match_texto.group(2)
        anio = match_texto.group(3)
        if mes_nombre in meses_map:
            return f"{anio}-{meses_map[mes_nombre]}-{dia}"

    # 4. Formato con diagonales (ej: "28/01/2025" -> "2025-01-28")
    match_slash = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', val_str)
    if match_slash:
        dia = match_slash.group(1).zfill(2)
        mes = match_slash.group(2).zfill(2)
        anio = match_slash.group(3)
        return f"{anio}-{mes}-{dia}"

    # 5. Formato ISO / Datetime estándar de Pandas (ej: "2025-07-05 00:00:00" -> "2025-07-05")
    try:
        dt = pandas.to_datetime(val_str, errors='coerce')
        if not pandas.isna(dt):
            return dt.strftime('%Y-%m-%d')
    except Exception:
        pass

    return None


#Aquí comienza el código
#DEFINIMOS LA RUTA DE LOS ARCHIVOS
#DEFINIMOS LA RUTA DE LOS ARCHIVOS
files = get_files_path()
directorio = files['directorio']
directorio_nuevo = files['directorio_nuevo']
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
engine = get_engine()

df_hdd_tipo = pandas.read_sql_query("SELECT id_hdd_tipo, hdd_opcion FROM hdd_tipo", con=engine)
df_condicion = pandas.read_sql_query("SELECT id_condicion, condicion_opcion FROM condicion", con=engine)
df_renovacion = pandas.read_sql_query("SELECT id_renovacion, renovacion_opcion FROM renovacion", con=engine)
df_cargadores = pandas.read_sql_query("SELECT id_cargador, cargador_opcion FROM cargadores", con=engine)

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

df_inventario_laptops["id_estatus_laptops"] = 1
df_inventario_laptops['fecha_entrega'] = df_inventario_laptops['fecha_entrega'].apply(normalizar_fecha_iso)
df_inventario_laptops['fecha_entrega'] = df_inventario_laptops['fecha_entrega'].where(df_inventario_laptops['fecha_entrega'].notna(), None)

columnas_laptops = [
    'hostname',
    'marca',
    'modelo',
    'numero_serie',
    'procesador',
    'datos_memoria_ram',
    'memoria_ram',
    'datos_almacenamiento',
    'almacenamiento',
    'motherboard',
    'sistema_operativo',
    'mac_address_lan',
    'mac_address_wifi',
    'precio',
    'comentarios',
    'observaciones',
    'id_hdd_tipo',
    'id_cargador',
    'id_condicion',
    'id_renovacion',
    'fecha_entrega',
    'codigo_empleado',
    'id_estatus_laptops',
]
df_inventario_laptops = df_inventario_laptops[columnas_laptops]

#Escribimos la hoja de empleados
with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_inventario_laptops.to_excel(writer, sheet_name='Inventario Laptops', index=False)

print(f"\"{len(df_datos_laptops)}\" registros listos para inyectar")

df_inventario_laptops.to_sql(
    name='inventario_laptops',
    con=engine,
    if_exists='append',
    index=False
)

print(f"Se importó correctamente la tabla ")