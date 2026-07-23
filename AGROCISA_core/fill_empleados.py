import pandas as pd
import re
import unicodedata
from pathlib import Path
import sqlite3

archivo = Path.home() / "git" / "proyects" / "AGROCISA_core" /"Archivos_Responsivas" / "Directorio.xlsx"
print (archivo)

excel_nuevo = Path.home() / "git" / "proyects" / "AGROCISA_core" /"Archivos_Responsivas" / "Directorio_Con_Codigo_Y_Nombres.xlsx"
print(excel_nuevo)

# 1. FUNCIÓN MÁGICA PARA QUITAR ACENTOS Y NORMALIZAR
def quitar_acentos(texto):
    if not isinstance(texto, str):
        return ""
    texto_nfkd = unicodedata.normalize('NFD', texto)
    return "".join([c for c in texto_nfkd if unicodedata.category(c) != 'Mn'])

def limpiar_caracteres_raros(texto):
    if not isinstance(texto, str):
        return texto
    
    # 2. O limpiamos eliminando cualquier caracter que no sea letra, número o espacio válido
    # Conservando Ñ, ñ, acentos y espacios
    texto_limpio = re.sub(r'[^\w\sÑñáéíóúÁÉÍÓÚüÜ.-]', '', texto)
    
    return texto_limpio.strip()

def normalizar_cadena(texto):
    if not isinstance(texto, str):
        return ""
    # 1. Quitar acentos
    texto_nfkd = unicodedata.normalize('NFD', texto)
    texto = "".join([c for c in texto_nfkd if unicodedata.category(c) != 'Mn'])
    # 2. Quitar caracteres raros
    texto = re.sub(r'[^\w\sÑñ.-]', '', texto)
    # 3. COLAPSAR MÚLTIPLES ESPACIOS A UNO SOLO Y HACE STRIP (¡AQUÍ ESTABA EL DUENDE!)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto.lower()

def limpiar_telefono(valor):
        if pd.isna(valor):
            return None
        # Sacamos los números limpios
        digitos = ''.join(filter(str.isdigit, str(valor)))
        # Si la celda estaba vacía o con un espacio blanco, 'digitos' vale ''
        if not digitos:
            return None
            
        return int(digitos)
    
# --- PARTE 1: LA FUENTE DE LA VERDAD (EMPLEADOS) ---
df_emp = pd.read_excel(archivo, sheet_name='Empleados')
activos = df_emp[df_emp['estatus'] == 'ACTIVO'].copy()

# Armamos la llave limpia
nombres_emp = (
    activos['nombre'].astype(str).apply(limpiar_caracteres_raros).apply(normalizar_cadena).str.strip() + " " +
    activos['apellido_paterno'].astype(str).apply(limpiar_caracteres_raros).apply(normalizar_cadena).str.strip() + " " +
    activos['apellido_materno'].astype(str).apply(limpiar_caracteres_raros).apply(normalizar_cadena).str.strip()
).str.lower()

print("=== nombres_emp (primeros 10) ===")
for i in range(min(10, len(nombres_emp))):
    print(f"{i}: '{nombres_emp.iloc[i]}'")
    

activos['llave_limpia'] = nombres_emp.apply(quitar_acentos)

print("=== llave_limpia (primeros 10) ===")
for i in range(min(10, len(activos['llave_limpia']))):
    print(f"{i}: '{activos['llave_limpia'].iloc[i]}'")

# DICCIONARIOS DE BÚSQUEDA (Uno para cada campo que queremos jalar del sistema)
mapa_codigo = dict(zip(activos['llave_limpia'], activos['codigo']))
mapa_nombre = dict(zip(activos['llave_limpia'], activos['nombre']))
mapa_paterno = dict(zip(activos['llave_limpia'], activos['apellido_paterno']))
mapa_materno = dict(zip(activos['llave_limpia'], activos['apellido_materno']))


# --- PARTE 2: EL CRUCE CON EL DIRECTORIO ---
df_dir = pd.read_excel(archivo, sheet_name='Asignaciones')

# Limpiamos la columna 'Nombre' del Directorio para comparar
nombre_dir_limpio = df_dir['Nombre'].astype(str).str.strip().str.lower().apply(quitar_acentos).apply(normalizar_cadena).apply(limpiar_caracteres_raros)

# INYECTAMOS LOS DATOS DEL SISTEMA USANDO .map()
df_dir['codigo'] = nombre_dir_limpio.map(mapa_codigo)
df_dir['nombre_sist'] = nombre_dir_limpio.map(mapa_nombre)
df_dir['apellido_paterno'] = nombre_dir_limpio.map(mapa_paterno)
df_dir['apellido_materno'] = nombre_dir_limpio.map(mapa_materno)

# --- PARTE 3: FILTRAR ACTIVOS Y LIMPIAR ESTRUCTURA ---
# Nos quedamos solo con los que hicieron match activo
asignaciones_activos = df_dir.dropna(subset=['codigo']).copy()

# Convertimos el código a entero
asignaciones_activos['codigo'] = asignaciones_activos['codigo'].astype(int)

# ACOMODAMOS LAS COLUMNAS EN EL ORDEN PERFECTO
# Ponemos: codigo, nombre_sist, apellido_paterno, apellido_materno, y luego el resto (correos, teléfonos, etc.)
cols_sistema = ['codigo', 'nombre_sist', 'apellido_paterno', 'apellido_materno']
cols_resto = [c for c in asignaciones_activos.columns if c not in cols_sistema and c != 'Nombre']

asignaciones_final = asignaciones_activos[cols_sistema + cols_resto]

# Renombramos 'nombre_sist' a 'nombre' para que quede chulo
asignaciones_final = asignaciones_final.rename(columns={'nombre_sist': 'nombre'})


