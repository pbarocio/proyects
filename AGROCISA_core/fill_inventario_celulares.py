import sqlite3
import pandas as pd
import unicodedata
import re
from pathlib import Path

# --- RUTAS DE ARCHIVO Y BDD ---
archivo_excel = Path.home() / "git" / "proyects" / "AGROCISA_core" /"Archivos_Responsivas" / "Directorio.xlsx"
db_path = "agrocisa_core.db"

# --- FUNCIONES DE LIMPIEZA Y NORMALIZACIÓN ---
def normalizar_cadena(texto):
    if not isinstance(texto, str):
        return ""
    texto_nfkd = unicodedata.normalize('NFD', texto)
    texto = "".join([c for c in texto_nfkd if unicodedata.category(c) != 'Mn'])
    texto = re.sub(r'[^\w\sÑñ.-]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto.lower()

def limpiar_entero(valor):
    """Limpia números de teléfono/renovación garantizando 10 dígitos sin ceros fantasma."""
    if pd.isna(valor) or str(valor).strip().lower() in ['nan', 'none', 'null', '']:
        return None
    
    val_str = str(valor).strip()
    
    # Si por alguna razón viene con punto decimal de float, volamos lo que esté a la derecha
    if '.' in val_str:
        val_str = val_str.split('.')[0]
        
    # Dejamos solo los dígitos numéricos
    digitos = re.sub(r'\D', '', val_str)
    
    return int(digitos) if digitos else None

# 1. LEER EXCEL Y CONECTAR A LA BD
df_cel = pd.read_excel(archivo_excel, sheet_name='Inventario Celulares')
conexion = sqlite3.connect(db_path)
cursor = conexion.cursor()

# 2. CARGAR MAPEOS DE DICCIONARIOS EN MEMORIA (De las tablas base que ya creaste)

# A) Mapeo Empleados {nombre_normalizado: codigo}
df_emp = pd.read_sql_query("SELECT codigo, nombre, apellido_paterno, apellido_materno FROM empleados", conexion)
df_emp['llave'] = (
    df_emp['nombre'].fillna('') + " " + 
    df_emp['apellido_paterno'].fillna('') + " " + 
    df_emp['apellido_materno'].fillna('')
).apply(normalizar_cadena)
mapa_empleados = dict(zip(df_emp['llave'], df_emp['codigo']))

# B) Mapeo Equipos {marca_modelo_normalizada: id_equipo}
df_eq = pd.read_sql_query("SELECT id_equipo, marca_modelo FROM equipos_2026", conexion)
mapa_equipos = dict(zip(df_eq['marca_modelo'].apply(normalizar_cadena), df_eq['id_equipo']))

# C) Mapeo Condicion {condicion_normalizada: id_condicion}
df_cond = pd.read_sql_query("SELECT condicion_opcion, condicion_opcion FROM condicion", conexion)
mapa_condicion = dict(zip(df_cond['condicion_opcion'].apply(normalizar_cadena), df_cond['condicion_opcion']))

# D) Mapeo Cargadores {cargador_normalizado: id_cargador}
df_carg = pd.read_sql_query("SELECT id_cargador, cargador_opcion FROM cargadores", conexion)
mapa_cargadores = dict(zip(df_carg['cargador_opcion'].apply(normalizar_cadena), df_carg['id_cargador']))

# E) Mapeo Cajas {caja_normalizada: id_caja}
df_caja = pd.read_sql_query("SELECT caja_opcion, caja_opcion FROM caja", conexion)
mapa_cajas = dict(zip(df_caja['caja_opcion'].apply(normalizar_cadena), df_caja['caja_opcion']))

# 3. EXTRAER Y TRANSFORMAR FILA POR FILA
registros_celulares = []

for _, fila in df_cel.iterrows():
    # Extraer IMEI (Mandatorio)
    imei_raw = str(fila.get('IMEI', '')).strip()
    imei = re.sub(r'\D', '', imei_raw)
    
    if not imei or len(imei) < 10:
        continue  # Si no hay IMEI válido, salta la fila

    # Datos únicos de Hardware
    num_renovacion = limpiar_entero(fila.get('Renovación'))
    num_serie = str(fila.get('Número de Serie', '')).strip() if pd.notna(fila.get('Número de Serie')) else None
    mac_addr = str(fila.get('MacAddress', '')).strip() if pd.notna(fila.get('MacAddress')) else None
    
    # Manejo de Fecha de Entrega
    fecha_raw = fila.get('Fecha de Entrega')
    fecha_entrega = pd.to_datetime(fecha_raw).strftime('%Y-%m-%d') if pd.notna(fecha_raw) else None
    
    # Comentarios y Observaciones
    comentarios = str(fila.get('Comentarios', '')).strip() if pd.notna(fila.get('Comentarios')) else None
    observaciones = str(fila.get('Observaciones', '')).strip() if pd.notna(fila.get('Observaciones')) else None

    # Mapeo de Foreign Keys
    num_linea = limpiar_entero(fila.get('Número'))
    
    equipo_norm = normalizar_cadena(str(fila.get('Marca-Modelo', '')))
    id_equipo = mapa_equipos.get(equipo_norm)

    cond_norm = normalizar_cadena(str(fila.get('Condición', '')))
    id_condicion = mapa_condicion.get(cond_norm)

    carg_norm = normalizar_cadena(str(fila.get('Cargador', '')))
    id_cargador = mapa_cargadores.get(carg_norm)

    caja_norm = normalizar_cadena(str(fila.get('Caja', '')))
    id_caja = mapa_cajas.get(caja_norm)

    emp_norm = normalizar_cadena(str(fila.get('Código_empleado', fila.get('Nombre', ''))))
    codigo_emp = mapa_empleados.get(emp_norm)

    registros_celulares.append((
        num_renovacion,
        imei,
        num_serie,
        mac_addr,
        fecha_entrega,
        comentarios,
        observaciones,
        num_linea,
        id_equipo,
        id_condicion,
        id_cargador,
        id_caja,
        codigo_emp
    ))

# 4. INYECCIÓN MASIVA A LA TABLA
cursor.executemany("""
    INSERT OR REPLACE INTO inventario_celulares (
        numero_renovacion,
        imei,
        numero_serie,
        mac_address,
        fecha_entrega,
        comentarios,
        observaciones,
        numero,
        id_equipo,
        id_condicion,
        id_cargador,
        id_caja,
        codigo_empleado
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
""", registros_celulares)

conexion.commit()
conexion.close()

print(f"=== ¡A HUEVO, CARNAL! ===")
print(f"Se inyectaron {len(registros_celulares)} celulares al inventario en 'agrocisa_core.db'.")