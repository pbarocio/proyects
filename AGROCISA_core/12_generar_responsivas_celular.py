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
            'equipo': row['equipo'],
            'numero': str(row['numero']) if pd.notna(row['numero']) else '',
            'imei': str(row['imei']) if pd.notna(row['imei']) else '',
            'numero_serie': row['numero_serie'] if pd.notna(row['numero_serie']) else '',
            'correo_gmail': row['correo_gmail'] if pd.notna(row['correo_gmail']) else '',
            'correo_corporativo': row['correo_corporativo'] if pd.notna(row['correo_corporativo']) else '',
            'gb': str(row['gb']) if pd.notna(row['gb']) else '',
            'condicion': row['condicion'] if pd.notna(row['condicion']) else '',
            'cargador': row['cargador'] if pd.notna(row['cargador']) else '',
            'caja': row['caja'] if pd.notna(row['caja']) else '',
            'comentarios': row['comentarios'] if pd.notna(row['comentarios']) else '',
            'precio': formatear_precio(row['precio']),
            'precio_letras': precio_a_letras(row['precio'])
        }
        
        # Renderizar y guardar
        plantilla.render(contexto)
        nombre_archivo = f"Responsiva celular {row['empleado']} ({row['equipo']} {row['numero_serie']}).docx"
        output_path = Path(output_dir) / nombre_archivo
        plantilla.save(output_path)
        print(f"✅ {nombre_archivo} generado.")
    
    print(f"\n🎯 Total: {len(df_responsivas)} responsivas generadas en '{output_dir}'")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    # Configuración de rutas
    paths = get_files_path()
    plantilla_path = paths['dir_plantillas'] / "plantilla_celulares.docx"
    output_dir = paths['dir_responsivas'] / "Responsivas_Celulares"
    output_dir.mkdir(exist_ok=True)
    
    # Conectar y traer los datos
    engine = get_engine()
    
    query = """
    SELECT 
        r.fecha_entrega,
        CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS empleado,
        s.nombre_sucursal AS sucursal,
        d.nombre_departamento AS departamento,
        p.nombre_puesto AS puesto,
        eq.marca_modelo AS equipo,
        r.numero,
        r.imei,
        ic.numero_serie,
        ce.correo_gmail,
        ce.correo_corporativo,
        lt.gb_promocion_2026 AS gb,
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
        JOIN modelos_celulares eq ON ic.id_modelo = eq.id_modelo
        JOIN condicion c ON ic.id_condicion = c.id_condicion
        JOIN cargadores ca ON ic.id_cargador = ca.id_cargador
        JOIN caja ON ic.id_caja = caja.id_caja
        LEFT JOIN lineas_telefonicas lt ON r.numero = lt.numero
        LEFT JOIN (
            SELECT 
                codigo_empleado,
                MAX(CASE WHEN id_tipo_correo = 2 THEN direccion_correo END) AS correo_gmail,
                MAX(CASE WHEN id_tipo_correo = 1 THEN direccion_correo END) AS correo_corporativo
            FROM correos_electronicos
            WHERE id_estatus_correo = 1  -- 👈 ACTIVO = 1
            GROUP BY codigo_empleado
        ) ce ON e.codigo = ce.codigo_empleado
        ORDER BY r.fecha_entrega ASC, e.nombre;
    """
    
    df_responsivas = pd.read_sql_query(query, con=engine)
    #df_responsivas['fecha_entrega'] = pd.to_datetime(df_responsivas['fecha_entrega'])
    
    print(f"✅ {len(df_responsivas)} responsivas cargadas desde la BDD.")
    
    # Generar los Word
    generar_responsivas_word(df_responsivas, plantilla_path, output_dir)