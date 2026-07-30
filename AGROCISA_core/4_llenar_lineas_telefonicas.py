import pandas
from openpyxl import load_workbook
from pathlib import Path
import numpy as np
from db_config import get_files_path, get_engine
from sqlalchemy import text

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

def limpiar_telefono(valor):
    if pandas.isna(valor) or valor is None: # 1. Manejo de nulos o celdas vacías
        return None
    texto = str(valor).split(".")[0].strip() # 2. Si es float/int, quitamos el punto decimal convirtiendo primero a string

    digitos = "".join(filter(str.isdigit, texto))  # 3. Nos quedamos solo con los caracteres numéricos

    if not digitos or len(digitos) != 10: # 4. Validamos que no esté vacío Y que sean exactamente 10 dígitos
        return None  # O puedes regresar None para marcarlo como inválido/vacío

    return digitos

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
files = get_files_path()
directorio = files['directorio']
directorio_nuevo = files['directorio_nuevo']
#LEEMOS la HOJA 'Asignaciones qué contiene los datos' SÓLO CON LAS COLUMNAS FUNCIONALES
df_datos_lineas = pandas.read_excel(directorio, sheet_name='Historico_Lineas_2026').copy()
df_datos_empleado = pandas.read_excel(directorio_nuevo, sheet_name='Asignaciones').copy()

df_datos_empleado['Celular'] = df_datos_empleado['Celular'].apply(limpiar_telefono)

df_lineas_telefonicas = pandas.DataFrame({
    'numero' : df_datos_lineas["número"].apply(limpiar_telefono),
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

df_lineas_telefonicas["id_estatus_linea"] = 1

#Escribimos la hoja de empleados
with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_lineas_telefonicas.to_excel(writer, sheet_name='Lineas Telefónicas', index=False)
    
print(f"\"{len(df_lineas_telefonicas)}\" líneas telefónicas listas para importar")

engine = get_engine()

with engine.begin() as conn:
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))

    df_lineas_telefonicas.to_sql(
        name='lineas_telefonicas',
        con=conn,
        if_exists='append',
        index=False
    )

    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))

print(f"Se inyectó correctamente la tabla 'lineas_telefonicas'")