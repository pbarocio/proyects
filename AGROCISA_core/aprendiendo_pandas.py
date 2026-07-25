import pandas
from pathlib import Path
import unicodedata
import re
import sqlite3

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

#Aquí comienza el código
#DEFINIMOS LA RUTA DE LOS ARCHIVOS
dir_archivos = Path.home() / "git" / "proyects" / "AGROCISA_core"
#AGREGAMOS LA RUTA COMPLETA DEL ARCHIVO DE EXCEL
directorio = dir_archivos / "Directorio 2026-07-21 martes.xlsx"
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
#REORDENAMOS LAS COLUMNAS
columnas_asignaciones_completa = [
    'codigo',
    'nombre',
    'apellido_paterno',
    'apellido_materno',
    'nombre_normalizado',
    'Sucursal',
    'Departamento',
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
    'KNOX'
]
df_asignaciones_completa = df_asignaciones_completa[columnas_asignaciones_completa]
#Escribimos el Resultado
archivo_asignaciones_completo = dir_archivos / "Asignaciones_completo.xlsx"
df_asignaciones_completa.to_excel(archivo_asignaciones_completo, sheet_name="Nuevo_asignaciones")

#LEEMOS LA TABLA DE SUCURSALES
db_name = "agrocisa_core.db"
conexion = sqlite3.connect(db_name)
cursor = conexion.cursor()

df_sucursales = pandas.read_sql_query("SELECT id_sucursal, nombre_sucursal FROM sucursales", conexion)
df_departamentos = pandas.read_sql_query("SELECT id_departamento, nombre_departamento FROM departamentos", conexion)
df_puestos = pandas.read_sql_query("SELECT id_puesto, nombre_puesto FROM puestos", conexion)

conexion.commit()
conexion.close()

#HACER MERGE CON SUCURSALES
df_asignaciones_sucursales = df_asignaciones_completa.merge(
    df_sucursales,
    left_on='Sucursal',
    right_on = 'nombre_sucursal',
    how='left'
)
#REORDENAMOS LAS COLUMNAS
columnas_asignaciones_sucursal = [
    'codigo',
    'nombre',
    'apellido_paterno',
    'apellido_materno',
    'nombre_normalizado',
    'id_sucursal',
    'nombre_sucursal',
    'Sucursal',
    'Departamento',
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
    'KNOX'
]
df_asignaciones_sucursales = df_asignaciones_sucursales[columnas_asignaciones_sucursal]
#Escribimos el Resultado
archivo_asignaciones_sucursales = dir_archivos / "Asignaciones_sucursales.xlsx"
df_asignaciones_sucursales.to_excel(archivo_asignaciones_sucursales, sheet_name="Con Sucursal")
#MERGE CON DEPARTAMENTOS
df_asignaciones_departamentos = df_asignaciones_sucursales.merge(
    df_departamentos,
    left_on='Departamento',
    right_on = 'nombre_departamento',
    how='left'
)
#REORDENAMOS LAS COLUMNAS
columnas_asignaciones_departamentos = [
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
    'KNOX'
]
df_asignaciones_departamentos = df_asignaciones_departamentos[columnas_asignaciones_departamentos]

archivo_asignaciones_departamentos = dir_archivos / "Asignaciones_departamentos.xlsx"
df_asignaciones_departamentos.to_excel(archivo_asignaciones_departamentos, sheet_name="Con Departamentos")

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
    'KNOX'
]
df_asignaciones_puestos = df_asignaciones_puestos[columnas_asignaciones_puestos]

archivo_asignaciones_puestos = dir_archivos / "Asignaciones_puestos.xlsx"
df_asignaciones_puestos.to_excel(archivo_asignaciones_puestos, sheet_name="Con Puestos")