import pandas
from pathlib import Path
import unicodedata
import re

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
dir_archivos = Path.home() / "git" / "proyects" / "AGROCISA_core" / "pandas"

archivo = Path.home() / "git" / "proyects" / "AGROCISA_core" / "pandas" / "Directorio 2026-07-21 martes.xlsx"

df_empleados = pandas.read_excel(archivo, sheet_name="Empleados")
df_empleados_activos = df_empleados[df_empleados["estatus"] == "ACTIVO"].copy()

df_nombre_completo_empleados_normalizado = (
    df_empleados_activos["nombre"].astype(str).fillna("").apply(normalizar_cadena) + " " + 
    df_empleados_activos['apellido_paterno'].astype(str).fillna("").apply(normalizar_cadena) + " " + 
    df_empleados_activos['apellido_materno'].astype(str).fillna("").apply(normalizar_cadena)
    ).astype(str).str.lower()

print(f"El filro aplicado dejó :{len(df_empleados_activos)} elementos")
print(f"Se normalizaron :{len(df_nombre_completo_empleados_normalizado)} elementos")
#print(df_nombre_completo_empleados_normalizado)
# contador_guiones_paterno = df_empleados['apellido_paterno'].str.contains('-', na=False).sum()
# contador_guiones_materno = df_empleados['apellido_materno'].str.contains('-', na=False).sum()
# print(f"Empleados con guión en Apellido Paterno: {contador_guiones_paterno}")
# print(f"Empleados con guión en Apellido Materno: {contador_guiones_materno}")
#print(nombre_completo_empleados_normalizado.isna().sum())

df_asignaciones = pandas.read_excel(archivo, sheet_name="Asignaciones")

df_nombre_completo_asignaciones_normalizado = df_asignaciones['Nombre'].apply(normalizar_cadena).str.lower()

print(f"Asignaciones tiene: {len(df_asignaciones['Nombre'])} elementos")
print(f"Se normalizaron: {len(df_nombre_completo_asignaciones_normalizado)} elementos")
print(df_nombre_completo_empleados_normalizado)

df_nombre_completo_empleados_normalizado = df_nombre_completo_empleados_normalizado.sort_values().reset_index(drop=True)
df_nombre_completo_asignaciones_normalizado = df_nombre_completo_asignaciones_normalizado.sort_values().reset_index(drop=True)

df_comparacion = pandas.DataFrame({
    'nombre_empleados': df_nombre_completo_empleados_normalizado,
    'nombre_asignaciones': df_nombre_completo_asignaciones_normalizado
})

archivo_salida = Path.home() / "git" / "proyects" / "AGROCISA_core" / "pandas" / "Comparacion.xlsx"

df_comparacion.to_excel(archivo_salida, index=False)


#MERGE
# 1. Creas un DataFrame con los nombres normalizados de Empleados y sus códigos
df_empleados_para_merge = pandas.DataFrame({
    'nombre_normalizado': df_nombre_completo_empleados_normalizado.reset_index(drop=True),
    'codigo': df_empleados_activos['codigo'].reset_index(drop=True)
})

# 2. Creas un DataFrame con los nombres normalizados de Asignaciones
df_asignaciones_para_merge = pandas.DataFrame({
    'nombre_normalizado': df_nombre_completo_asignaciones_normalizado.reset_index(drop=True)
})

# 3. Haces un merge (left join)
df_resultado = df_asignaciones_para_merge.merge(
    df_empleados_para_merge,
    on='nombre_normalizado',
    how='left'  # ← Esto es clave: LEFT JOIN
)

# Los que sí encontraron
match = df_resultado[df_resultado['codigo'].notna()]

# Los que no encontraron (los que te interesan)
no_match = df_resultado[df_resultado['codigo'].isna()]

archivo_merge  = dir_archivos / "Resultado_Merge.xlsx"

df_resultado.to_excel(archivo_merge, index=False)