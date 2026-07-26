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
directorio_nuevo = dir_archivos / "Estructura BDD.xlsx"
#LEEMOS la HOJA 'Asignaciones qué contiene los datos' SÓLO CON LAS COLUMNAS FUNCIONALES
df_datos_correos = pandas.read_excel(
                                    directorio_nuevo,
                                    sheet_name='Asignaciones',
                                    usecols=["codigo","Correo Gmail","Contraseña Gmail","Correo Institucional", "Contraseña Institucional"]
                                    ).copy()
#CREAMOS EL DATAFRAME CON LOS DATOS DE CORREOS_CORPORATIVOS
df_tabla_correos_Corporativos = pandas.DataFrame({
    'codigo_empleado': df_datos_correos["codigo"],
    'tipo_correo_df': 'CORPORATIVO',
    'direccion_correo': df_datos_correos["Correo Institucional"],
    'password': df_datos_correos["Contraseña Institucional"]
})
#Eliminamos los Correos qué estén en Null, NaN o ""
df_tabla_correos_Corporativos = df_tabla_correos_Corporativos[df_tabla_correos_Corporativos['direccion_correo'].notna() & (df_tabla_correos_Corporativos['direccion_correo'] != '')]

#CREAMOS EL DATAFRAME CON LOS DATOS DE GMAIL
df_tabla_correos_Gmail = pandas.DataFrame({
    'codigo_empleado': df_datos_correos["codigo"],
    'tipo_correo_df' : 'GMAIL',
    'direccion_correo': df_datos_correos["Correo Gmail"],
    'password': df_datos_correos["Contraseña Gmail"]
})
#Eliminamos los Correos qué estén en Null, NaN o ""
df_tabla_correos_Gmail = df_tabla_correos_Gmail[df_tabla_correos_Gmail['direccion_correo'].notna() & (df_tabla_correos_Gmail['direccion_correo'] != '')]

#CONCATENAMOS LOS DOS DATAFRAMES
df_correos = pandas.concat([df_tabla_correos_Corporativos, df_tabla_correos_Gmail], ignore_index=True)
#CREAMOS LA COLUMNA DE ACTIVOS
df_correos['estatus_correo_df'] = 'ACTIVO'
# Solo los que no tienen código se ponen INACTIVO
df_correos.loc[df_correos['codigo_empleado'].isna(), 'estatus_correo_df'] = 'INACTIVO'

#LEEMOS LA TABLA DE estatus_correos_electronicos
db_name = "agrocisa_core.db"
conexion = sqlite3.connect(db_name)
cursor = conexion.cursor()

df_tipo_correo = pandas.read_sql_query("SELECT id_tipo_correo, tipo_correo FROM tipos_correos_electronicos", conexion)
df_estatus_correo = pandas.read_sql_query("SELECT id_estatus_correo, estatus_correo FROM estatus_correos_electronicos", conexion)

conexion.commit()
conexion.close()
#HACEMOS MERGE PARA TRAER EL TIPO DE CORREO
df_correo_tipo = df_correos.merge(
    df_tipo_correo,
    left_on='tipo_correo_df',
    right_on='tipo_correo',
    how='left'
)

#HACEMOS UN MERGE PARA TENER EL ID DE ESTATUS_CORREO
df_correos_id = df_correo_tipo.merge(
    df_estatus_correo,
    left_on='estatus_correo_df',
    right_on='estatus_correo',
    how='left'
)

#CAMBIAMOS EL ÓRDEN DE LAS COLUMNAS
columnas_correo_id = [
    'direccion_correo',
    'password',
    'id_tipo_correo',
    'id_estatus_correo',
    'codigo_empleado',
]
df_correos_id = df_correos_id[columnas_correo_id]

print(f"\"{len(df_correos_id)}\" direcciones de correo listas para exportar...")
#Escribimos una hoja para los correos de Gmail
with pandas.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_correos_id.to_excel(writer, sheet_name='Correos', index=False)