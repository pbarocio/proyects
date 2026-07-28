import pandas as pd
import sqlite3
from pathlib import Path
from docxtpl import DocxTemplate
from num2words import num2words
import locale

# Configurar locale para fechas en español
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES')
    except:
        pass  # Si no jala, usamos el formato manual

def format_fecha(fecha_raw):
    """Formatea una fecha a español: 'viernes 25 de julio de 2026'"""
    # Si es string, convertir a datetime
    if isinstance(fecha_raw, str):
        try:
            fecha_raw = pd.to_datetime(fecha_raw)
        except:
            return "Sin fecha"
    
    if pd.isna(fecha_raw):
        return "Sin fecha"
    
    DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", 
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    
    nombre_dia = DIAS[fecha_raw.weekday()]
    nombre_mes = MESES[fecha_raw.month - 1]
    return f"{nombre_dia} {fecha_raw.day} de {nombre_mes} de {fecha_raw.year}".capitalize()

def formatear_precio(precio_raw):
    """Formatea el precio con comas: 10,999"""
    if pd.isna(precio_raw):
        return "0"
    try:
        precio_entero = int(float(precio_raw))
        return f"{precio_entero:,}"
    except:
        return "0"

def precio_a_letras(precio_raw):
    """Convierte un precio a letras: 'Diez mil novecientos noventa y nueve pesos'"""
    if pd.isna(precio_raw):
        return "CERO PESOS 00/100 M.N."
    try:
        precio_entero = int(float(precio_raw))
        letras = num2words(precio_entero, lang='es')
        return f"{letras} pesos 00/100 m.n.".upper()
    except:
        return "CERO PESOS 00/100 M.N."

def generar_responsivas_word(df_responsivas, plantilla_path, output_dir):
    """
    Genera un Word por cada responsiva en el DataFrame usando una plantilla.
    """
    plantilla = DocxTemplate(plantilla_path)
    
    for idx, row in df_responsivas.iterrows():
        # Preparar el contexto para la plantilla
        contexto = {
            'fecha_entrega': format_fecha(row['fecha_entrega']),
            'empleado': row['empleado'].title(),
            'sucursal': row['sucursal'],
            'departamento': row['departamento'],
            'puesto': row['puesto'],
            'hostname': str(row['hostname']) if pd.notna(row['hostname']) else '',
            'procesador': str(row['procesador']) if pd.notna(row['procesador']) else '',
            'memoria_ram': row['memoria_ram'] if pd.notna(row['memoria_ram']) else '',
            'tipo_hdd': row['tipo_hdd'] if pd.notna(row['tipo_hdd']) else '',
            'almacenamiento': row['almacenamiento'] if pd.notna(row['almacenamiento']) else '',
            'correo_gmail': row['correo_gmail'] if pd.notna(row['correo_gmail']) else '',
            'correo_corporativo': row['correo_corporativo'] if pd.notna(row['correo_corporativo']) else '',
            'condicion': row['condicion'] if pd.notna(row['condicion']) else '',
            'comentarios': row['comentarios'] if pd.notna(row['comentarios']) else '',
            'precio': formatear_precio(row['precio']),
            'precio_letras': precio_a_letras(row['precio'])
        }
        
        # Renderizar y guardar
        plantilla.render(contexto)
        nombre_archivo = f"Responsiva CPU {row['empleado'].title()}-{row['hostname']}.docx"
        output_path = Path(output_dir) / nombre_archivo
        plantilla.save(output_path)
        print(f"✅ {nombre_archivo} generado.")
    
    print(f"\n🎯 Total: {len(df_responsivas)} responsivas generadas en '{output_dir}'")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    # Configuración de rutas
    dir_archivos = Path.home() / "git" / "proyects" / "AGROCISA_core" / "Archivos_Responsivas"
    db_path = Path.home() / "git" / "proyects" / "AGROCISA_core" / "agrocisa_core.db"
    plantilla_path = dir_archivos / "plantilla_cpu.docx"
    output_dir = dir_archivos / "Responsivas CPU"
    output_dir.mkdir(exist_ok=True)
    
    # Conectar y traer los datos
    conexion = sqlite3.connect(db_path)
    
    query = """
    SELECT
	rcp.fecha_entrega,
	emp.nombre || ' ' || emp.apellido_paterno || ' ' || emp.apellido_materno AS empleado,
	suc.nombre_sucursal AS sucursal,
	dep.nombre_departamento AS departamento,
	pue.nombre_puesto AS puesto,
	icp.hostname,
	icp.procesador,
	icp.memoria_ram,
	thd.hdd_opcion AS tipo_hdd,
	icp.almacenamiento,
	ce.correo_gmail,
	ce.correo_corporativo,
	con.condicion_opcion AS condicion,
	icp.comentarios,
    icp.precio

	FROM responsivas_cpu rcp
	LEFT JOIN empleados emp ON rcp.codigo_empleado = emp.codigo
	LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
	LEFT JOIN departamentos dep ON emp.id_departamento = dep.id_departamento
	LEFT JOIN puestos pue ON emp.id_puesto = pue.id_puesto
	LEFT JOIN inventario_cpu icp ON rcp.hostname = icp.hostname
	LEFT JOIN hdd_tipo thd ON icp.id_hdd_tipo = thd.id_hdd_tipo
	LEFT JOIN condicion con ON icp.id_condicion = con.id_condicion
	LEFT JOIN (
		SELECT
			codigo_empleado,
			MAX(CASE WHEN id_tipo_correo = 2 THEN direccion_correo END) AS correo_gmail,
                MAX(CASE WHEN id_tipo_correo = 1 THEN direccion_correo END) AS correo_corporativo
            FROM correos_electronicos
            WHERE id_estatus_correo = 1  -- 👈 ACTIVO = 1
            GROUP BY codigo_empleado
	) ce ON icp.codigo_empleado = ce.codigo_empleado
	ORDER BY rcp.fecha_entrega ASC, emp.nombre
    """
    
    df_responsivas = pd.read_sql_query(query, conexion)
    conexion.close()
    
    print(f"✅ {len(df_responsivas)} responsivas de cpu cargadas desde la BDD.")
    
    # Generar los Word
    generar_responsivas_word(df_responsivas, plantilla_path, output_dir)