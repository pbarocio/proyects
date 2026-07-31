import pandas
from openpyxl import load_workbook
from pathlib import Path
import unicodedata
import re
from db_config import get_files_path, get_engine
from sqlalchemy import text

# Mostrar todas las filas
pandas.set_option('display.max_rows', None)

# Mostrar todas las columnas
pandas.set_option('display.max_columns', None)

# Mostrar texto completo (sin truncar)
pandas.set_option('display.max_colwidth', None)

def normalizar_cadena (cadena):
    if not isinstance(cadena, str):
        return ""
    
    texto_nfkd = unicodedata.normalize('NFD', cadena)
    texto_limpio = "".join([c for c in texto_nfkd if unicodedata.category(c) != 'Mn'])

    texto_limpio = re.sub(r'[^\w\sÑñáéíóúÁÉÍÓÚüÜ.-]', '', texto_limpio) #Elminar carcteres no permitidos (#, $, *, ...) ..
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio) #Colapsa espacios múltiples a uno solo
    texto_limpio = texto_limpio.strip()
    
    return texto_limpio

def quitar_caracteres_no_validos(texto):
    if not isinstance(texto, str):
        return ""
    
    texto_limpio = re.sub(r'[^\w\sÑñáéíóúÁÉÍÓÚüÜ.-]', '', texto_limpio) #Elminar carcteres no permitidos (#, $, *, ...) ..
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio) #Colapsa espacios múltiples a uno solo
    texto_limpio = texto_limpio.strip()
    
    return texto_limpio

def limpiar_telefono(valor):
    if pandas.isna(valor) or valor is None: # 1. Manejo de nulos o celdas vacías
        return None
    texto = str(valor).split(".")[0].strip() # 2. Si es float/int, quitamos el punto decimal convirtiendo primero a string

    digitos = "".join(filter(str.isdigit, texto))  # 3. Nos quedamos solo con los caracteres numéricos

    if not digitos or len(digitos) != 10: # 4. Validamos que no esté vacío Y que sean exactamente 10 dígitos
        return None  # O puedes regresar None para marcarlo como inválido/vacío

    return digitos

files = get_files_path()
directorio = files['directorio']
directorio_nuevo = files['directorio_nuevo']

#LEEMOS la HOJA 'EMPLEADOS' SÓLO CON LAS COLUMNAS FUNCIONALES
df_empleados = pandas.read_excel(
    directorio, 
    sheet_name='Empleados',
    usecols=["codigo","nombre","apellido_paterno","apellido_materno","estatus"]
    ).copy()
#FILTRAMOS SOLAMENTE LOS EMPLEADOS ACTIVOS
df_empleados = df_empleados[df_empleados["estatus"] == "ACTIVO"]
#ELMINAMOS LA COLUMNA ESTATUS, YA NO SE NECESITA
df_empleados.drop('estatus', axis=1, inplace=True)
#CREAMOS LA COLUMNA (SERIE) NOMBRES NORMALIZADOS
df_empleados["nombre_normalizado"] = (
    df_empleados["nombre"].astype(str).fillna("").apply(normalizar_cadena) + " " +
    df_empleados["apellido_paterno"].astype(str).fillna("").apply(normalizar_cadena) + " " +
    df_empleados["apellido_materno"].astype(str).fillna("").apply(normalizar_cadena)
).str.lower()
#SÍ QUEREMOS PONER NOMBRE NORMALIZADO AL PRINCIPIO TENEMOS QUÉ QUITAR df_empleados["nombre_normalizado"] -> df_empleados = (...)
#df_empleados_activos.insert(1, "nombre_normalizado", empleados__nombre_normalizado)
#MOSTRAMOS LA CANTIDAD DE ELEMENTOS DE EMPLEADOS
print(f"'Empleados tiene' \"{len(df_empleados)}\" elementos...")
#LEEMOS LA HOJA ASIGNACIONES COMPLETA
df_asignaciones = pandas.read_excel(
    directorio,
    sheet_name="Asignaciones"
    ).copy()

#MOSTRAMOS EL NUMERO DE ELEMENTOS EN ASIGNACIONES
print(f"Asignaciones tiene: {len(df_asignaciones)} elementos...")
#NORMALIZAMOS LOS NOMBRES
df_asignaciones["nombre_normalizado"] = (
    df_asignaciones["Nombre"].astype(str).fillna("").apply(normalizar_cadena)
).str.lower()
#ELIMINAMOS EL NOMBRE COMPLETO CON ACENTOS
df_asignaciones.drop('Nombre', axis=1, inplace=True)
#HACEMOS EL MERGE ENTRE LAS DOS TABLAS
df_asignaciones_completa = df_asignaciones.merge(
    df_empleados,
    on='nombre_normalizado',
    how="left"
)

