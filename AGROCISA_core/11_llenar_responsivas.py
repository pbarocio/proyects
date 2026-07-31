import pandas
from openpyxl import load_workbook
from pathlib import Path
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

#LEEMOS LAS TABLAS BÁSICAS
engine = get_engine()

query_celulares = """
    SELECT fecha_entrega, codigo_empleado, numero, imei FROM inventario_celulares_2026
    WHERE codigo_empleado IS NOT NULL AND fecha_entrega IS NOT NULL
"""

df_responsivas_celualres = pandas.read_sql_query(query_celulares, con=engine)
df_responsivas_celualres['fecha_entrega'] = df_responsivas_celualres['fecha_entrega'].apply(normalizar_fecha_iso)

df_responsivas_celualres.to_sql(
    name='responsivas_celulares',
    con=engine,
    if_exists='append',
    index=False
)

print(f"Se inyectó correctamente la tabla 'responsivas_celulares'")

query_cpu = """
    SELECT id_cpu, fecha_entrega, codigo_empleado FROM inventario_cpu
    WHERE codigo_empleado IS NOT NULL AND fecha_entrega IS NOT NULL
"""

df_responsivas_cpu = pandas.read_sql_query(query_cpu, con=engine)
df_responsivas_cpu['fecha_entrega'] = df_responsivas_cpu['fecha_entrega'].apply(normalizar_fecha_iso)

df_responsivas_cpu.to_sql(
    name='responsivas_cpu',
    con=engine,
    if_exists='append',
    index=False
)

print(f"Se inyectó correctamente la tabla 'responsivas_cpu'")

query_laptops = """
    SELECT fecha_entrega, codigo_empleado, numero_serie FROM inventario_laptops
    WHERE codigo_empleado IS NOT NULL AND fecha_entrega IS NOT NULL
"""

df_responsivas_laptops = pandas.read_sql_query(query_laptops, con=engine)
df_responsivas_laptops['fecha_entrega'] = df_responsivas_laptops['fecha_entrega'].apply(normalizar_fecha_iso)

df_responsivas_laptops.to_sql(
    name='responsivas_laptops',
    con=engine,
    if_exists='append',
    index=False
)

print(f"Se inyectó correctamente la tabla 'responsivas_laptops'")

query_monitores = """
    SELECT fecha_entrega, codigo_empleado, numero_serie FROM inventario_monitores
    WHERE codigo_empleado IS NOT NULL AND fecha_entrega IS NOT NULL
"""

df_responsivas_monitores = pandas.read_sql_query(query_monitores, con=engine)
df_responsivas_monitores['fecha_entrega'] = df_responsivas_monitores['fecha_entrega'].apply(normalizar_fecha_iso)

df_responsivas_monitores.to_sql(
    name='responsivas_monitores',
    con=engine,
    if_exists='append',
    index=False
)

print(f"Se inyectó correctamente la tabla 'responsivas_monitores'")

query_tablets = """
    SELECT fecha_entrega, codigo_empleado, numero_serie FROM inventario_tablets
    WHERE codigo_empleado IS NOT NULL AND fecha_entrega IS NOT NULL
"""

df_responsivas_tablets = pandas.read_sql_query(query_tablets, con=engine)
df_responsivas_tablets['fecha_entrega'] = df_responsivas_tablets['fecha_entrega'].apply(normalizar_fecha_iso)

df_responsivas_tablets.to_sql(
    name='responsivas_tablets',
    con=engine,
    if_exists='append',
    index=False
)

print(f"Se inyectó correctamente la tabla 'responsivas_tablets'")

#DEFINIMOS LA RUTA DE LOS ARCHIVOS
files = get_files_path()
directorio = files['directorio']
directorio_nuevo = files['directorio_nuevo']
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

print(f"\"{len(df_responsivas_tablets)}\" responsivas_tablets listas para inyectar...")