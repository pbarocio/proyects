import pandas as pd
from pathlib import Path

archivo = Path.home() / "git" / "pablo-contexto" / "Archivos_Responsivas" / "Directorio.xlsx"
print (archivo)

#1. LEER EL ARCHIVO
#Pandas abre el Excel y sube la pestaña 'Empleados' a la memoria como un DataFrame (df)
df = pd.read_excel(archivo, sheet_name='Empleados')

# 2. IMPRIMIR UNA SOLA COLUMNA
# No necesitas bucles, le pides el nombre de la columna entre corchetes
print("=== LISTA DE NOMBRES ===")
print(df['nombre'])

# 3. IMPRIMIR VARIAS COLUMNAS JUNTAS
print("\n=== ID Y NOMBRE ===")
print(df[['empleado_id', 'nombre', 'estatus']])

# 4. EL FILTRO MÁGICO (Lo que mencionaste)
# Creamos una NUEVA tabla que contiene solo las filas de los activos
activos = df[df['estatus'] == 'ACTIVO']

print("\n=== TABLA RECORTE: SOLO ACTIVOS ===")
print(activos[['empleado_id', 'nombre', 'estatus']])