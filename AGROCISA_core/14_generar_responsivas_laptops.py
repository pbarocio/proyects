import pandas as pd
from db_config import get_files_path, get_engine
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
            'marca': row['marca'],
            'modelo': str(row['modelo']) if pd.notna(row['modelo']) else '',
            'numero_serie': row['numero_serie'] if pd.notna(row['numero_serie']) else '',
            'correo_gmail': row['correo_gmail'] if pd.notna(row['correo_gmail']) else '',
            'correo_corporativo': row['correo_corporativo'] if pd.notna(row['correo_corporativo']) else '',
            'condicion_lap': row['condicion_lap'] if pd.notna(row['condicion_lap']) else '',
            'cargador': row['cargador'] if pd.notna(row['cargador']) else '',
            'comentarios': row['comentarios'] if pd.notna(row['comentarios']) else '',
            'precio': formatear_precio(row['precio']),
            'precio_letras': precio_a_letras(row['precio'])
        }
        
        # Renderizar y guardar
        plantilla.render(contexto)
        nombre_archivo = f"Responsiva laptop {row['empleado'].title()}-{row['marca']}-{row['numero_serie']}.docx"
        output_path = Path(output_dir) / nombre_archivo
        plantilla.save(output_path)
        print(f"✅ {nombre_archivo} generado.")
    
    print(f"\n🎯 Total: {len(df_responsivas)} responsivas generadas en '{output_dir}'")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    # Configuración de rutas
    paths = get_files_path()
    plantilla_path = paths['dir_plantillas'] / "plantilla_laptops.docx"
    output_dir = paths['dir_responsivas'] / "Responsivas Laptops"
    output_dir.mkdir(exist_ok=True)
    
    # Conectar y traer los datos
    engine = get_engine()
    
    query = """
    SELECT
	rlap.fecha_entrega,
	CONCAT_WS(' ',emp.nombre, emp.apellido_paterno, emp.apellido_materno) AS empleado,
	suc.nombre_sucursal AS sucursal,
	dep.nombre_departamento AS departamento,
	pue.nombre_puesto AS puesto,
	ilap.marca AS marca,
	ilap.modelo AS modelo,
	rlap.numero_serie AS numero_serie,
	ce.correo_gmail,
	ce.correo_corporativo,
	con.condicion_opcion as condicion_lap,
	car.cargador_opcion as cargador,
	ilap.comentarios,
	ilap.precio
	
	FROM responsivas_laptops rlap
	LEFT JOIN empleados emp ON rlap.codigo_empleado = emp.codigo
	LEFT JOIN sucursales suc ON emp.id_sucursal = suc.id_sucursal
	LEFT JOIN departamentos dep ON emp.id_departamento = dep.id_departamento
	LEFT JOIN puestos pue ON emp.id_puesto = pue.id_puesto
	LEFT JOIN inventario_laptops ilap ON rlap.numero_serie = ilap.numero_serie
	LEFT JOIN condicion con ON ilap.id_condicion = con.id_condicion
	LEFT JOIN cargadores car ON ilap.id_cargador = car.id_cargador
	LEFT JOIN(
		SELECT
			codigo_empleado,
			MAX(CASE WHEN id_tipo_correo = 2 THEN direccion_correo END) AS correo_gmail,
                MAX(CASE WHEN id_tipo_correo = 1 THEN direccion_correo END) AS correo_corporativo
            FROM correos_electronicos
            WHERE id_estatus_correo = 1  -- 👈 ACTIVO = 1
            GROUP BY codigo_empleado
	) ce ON rlap.codigo_empleado = ce.codigo_empleado
	ORDER BY rlap.fecha_entrega ASC, emp.nombre
    """
    
    df_responsivas = pd.read_sql_query(query, con=engine)
    
    print(f"✅ {len(df_responsivas)} responsivas de laptops cargadas desde la BDD.")
    
    # Generar los Word
    generar_responsivas_word(df_responsivas, plantilla_path, output_dir)