#LEEMOS LA TABLA DE SUCURSALES
engine = get_engine()

df_sucursales = pandas.read_sql_query("SELECT id_sucursal, nombre_sucursal FROM sucursales", con=engine)
df_departamentos = pandas.read_sql_query("SELECT id_departamento, nombre_departamento FROM departamentos", con=engine)
df_puestos = pandas.read_sql_query("SELECT id_puesto, nombre_puesto FROM puestos", con=engine)

#HACER MERGE CON SUCURSALES
df_asignaciones_sucursales = df_asignaciones_completa.merge(
    df_sucursales,
    left_on='Sucursal',
    right_on = 'nombre_sucursal',
    how='left'
)

#MERGE CON DEPARTAMENTOS
df_asignaciones_departamentos = df_asignaciones_sucursales.merge(
    df_departamentos,
    left_on='Departamento',
    right_on = 'nombre_departamento',
    how='left'
)

#MERGE CON PUESTOS
df_asignaciones_puestos = df_asignaciones_departamentos.merge(
    df_puestos,
    left_on='Puesto',
    right_on = 'nombre_puesto',
    how='left'
)
#REORDENAMOS LAS COLUMNAS
columnas_asignaciones_puestos = [
    'codigo',
    'nombre',
    'apellido_paterno',
    'apellido_materno',
    'nombre_normalizado',
    'id_sucursal',
    'nombre_sucursal',
    'Sucursal',
    'id_departamento',
    'nombre_departamento',
    'Departamento',
    'id_puesto',
    'nombre_puesto',
    'Puesto',
    'Correo Gmail',
    'Contraseña Gmail',
    'Correo Institucional',
    'Contraseña Institucional',
    'Celular',
    'Laptop',
    'CPU',
    'Monitor',
    'Tablet',
    'Zona',
]
df_asignaciones_puestos = df_asignaciones_puestos[columnas_asignaciones_puestos]

#CONVERTIMOS LA COLUMNA CELULAR A STRING PARA USARLA CON VARCHAR
df_asignaciones_puestos["Celular"] = df_asignaciones_puestos["Celular"].apply(limpiar_telefono)
#CREAMOS EL NUEVO ARCHIVO PARA EL MAPEO DE TABLAS
df_asignaciones_puestos.to_excel(directorio_nuevo, sheet_name="Asignaciones", index=False)

#ELIMINAMOS LOS EMPLEADOS SIN CÓDIGO Y CREAMOS EL DATAFRAME DE EMPLEADOS
df_empleados = df_asignaciones_puestos[
    df_asignaciones_puestos["codigo"].notna() & (df_asignaciones_puestos["codigo"] != '')
]
#CONVERTIMOS LOS TELÉFONOS A STRING PARA EL VARCHAR
df_empleados["Celular"] = df_empleados["Celular"].apply(limpiar_telefono)
#DEFINIMOS LA COLUMNA PARA LA TABLA EMPLEADOS
columnas_empleados = [
    'codigo',
    'apellido_paterno',
    'apellido_materno',
    'nombre',
    'id_sucursal',
    'id_departamento',
    'id_puesto',
    'Celular',
    'Zona',
]
df_empleados = df_empleados[columnas_empleados]

df_empleados.rename(columns={
    'Celular': 'numero_telefono',
    'Zona' : 'zona',
    },inplace=True)

df_empleados["id_estatus_empleado"] = 1

df_empleados["nombre"] = df_empleados["nombre"].str.title()
df_empleados["apellido_paterno"] = df_empleados["apellido_paterno"].str.title()
df_empleados["apellido_materno"] = df_empleados["apellido_materno"].str.title()

#Escribimos la hoja de empleados
with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_empleados.to_excel(writer, sheet_name='Empleados', index=False)
    
print(f"\"{len(df_empleados)}\" empleados listos para exportar...")

#USAMOS ENGINE PARA INYECTAR LA BDD CON ALCHEMY
engine = get_engine()

with engine.begin() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

    df_empleados.to_sql(
        name='empleados',
        con=conn,
        if_exists='append',
        index=False
    )

    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

print(f"Se inyectó correctamente la tabla 'empleados'")