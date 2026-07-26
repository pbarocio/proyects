import pandas
from openpyxl import load_workbook
from pathlib import Path
import numpy as np
import sqlite3
from num2words import num2words

def format_fecha(fecha_raw):
    if not fecha_raw or fecha_raw == "Sin dato":
        return "Sin Fecha"
        
    # Listas de traducción nativa
    DIAS_SEMANA = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    
    # Armamos las piezas usando las propiedades del objeto fecha
    nombre_dia = DIAS_SEMANA[fecha_raw.weekday()]
    nombre_mes = MESES[fecha_raw.month - 1]
    dia_mes = fecha_raw.day
    anio = fecha_raw.year
    
    # Juntamos todo y le clavamos el .capitalize() para la mayúscula inicial
    return f"{nombre_dia} {dia_mes} de {nombre_mes} de {anio}".capitalize()

def formatear_precio(precio_raw):
    if precio_raw is None:
        return "0"
    try:
        precio_entero = int(float(precio_raw))
        return f"{precio_entero:,}"
    except (ValueError, TypeError):
        return "0"

def convertir_precio_letras(precio_raw):
    if precio_raw is None:
        return "CERO PESOS 00/100 M.N."
    try:
        precio_entero = int(float(precio_raw))
        precio_en_letras = num2words(precio_entero, lang='es')
        return f"{precio_en_letras} pesos 00/100 m.n.".upper()
    except (ValueError, TypeError):
        return "CERO PESOS 00/100 M.N."

# Mostrar todas las filas
pandas.set_option('display.max_rows', None)

# Mostrar todas las columnas
pandas.set_option('display.max_columns', None)

# Mostrar texto completo (sin truncar)
pandas.set_option('display.max_colwidth', None)

#Aquí comienza el código
#DEFINIMOS LA RUTA DE LOS ARCHIVOS
dir_archivos = Path.home() / "git" / "proyects" / "AGROCISA_core"
#AGREGAMOS LA RUTA COMPLETA DEL ARCHIVO DE EXCEL
directorio = dir_archivos / "Directorio 2026-07-21 martes.xlsx"
directorio_nuevo = dir_archivos / "Estructura BDD.xlsx"
#LEEMOS la HOJA qué contiene los datos' 
df_responsivas = pandas.read_excel(directorio_nuevo, sheet_name='Responsivas Celulares').copy()

#fecha_entrega	codigo_empleado	numero	imei
#LEEMOS LAS TABLA
db_name = "agrocisa_core.db"
conexion = sqlite3.connect(db_name)

query = """
    SELECT 
    r.fecha_entrega,
    e.codigo,
    e.nombre || ' ' || e.apellido_paterno || ' ' || e.apellido_materno AS empleado,
    s.nombre_sucursal AS sucursal,
    d.nombre_departamento AS departamento,
    p.nombre_puesto AS puesto,
    eq.marca_modelo AS equipo,
    r.numero,
    r.imei,
    ic.numero_serie,
    ce.correo_gmail,
    ce.correo_institucional,
    lt.gb_promocion_2026,
    c.condicion_opcion AS condicion,
    ca.cargador_opcion AS cargador,
    caja.caja_opcion AS caja,
    ic.comentarios,
    eq.precio
    FROM responsivas_celulares r
    JOIN empleados e ON r.codigo_empleado = e.codigo
    JOIN sucursales s ON e.id_sucursal = s.id_sucursal
    JOIN departamentos d ON e.id_departamento = d.id_departamento
    JOIN puestos p ON e.id_puesto = p.id_puesto
    JOIN inventario_celulares ic ON r.imei = ic.imei
    JOIN equipos_2026 eq ON ic.id_equipo = eq.id_equipo
    JOIN condicion c ON ic.id_condicion = c.id_condicion
    JOIN cargadores ca ON ic.id_cargador = ca.id_cargador
    JOIN caja ON ic.id_caja = caja.id_caja
    LEFT JOIN lineas_telefonicas lt ON r.numero = lt.numero
    LEFT JOIN (
        SELECT 
            codigo_empleado,
            MAX(CASE WHEN id_tipo_correo = 2 THEN direccion_correo END) AS correo_gmail,
            MAX(CASE WHEN id_tipo_correo = 1 THEN direccion_correo END) AS correo_institucional
        FROM correos_electronicos
        WHERE id_estatus_correo = 1  -- 👈 ACTIVO = 1
        GROUP BY codigo_empleado
    ) ce ON e.codigo = ce.codigo_empleado
    ORDER BY r.fecha_entrega DESC, e.nombre;
    """
df_responsivas = pandas.read_sql_query(query, conexion)
conexion.close()

#df_responsivas["fecha_entrega"] = df_responsivas["fecha_entrega"].apply(format_fecha)
df_responsivas["precio"] = df_responsivas["precio"].apply(formatear_precio)
df_responsivas["precio_letras"] = df_responsivas["precio"].apply(convertir_precio_letras)

# Exportar a Excel
with pandas.ExcelWriter("responsivas_celulares.xlsx", engine='openpyxl') as writer:
    df_responsivas.to_excel(writer, sheet_name='Responsivas', index=False)

print(f"✅ {len(df_responsivas)} responsivas exportadas a 'responsivas_celulares.xlsx'")