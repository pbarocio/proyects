import pandas
from openpyxl import load_workbook
from pathlib import Path
import numpy as np
import sqlite3

# Mostrar todas las filas
pandas.set_option('display.max_rows', None)

# Mostrar todas las columnas
pandas.set_option('display.max_columns', None)

# Mostrar texto completo (sin truncar)
pandas.set_option('display.max_colwidth', None)

def limpiar_entero (valor):
    if pandas.isna(valor):
        return None
    if isinstance(valor, float):
        valor = int(valor)
    # Sacamos los números limpios
    digitos = ''.join(filter(str.isdigit, str(valor)))
    # Si la celda estaba vacía o con un espacio blanco, 'digitos' vale ''
    if not digitos:
        return None
        
    return int(digitos)

def limpiar_moneda(value):
    if value is None or str(value).strip() in ('N/A', ''):
        return None
    clean_val = str(value).replace('$', '').replace(',', '').strip()
    return float(clean_val)

def limpiar_gb(value):
    if value is None or str(value).strip() in ('N/A', ''):
        return None
    clean_val = str(value).replace(',', '.').strip()
    return float(clean_val)

#Aquí comienza el código
#DEFINIMOS LA RUTA DE LOS ARCHIVOS
dir_archivos = Path.home() / "git" / "proyects" / "AGROCISA_core"
#AGREGAMOS LA RUTA COMPLETA DEL ARCHIVO DE EXCEL
directorio = dir_archivos / "Directorio 2026-07-21 martes.xlsx"
directorio_nuevo = dir_archivos / "Estructura BDD.xlsx"
#LEEMOS la HOJA 'Asignaciones qué contiene los datos' SÓLO CON LAS COLUMNAS FUNCIONALES
df_datos_lineas = pandas.read_excel(directorio, sheet_name='Historico_Lineas_2026').copy()
df_datos_empleado = pandas.read_excel(directorio_nuevo, sheet_name='Asignaciones').copy()

df_lineas_telefonicas = pandas.DataFrame({
    'numero' : df_datos_lineas["número"].apply(limpiar_entero),
    'mpp' : np.where(df_datos_lineas["MPP"].notna(),1, 0),
    'plan_2024' : df_datos_lineas["Plan 2024"],
    'mensualidad_2024' : df_datos_lineas["Mensualidad 2024"].apply(limpiar_moneda),
    'GB_2024' : df_datos_lineas["GB 2024"].apply(limpiar_gb),
    'plan_2026' : df_datos_lineas["Plan 2026"],
    'mensualidad_2026' : df_datos_lineas["Mensualidad 2026"].apply(limpiar_moneda),
    'GB_2026' : df_datos_lineas["GB"].apply(limpiar_gb),
    'GB_promocion_2026' : df_datos_lineas["GB Promoción"].apply(limpiar_gb),
    'diferencia_2024_2026' : df_datos_lineas["Diferencia"].apply(limpiar_moneda)
})

#df_lineas_telefonicas["mpp"] = np.where(df_datos_lineas["MPP"].notna(),1, 0)
df_lineas_telefonicas_codigo = df_lineas_telefonicas.merge(
    df_datos_empleado,
    left_on='numero',
    right_on='Celular',
    how='left'
)

columnas_lineas_telefonicas = [
    'numero',
    'codigo',
    'mpp',
    'plan_2024',
    'mensualidad_2024',
    'GB_2024',
    'plan_2026',
    'mensualidad_2026',
    'GB_2026',
    'GB_promocion_2026',
    'diferencia_2024_2026',
]
df_lineas_telefonicas = df_lineas_telefonicas_codigo[columnas_lineas_telefonicas]
df_lineas_telefonicas.rename(columns={
    'codigo' : 'codigo_empleado',
    'mpp' : 'is_mpp'
    },inplace=True)

#Escribimos la hoja de empleados
with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_lineas_telefonicas.to_excel(writer, sheet_name='Lineas Telefónicas', index=False)
    
print(f"\"{len(df_lineas_telefonicas)}\" líneas telefónicas listas para importar")

conexion = sqlite3.connect("agrocisa_core.db")

df_lineas_telefonicas.to_sql(
    name='lineas_telefonicas',
    con=conexion,
    if_exists='append',
    index=False
)

conexion.commit()
conexion.close()

print(f"Se importó correctamente la tabla lineas_telefonicas")