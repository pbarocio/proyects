import pandas
from openpyxl import load_workbook
from pathlib import Path
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

#Aquí comienza el código
#DEFINIMOS LA RUTA DE LOS ARCHIVOS
dir_archivos = Path.home() / "git" / "proyects" / "AGROCISA_core"
#AGREGAMOS LA RUTA COMPLETA DEL ARCHIVO DE EXCEL
directorio_nuevo = dir_archivos / "Asignaciones_merged.xlsx"
#LEEMOS la HOJA 'Asignaciones qué contiene los datos' SÓLO CON LAS COLUMNAS FUNCIONALES
pd_datos_correos = pandas.read_excel(
                                    directorio_nuevo,
                                    sheet_name='Asignaciones',
                                    usecols=["codigo","Correo Gmail","Contraseña Gmail","Correo Institucional", "Contraseña Institucional"]
                                    ).copy()

pd_tabla_correos_Gmail = pandas.DataFrame({
    'codigo_empleados': pd_datos_correos["codigo"],
    'tipo_correo' : 'Gmail'
    'correo': pd_datos_correos["Correo Gmail"],
    'password': pd_datos_correos["Contraseña Gmail"]
})

#pd_todos_correos = pandas.concat([pd_tabla_correos["codigo"], pandas.Series(pd_datos_correos["Correo Institucional"])], ignore_index=True)

with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    pd_tabla_correos_Gmail.to_excel(writer, sheet_name='Corres Gmail', index=False)

pd_tabla_correos_Institucionales = pandas.DataFrame({
    'codigo_empleados': pd_datos_correos["codigo"],
    'correo': pd_datos_correos["Correo Institucional"],
    'password': pd_datos_correos["Contraseña Institucional"]
    'tipo': 'Corporativo'
})

with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    pd_tabla_correos_Institucionales.to_excel(writer, sheet_name='Correos Institucionales', index=False)
