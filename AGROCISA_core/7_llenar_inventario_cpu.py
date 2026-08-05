import pandas
from openpyxl import load_workbook
from pathlib import Path
import re
import numpy as np
from db_config import get_files_path, get_engine

# Mostrar todas las filas
pandas.set_option('display.max_rows', None)

# Mostrar todas las columnas
pandas.set_option('display.max_columns', None)

# Mostrar texto completo (sin truncar)
pandas.set_option('display.max_colwidth', None)

def limpiar_codigo (valor):
    if pandas.isna(valor) or valor is None:
        return None
    
    texto = str(valor).split('.')[0].strip()
    
    # Sacamos los números limpios
    digitos = ''.join(filter(str.isdigit, str(valor)))
    # Si la celda estaba vacía o con un espacio blanco, 'digitos' vale ''
    if not digitos:
        return None
        
    return str(digitos)

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
files = get_files_path()
directorio = files['directorio']
directorio_nuevo = files['directorio_nuevo']
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
    'Observaciones' : 'comentarios',
    'Fecha de entrega' : 'fecha_entrega',
    'Sistema Operativo' : 'sistema_operativo',
    'Procesador' : 'procesador',
    'RAM' : 'memoria_ram',
    "Chipset" : 'motherboard',
    'Almacenamiento' : 'almacenamiento',
    'Tipo HD' : 'tipo_hdd',
    'Renovar' : 'renovar',
    'Componentes' : 'observaciones',
    'MAC LAN' : 'mac_address_lan',
    'MAC WIFI' : 'mac_address_wlan',
    'Fecha Mantenimiento' : 'fecha_mantenimiento'
}, inplace=True)

df_datos_empleados = pandas.read_excel(
    directorio_nuevo, 
    sheet_name='Asignaciones',
    usecols=["CPU", "codigo"],
    dtype={"codigo": str},
    ).copy()

df_datos_empleados["codigo"] = df_datos_empleados["codigo"].apply(limpiar_codigo)

# Eliminar nulos y duplicados (solo para el mapeo)
df_datos_empleados = df_datos_empleados.dropna(subset=['codigo']).dropna(subset=['CPU'])

#Añadimos la columna de estatus
df_datos_cpu["id_estatus_cpu"] = 1
#MAPEAMOS EL CÓDIGO DE EMPLEADO PARA AÑADIRLO A LOS DATOS DEL CPU
map_codigo = dict(zip(df_datos_empleados['CPU'], df_datos_empleados['codigo']))
df_datos_cpu["codigo_empleado"] = df_datos_cpu['hostname'].map(map_codigo)

#INICIALIZAMOS LOS NUEVOS CAMPOS PARA LA BDD
df_datos_cpu["marca"] = None
df_datos_cpu["modelo"] = None
df_datos_cpu["numero_serie"] = None
df_datos_cpu["datos_memoria_ram"] = None
df_datos_cpu["datos_almacenamiento"] = None

columnas_cpu = [
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
    'mac_address_wlan',
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
engine = get_engine()

df_hdd_tipo = pandas.read_sql_query("SELECT id_hdd_tipo, hdd_opcion FROM hdd_tipo", con=engine)
df_condicion = pandas.read_sql_query("SELECT id_condicion, condicion_opcion FROM condicion", con=engine)
df_renovacion = pandas.read_sql_query("SELECT id_renovacion, renovacion_opcion FROM renovacion", con=engine)

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


df_inventario_cpu['fecha_entrega'] = df_inventario_cpu['fecha_entrega'].apply(normalizar_fecha_iso)
df_inventario_cpu['fecha_mantenimiento'] = df_inventario_cpu['fecha_mantenimiento'].apply(normalizar_fecha_iso)

df_inventario_cpu['fecha_entrega'] = df_inventario_cpu['fecha_entrega'].where(df_inventario_cpu['fecha_entrega'].notna(), None)
df_inventario_cpu['fecha_mantenimiento'] = df_inventario_cpu['fecha_mantenimiento'].where(df_inventario_cpu['fecha_mantenimiento'].notna(), None)

columnas_cpu = [
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
    'mac_address_wlan',
    'precio',
    'comentarios',
    'observaciones',
    'fecha_mantenimiento',
    'id_condicion',
    'id_renovacion',
    'fecha_entrega',
    'codigo_empleado',
    'id_estatus_cpu',
]
df_inventario_cpu = df_inventario_cpu[columnas_cpu]


#Escribimos la hoja de empleados
with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_inventario_cpu.to_excel(writer, sheet_name='Inventario CPU', index=False)
    
print(f"\"{len(df_datos_cpu)}\" CPU's listos para exportar ...")

df_inventario_cpu.to_sql(
    name='inventario_cpu',
    con=engine,
    if_exists='append',
    index=False
)

print(f"Se importó correctamente la tabla 'inventario_cpu'")