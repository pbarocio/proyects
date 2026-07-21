import pandas as pd
import unicodedata
from pathlib import Path
import sqlite3

archivo = Path.home() / "git" / "pablo-contexto" / "Archivos_Responsivas" / "Directorio.xlsx"
print (archivo)

excel_nuevo = Path.home() / "git" / "pablo-contexto" / "Archivos_Responsivas" / "Directorio_Con_Codigo_Y_Nombres.xlsx"
print(excel_nuevo)

# 1. FUNCIÓN MÁGICA PARA QUITAR ACENTOS Y NORMALIZAR
def quitar_acentos(texto):
    if not isinstance(texto, str):
        return ""
    texto_nfkd = unicodedata.normalize('NFD', texto)
    return "".join([c for c in texto_nfkd if unicodedata.category(c) != 'Mn'])

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
    activos['nombre'].astype(str).str.strip() + " " +
    activos['apellido_paterno'].astype(str).str.strip() + " " +
    activos['apellido_materno'].astype(str).str.strip()
).str.lower()

activos['llave_limpia'] = nombres_emp.apply(quitar_acentos)

# DICCIONARIOS DE BÚSQUEDA (Uno para cada campo que queremos jalar del sistema)
mapa_codigo = dict(zip(activos['llave_limpia'], activos['codigo']))
mapa_nombre = dict(zip(activos['llave_limpia'], activos['nombre']))
mapa_paterno = dict(zip(activos['llave_limpia'], activos['apellido_paterno']))
mapa_materno = dict(zip(activos['llave_limpia'], activos['apellido_materno']))


# --- PARTE 2: EL CRUCE CON EL DIRECTORIO ---
df_dir = pd.read_excel(archivo, sheet_name='Directorio')

# Limpiamos la columna 'Nombre' del Directorio para comparar
nombre_dir_limpio = df_dir['Nombre'].astype(str).str.strip().str.lower().apply(quitar_acentos)

# INYECTAMOS LOS DATOS DEL SISTEMA USANDO .map()
df_dir['codigo'] = nombre_dir_limpio.map(mapa_codigo)
df_dir['nombre_sist'] = nombre_dir_limpio.map(mapa_nombre)
df_dir['apellido_paterno'] = nombre_dir_limpio.map(mapa_paterno)
df_dir['apellido_materno'] = nombre_dir_limpio.map(mapa_materno)

# --- PARTE 3: FILTRAR ACTIVOS Y LIMPIAR ESTRUCTURA ---
# Nos quedamos solo con los que hicieron match activo
directorio_activos = df_dir.dropna(subset=['codigo']).copy()

# Convertimos el código a entero
directorio_activos['codigo'] = directorio_activos['codigo'].astype(int)

# ACOMODAMOS LAS COLUMNAS EN EL ORDEN PERFECTO
# Ponemos: codigo, nombre_sist, apellido_paterno, apellido_materno, y luego el resto (correos, teléfonos, etc.)
cols_sistema = ['codigo', 'nombre_sist', 'apellido_paterno', 'apellido_materno']
cols_resto = [c for c in directorio_activos.columns if c not in cols_sistema and c != 'Nombre']

directorio_final = directorio_activos[cols_sistema + cols_resto]

# Renombramos 'nombre_sist' a 'nombre' para que quede chulo
directorio_final = directorio_final.rename(columns={'nombre_sist': 'nombre'})


# --- PARTE 4: GUARDAR EL RESULTADO ---
directorio_final.to_excel(excel_nuevo, index=False)
#########AQUÍ COMIENZA EL PEDO DE LA TABLA

# 1. Filtramos el DataFrame 'directorio_final' para dejar las 5 columnas
# (Asegúrate de que la columna del teléfono sea numérico INTEGER para que haga match con tu FK)
empleados_tabla = directorio_final[[
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

empleados_tabla.to_sql(
    name='empleados',
    con=conexion,
    if_exists='append',
    index=False
)

conexion.close()

print("¡Listo carnal! Se pobló la tabla 'empleados' respetando tu schema y la FK hacia 'lineas_telcel'.")

print("=== ¡PROCESO CONCLUIDO CON ÉXITO, CARNAL! ===")
print(f"Total registros matheados y procesados: {len(directorio_final)}")
print("\nMuestra de las primeras columnas resultantes:")
print(directorio_final[['codigo', 'nombre', 'apellido_paterno', 'apellido_materno']].head(5))