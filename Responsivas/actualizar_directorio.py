import pandas as pd
import unicodedata
from pathlib import Path

archivo = Path.home() / "git" / "pablo-contexto" / "Archivos_Responsivas" / "Directorio.xlsx"
print (archivo)

excel_nuevo = Path.home() / "git" / "pablo-contexto" / "Archivos_Responsivas" / "Directorio_Con_Codigo.xlsx"

# 1. FUNCIÓN MÁGICA
def quitar_acentos(texto):
    if not isinstance(texto, str):
        return ""
    texto_nfkd = unicodedata.normalize('NFD', texto)
    return "".join([c for c in texto_nfkd if unicodedata.category(c) != 'Mn'])

# --- PARTE 1: LA FUENTE DE LA VERDAD (EMPLEADOS) ---
df_emp = pd.read_excel(archivo, sheet_name='Empleados')
activos = df_emp[df_emp['estatus'] == 'ACTIVO'].copy()

# Armamos la llave limpia de la base del sistema
nombres_emp = (
    activos['nombre'].astype(str).str.strip() + " " +
    activos['apellido_paterno'].astype(str).str.strip() + " " +
    activos['apellido_materno'].astype(str).str.strip()
).str.lower()

activos['llave_limpia'] = nombres_emp.apply(quitar_acentos)

# Creamos nuestro diccionario zíper
mapa_empleados = dict(zip(activos['llave_limpia'], activos['codigo']))


# --- PARTE 2: EL CRUCE CON EL DIRECTORIO ---
df_dir = pd.read_excel(archivo, sheet_name='Directorio')

# A. Limpiamos la columna 'Nombre' del Directorio para poder comparar
nombre_dir_limpio = df_dir['Nombre'].astype(str).str.strip().str.lower().apply(quitar_acentos)

# B. LA MAGIA DE PANDAS: Inyectamos el código buscando en el diccionario
# .map() busca cada nombre del directorio en el diccionario y le pega el valor (código)
df_dir['codigo'] = nombre_dir_limpio.map(mapa_empleados)

# C. FILTRAR ACTIVOS Y MOVER COLUMNA AL INICIO
# Los que no hicieron match o pertenecen a gente dada de baja quedan como NaN (vacíos)
directorio_activos = df_dir.dropna(subset=['codigo']).copy()

# Convertimos el código a entero (para que no salga como 595.0 en Excel)
directorio_activos['codigo'] = directorio_activos['codigo'].astype(int)

# Reordenamos columnas para que 'codigo' sea la primera
cols = ['codigo'] + [c for c in directorio_activos.columns if c != 'codigo']
directorio_final = directorio_activos[cols]


# --- PARTE 3: GUARDAR EL RESULTADO ---
directorio_final.to_excel(excel_nuevo, index=False)

print("=== ¡LISTO CARNAL! ===")
print(f"Total registros en directorio original: {len(df_dir)}")
print(f"Total registros activos matheados: {len(directorio_final)}")
print("\nMuestra de los primeros 5 resultados:")
print(directorio_final[['codigo', 'Nombre', 'Correo Gmail']].head(5))