import sqlite3
import pandas as pd
import unicodedata
import re
from pathlib import Path

# --- RUTA DE ARCHIVO Y BASE DE DATOS ---
archivo_excel = Path.home() / "git" / "proyects" / "AGROCISA_core" /"Archivos_Responsivas" / "Directorio.xlsx"
db_path = "agrocisa_core.db"

# --- FUNCIÓN DE NORMALIZACIÓN PARA MACHEAR NOMBRES ---
def normalizar_cadena(texto):
    if not isinstance(texto, str):
        return ""
    texto_nfkd = unicodedata.normalize('NFD', texto)
    texto = "".join([c for c in texto_nfkd if unicodedata.category(c) != 'Mn'])
    texto = re.sub(r'[^\w\sÑñ.-]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto.lower()

# 1. LEER EXCEL Y CONECTAR A LA BD
df_asig = pd.read_excel(archivo_excel, sheet_name='Asignaciones')
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# 2. OBTENER MAPEO DE EMPLEADOS DESDE LA BD {nombre_normalizado: codigo}
df_emp_db = pd.read_sql_query("SELECT codigo, nombre, apellido_paterno, apellido_materno FROM empleados", conexion)
df_emp_db['llave'] = (
    df_emp_db['nombre'].fillna('') + " " + 
    df_emp_db['apellido_paterno'].fillna('') + " " + 
    df_emp_db['apellido_materno'].fillna('')
).apply(normalizar_cadena)

mapa_empleados = dict(zip(df_emp_db['llave'], df_emp_db['codigo']))

# 3. EXTRACCIÓN Y PREPARACIÓN DE DATOS
registros_correos = []

for _, fila in df_asig.iterrows():
    nombre_raw = str(fila.get('Nombre', ''))
    nombre_norm = normalizar_cadena(nombre_raw)
    
    # Identificar el código de empleado
    codigo_emp = mapa_empleados.get(nombre_norm, None)
    estatus = 'VACANTE' if codigo_emp is None else 'ACTIVO'

    # A) Correo Institucional + Contraseña.1
    inst_email = str(fila.get('Correo Institucional', '')).strip().lower()
    inst_pass = str(fila.get('Contraseña.1', '')) if pd.notna(fila.get('Contraseña.1')) else None
    
    if inst_email and inst_email != 'nan' and '@' in inst_email:
        registros_correos.append((inst_email, inst_pass, 'INSTITUCIONAL', codigo_emp, estatus))

    # B) Correo Gmail + Contraseña
    gmail_email = str(fila.get('Correo Gmail', '')).strip().lower()
    gmail_pass = str(fila.get('Contraseña', '')) if pd.notna(fila.get('Contraseña')) else None
    
    if gmail_email and gmail_email != 'nan' and '@' in gmail_email and gmail_email != inst_email:
        registros_correos.append((gmail_email, gmail_pass, 'GMAIL', codigo_emp, estatus))

# 4. INYECCIÓN DIRECTA A LA TABLA YA CREADA
cursor.executemany("""
    INSERT OR REPLACE INTO correos_electronicos (direccion_correo, password, tipo_correo, codigo_empleado, estatus)
    VALUES (?, ?, ?, ?, ?);
""", registros_correos)

conexion.commit()
conexion.close()

print(f"=== ¡A HUEVO, CARNAL! ===")
print(f"Se inyectaron {len(registros_correos)} correos a la base de datos 'agrocisa_core.db'.")