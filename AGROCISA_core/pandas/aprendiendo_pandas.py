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

def quitar_acentos (cadena):
    if not isinstance(cadena, str):
        return ""
    texto_nfkd = unicodedata.normalize('NFD', cadena)
    return "".join([c for c in texto_nfkd if unicodedata.category(c) != 'Mn'])

def normalizar_cadena(texto):
    if not isinstance(texto, str):
        return ""
    #Extraer caracteres sin espacio (diacrítico) 
    texto_nfkd = unicodedata.normalize('NFD', texto)
    conservar = ['ñ', 'Ñ', 'ü', 'Ü', "'"] #Excluimos la virgulilla de la Ñ y las diérecis de la normalización de los acentos
    
    resultado = []
    for c in texto_nfkd:
        if c in conservar:
            resultado.append(c)
        elif unicodedata.category(c) == 'Mn':
            continue
        else:
            resultado.append(c)
            
    texto_limpio = "".join(resultado)
    texto_limpio = re.sub(r'[^\w\sÑñáéíóúÁÉÍÓÚüÜ.-]', '', texto_limpio) #Elminar carcteres no permitidos (#, $, *, ...) ..
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio) #Colapsa espacios múltiples a uno solo
    texto_limpio = texto_limpio.strip()
    
    return texto_limpio

archivo = Path.home() / "git" / "pablo-contexto" / "Python/Ejemplos/pandas" / "Directorio 2026-07-21 martes.xlsx"

df_empleados = pandas.read_excel(archivo, sheet_name="Empleados")
df_empleados_activos = df_empleados[df_empleados["estatus"] == "ACTIVO"]

df_empleados_nombre_completo = (
    df_empleados_activos["nombre"].astype(str).fillna("").apply(normalizar_cadena) + " " + 
    df_empleados_activos['apellido_paterno'].astype(str).fillna("-").apply(normalizar_cadena) + " " + 
    df_empleados_activos['apellido_materno'].astype(str).fillna("-").apply(normalizar_cadena)
    ).astype(str).str.lower()

print(f"El filro aplicado dejó :{len(df_empleados_activos)} elementos")
print(df_empleados_nombre_completo)
print(f"Se normalizaron :{len(df_empleados_activos)} elementos")
contador_guiones_paterno = df_empleados['apellido_paterno'].str.contains('-', na=False).sum()
contador_guiones_materno = df_empleados['apellido_materno'].str.contains('-', na=False).sum()
print(f"Empleados con guión en Apellido Paterno: {contador_guiones_paterno}")
print(f"Empleados con guión en Apellido Materno: {contador_guiones_materno}")
#print(df_empleados_nombre_completo.isna().sum())

df_asignaciones = pandas.read_excel(archivo, sheet_name="Asignaciones")