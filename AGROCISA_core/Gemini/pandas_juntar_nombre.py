import pandas as pd
import unicodedata
from pathlib import Path

archivo = Path.home() / "git" / "pablo-contexto" / "Archivos_Responsivas" / "Directorio.xlsx"
print (archivo)

# 1. LA FUNCIÓN MÁGICA (Cópiala y déjala ahí tranquila)
def quitar_acentos(texto):
    if not isinstance(texto, str):
        return ""
    texto_nfkd = unicodedata.normalize('NFD', texto)
    return "".join([c for c in texto_nfkd if unicodedata.category(c) != 'Mn'])


# 2. CARGAR EL EXCEL Y FILTRAR ACTIVOS
df = pd.read_excel(archivo, sheet_name='Empleados')
activos = df[df['estatus'] == 'ACTIVO'].copy()  # El .copy() es para trabajar seguros en una tabla limpia


# 3. PARTE NUEVA: JUNTAR Y LIMPIAR
# Agarramos las 3 columnas de activos, las pegamos, quitamos espacios y pasamos a minúsculas
nombres_pegados = (
    activos['nombre'].astype(str).str.strip() + " " +
    activos['apellido_paterno'].astype(str).str.strip() + " " +
    activos['apellido_materno'].astype(str).str.strip()
).str.lower()

# Le quitamos los acentos a toda la columna resultante de un solo trancazo
activos['llave_limpia'] = nombres_pegados.apply(quitar_acentos)

# Convertimos las columnas 'llave_limpia' y 'codigo' directamente a un Diccionario
mapa_empleados = dict(zip(activos['llave_limpia'], activos['codigo']))

# Vamos a probar cómo busca en la memoria:
print("=== EJEMPLO DE BÚSQUEDA EN EL DICCIONARIO ===")
# Pon aquí el nombre de algún empleado de tu empresa (en minúsculas y sin acentos)
ejemplo_busqueda = "pablo alberto barocio valle" 

if ejemplo_busqueda in mapa_empleados:
    print(f"El número de nómina/código de {ejemplo_busqueda} es: {mapa_empleados[ejemplo_busqueda]}")
else:
    print("No se encontró al empleado.")


# 4. VAMOS A VER QUÉ HIZO
print("=== EJEMPLO DE NOMBRES LIMPIOS Y LISTOS ===")
print(activos[['codigo', 'llave_limpia']].head(10))