# --- PARTE 4: GUARDAR EL RESULTADO ---
asignaciones_final.to_excel(excel_nuevo, index=False)
#########AQUÍ COMIENZA EL PEDO DE LA TABLA

# 1. Filtramos el DataFrame 'asignaciones_final' para dejar las 5 columnas
# (Asegúrate de que la columna del teléfono sea numérico INTEGER para que haga match con tu FK)
empleados_tabla = asignaciones_final[[
    'codigo', 
    'apellido_paterno', 
    'apellido_materno', 
    'nombre', 
    'Celular'
]].copy()

# 2. Renombramos únicamente la columna 'telefono' a 'numero_telefono'
# para que coincida exactito con tu DDL
empleados_tabla = empleados_tabla.rename(columns={'Celular': 'numero_telefono'})
#empleados_tabla['numero_telefono'] = empleados_tabla['numero_telefono'].apply(limpiar_telefono)
# 2. Convertimos al entero de Pandas que SI permite nulos (Int64)
empleados_tabla['numero_telefono'] = empleados_tabla['numero_telefono'].astype('Int64')
# 3. Inyección limpia a agrocisa_core.db usando append
conexion = sqlite3.connect("agrocisa_core.db")

# 1. Jalamos los catálogos con sus IDs que ya se poblaron en fill_tables.py
df_suc = pd.read_sql_query("SELECT id_sucursal, nombre_sucursal FROM sucursales", conexion)
df_dep = pd.read_sql_query("SELECT id_departamento, nombre_departamento FROM departamentos", conexion)
df_pue = pd.read_sql_query("SELECT id_puesto, nombre_puesto FROM puestos", conexion)

# 2. Creamos los mapas de conversión (Texto -> ID)
map_sucursal = dict(zip(df_suc['nombre_sucursal'].str.upper().str.strip(), df_suc['id_sucursal']))
map_depto = dict(zip(df_dep['nombre_departamento'].str.upper().str.strip(), df_dep['id_departamento']))
map_puesto = dict(zip(df_pue['nombre_puesto'].str.upper().str.strip(), df_pue['id_puesto']))

# 3. Preparación de la tabla empleados
empleados_tabla = asignaciones_final[[
    'codigo', 
    'apellido_paterno', 
    'apellido_materno', 
    'nombre', 
    'Sucursal',
    'Departamento',
    'Puesto',
    'Celular'
]].copy()

# 4. Inyectamos los IDs numéricos (Foreign Keys) en lugar del texto
empleados_tabla['id_sucursal'] = empleados_tabla['Sucursal'].astype(str).str.upper().str.strip().map(map_sucursal)
empleados_tabla['id_departamento'] = empleados_tabla['Departamento'].astype(str).str.upper().str.strip().map(map_depto)
empleados_tabla['id_puesto'] = empleados_tabla['Puesto'].astype(str).str.upper().str.strip().map(map_puesto)

# 5. Limpieza de columnas y tipos de datos
empleados_tabla = empleados_tabla.rename(columns={'Celular': 'numero_telefono'})
empleados_tabla['numero_telefono'] = empleados_tabla['numero_telefono'].astype('Int64')

# Seleccionamos únicamente las columnas que van exactas con tu DDL
cols_db = [
    'codigo', 
    'apellido_paterno', 
    'apellido_materno', 
    'nombre', 
    'id_sucursal',
    'id_departamento',
    'id_puesto',
    'numero_telefono',
]
empleados_tabla = empleados_tabla[cols_db]

# 6. Mantenemos el candado anti-duplicados
empleados_tabla = empleados_tabla.sort_values(by='numero_telefono', na_position='last')
empleados_tabla = empleados_tabla.drop_duplicates(subset=['codigo'], keep='first')

# 7. Inyección limpia a la BDD
empleados_tabla.to_sql(
    name='empleados',
    con=conexion,
    if_exists='append',
    index=False
)

print("¡A huevo! Tabla 'empleados' inyectada con todas sus Foreign Keys normalizadas.")

# 1. Del DataFrame de asignaciones, sacamos el mapa {numero_telefono: codigo_empleado}
# Filtrando únicamente los que sí tienen número de celular y código de empleado válido
lineas_mapeo = asignaciones_final[['Celular', 'codigo']].dropna().copy()
lineas_mapeo['Celular'] = lineas_mapeo['Celular'].astype('Int64')
lineas_mapeo['codigo'] = lineas_mapeo['codigo'].astype(int)

# Quitamos duplicados por si un mismo número venía dos veces por error
#lineas_mapeo = lineas_mapeo.drop_duplicates(subset=['Celular'])

# 2. Ejecutamos un UPDATE masivo en la tabla 'lineas_telcel' para asociar el codigo_empleado
cursor = conexion.cursor()

datos_update = [
    (row['codigo'], row['Celular']) 
    for _, row in lineas_mapeo.iterrows()
]

# Actualizamos la columna codigo_empleado haciendo match por el numero de teléfono
cursor.executemany("""
    UPDATE lineas_telefonicas
    SET codigo_empleado = ? 
    WHERE numero = ?;
""", datos_update)

conexion.commit()
conexion.close()

print(f"¡A huevo! Se asociaron exitosamente {len(datos_update)} líneas con su respectivo código de empleado en 'lineas_telcel'.")


conexion.close()

print("=== ¡PROCESO CONCLUIDO CON ÉXITO, CARNAL! ===")
print(f"Total registros matheados y procesados: {len(asignaciones_final)}")
print("\nMuestra de las primeras columnas resultantes:")
print(asignaciones_final[['codigo', 'nombre', 'apellido_paterno', 'apellido_materno']].head(5))