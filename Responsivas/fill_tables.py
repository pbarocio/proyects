import sqlite3
import openpyxl
from pathlib import Path

def fill_branches(cursor):
    branches_list = [
        ("La Barca",),
        ("Pénjamo",),
        ("La Piedad",),
        ("Morelia",),
        ("Poncitlán",),
        ("Zona Altos",),
        ("Corporativo",),
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO sucursales (nombre_sucursal) 
    VALUES (?);
    """, branches_list)

    print(f"¡Se han cargado {cursor.rowcount} sucursales nuevas al catálogo de agrocisa_core.db!")
    
def fill_departments(cursor):
    departments_list = [
        ("Agricultura Inteligente",),
        ("Capital Humano",),
        ("Compras",),
        ("Compras Internacionales",),
        ("Contabilidad",),
        ("Corporativo",),
        ("Crédito y Cobranza",),
        ("Dealer Standard",),
        ("Dirección",),
        ("Finanzas",),
        ("Jurídico",),
        ("Mantenimiento",),
        ("Maquinaria Agrícola",),
        ("Maquinaria Agrícola y Construcción",),
        ("Maquinaria Construcción",),
        ("Marketing",),
        ("Parque Vehicular",),
        ("Postventa",),
        ("Refacciones",),
        ("Servicio",),
        ("Sistemas",),
        ("Staff",),
        ("Vigilancia",),
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO departmentos (nombre_departamento) 
    VALUES (?);
    """, departments_list)

    print(f"¡Se han cargado {cursor.rowcount} departmentos nuevos al catálogo de agrocisa_core.db!")
    
def fill_positions(cursor):
    positions_list = [
        ("Almacenista",),
        ("Analista Comercial",),
        ("Analista de Refacciones y Servicio",),
        ("Analista de Ventas",),
        ("Analista Postventa",),
        ("Asesor de Refacciones Campo",),
        ("Asesor de Refacciones Mostrador",),
        ("Asesor de Ventas",),
        ("Asesor de Ventas en Línea",),
        ("Auxiliar Administrativo",),
        ("Auxiliar de Sistemas",),
        ("Cajera",),
        ("Chofer",),
        ("Dinamómetro",),
        ("Director",),
        ("Diseñador Gráfico",),
        ("DMS",),
        ("Encargado de Refacciones Sucursal",),
        ("Gerente de Sucursal",),
        ("Guardia",),
        ("Implementero",),
        ("Jefa Crédito y Cobranza",),
        ("Jefa de Finanzas",),
        ("Jefe Administrativo",),
        ("Jefe de Agricultura Inteligente",),
        ("Jefe de Capital Humano",),
        ("Jefe de Contabilidad",),
        ("Jefe de Mantenimiento",),
        ("Jefe de Marketing",),
        ("Jefe de Refacciones",),
        ("Jefe de Sistemas",),
        ("Jefe de Staff",),
        ("Jefe de Taller",),
        ("Jefe de Técnicos",),
        ("Jefe de Ventas Construcción",),
        ("Jefe Maquinaria Gama Alta",),
        ("Jefe Operativo",),
        ("Jefe Parque Vehicular",),
        ("Jefe Postventa",),
        ("Jefe Ventas Agrícola",),
        ("Logística",),
        ("Marketing Digital",),
        ("Marketing Experiencial",),
        ("Practicas Profesionales",),
        ("Promotor de Servicio",),
        ("Reclamos",),
        ("Reclutamiento",),
        ("Representante Legal",),
        ("Sin Asignar",),
        ("Técnico",),
        ("Telemetría",),
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO puestos (nombre_puesto) 
    VALUES (?);
    """, positions_list)

    print(f"¡Se han cargado {cursor.rowcount} puestos nuevos al catálogo de agrocisa_core.db!")
    
def fill_box(cursor):
    box_list = [
        ("Con caja",),
        ("Sin caja",),
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO caja (caja_opcion) 
    VALUES (?);
    """, box_list)

    print(f"¡Se han cargado {cursor.rowcount} caja_options nuevas al catálogo de agrocisa_core.db!")

def fill_conditions(cursor):
    condition_list = [
        ("Nuevo (a)",),
        ("Usado (a)",),
        ("Buenas condiciones",),
        ("Media vida",),
        ("Obsoleto (a)",),
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO condicion (condicion_opcion) 
    VALUES (?);
    """, condition_list)

    print(f"¡Se han cargado {cursor.rowcount} condicion_opcion nuevas al catálogo de agrocisa_core.db!")

def fill_hd_type(cursor):
    hd_type_list = [
        ("HDD",),
        ("SSD",),
        ("M2VMe",),
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO hd_tipo (hd_opcion) 
    VALUES (?);
    """, hd_type_list)

    print(f"¡Se han cargado {cursor.rowcount} hd_tipo nuevas al catálogo de agrocisa_core.db!")
    
def fill_renew(cursor):
    renew_list = [
        ("Sí",),
        ("No",),
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO renovacion (renovacion_opcion) 
    VALUES (?);
    """, renew_list)

    print(f"¡Se han cargado {cursor.rowcount} 'renovacion_opciones' nuevas al catálogo de agrocisa_core.db!")
    
def fill_chargers(cursor):
    charger_list = [
        ("CON Cargador Original y Cable Original",),
        ("CON Cargador Original y Cable Genérico",),
        ("CON Cargador y Cable Genéricos",),
        ("CON Cargador original SIN cable",),
        ("CON Cargador gernérico SIN Cable",),
        ("Sólo Cable",),
        ("SIN Cargador y SIN Cable",),
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO cargadores (cargador_opcion) 
    VALUES (?);
    """, charger_list)

    print(f"¡Se han cargado {cursor.rowcount} 'cargador_opciones' nuevas al catálogo de agrocisa_core.db!")
    
def fill_phone_plans(cursor):
    # Metemos los datos limpios de tu imagen
    # Estructura de la tupla: (Tipo, Mensualidad, GB)
    plans_list = [
        ("BASE", 229, 4.5),
        ("1", 269, 9.0),
        ("2", 329, 7.5),
        ("4", 599, 22.5),
        ("5", 649, 45.0)
    ]

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '?'
    cursor.executemany("""
    INSERT OR IGNORE INTO planes_telcel_2026 (nombre_plan, mensualidad, datos_incluidos) 
    VALUES (?, ?, ?);
    """, plans_list)

    print(f"¡Se han cargado {cursor.rowcount} 'planes_telcel_2026' nuevos al catálogo!")
    
def fill_mobile_phones_2026(cursor):
    # Metemos los datos limpios de tu imagen
    # Estructura de la tupla: (Tipo, Mensualidad, GB)
    mobile_phones_list = [
        ("Iphone 17 256", 19999),
        ("Iphone 17 Pro 256", 28499),
        ("Iphone 17 PRO MAX", 30999),
        ("Samsung S26+ 512GB", 33499),
        ("Samsung S25FE 128GB", 15499),
        ("Samsung Galaxy A36", 7499),
        ("Samsung Galaxy A56", 10999),
        ("Samsung S26 Ultra 512GB", 29999)
    ]

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '?'
    cursor.executemany("""
    INSERT OR IGNORE INTO equipos_2026 (marca_modelo, precio) 
    VALUES (?, ?);
    """, mobile_phones_list)

    print(f"¡Se han cargado {cursor.rowcount} 'equipos_2026' nuevos al catálogo!")

def clean_money_value(value):
    if value is None or str(value).strip() in ('N/A', ''):
        return None
    clean_val = str(value).replace('$', '').replace(',', '').strip()
    return float(clean_val)

def clean_gb_value(value):
    if value is None or str(value).strip() in ('N/A', ''):
        return None
    clean_val = str(value).replace(',', '.').strip()
    return float(clean_val)

def fill_mobile_lines(cursor, excel_path):
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    sheet = wb['Historico_Lineas_2026']
    
    COL_NUMERO = 0
    COL_MPP = 1
    COL_PLAN_2024 = 2
    COL_MENSUALIDAD_2024 = 3
    COL_GB_2024 = 4
    COL_PLAN_2026 = 5
    COL_MENSUALIDAD_2026 = 6
    COL_GB_BASE_2026 = 7
    COL_GB_PROMOCION_2026 = 8
    COL_DIFERENCIA_2024_2026 = 9
    
    lines_to_insert = []
    
    # max_col=10 para asegurar que leemos desde Teléfono hasta Diferencia completo
    for row in sheet.iter_rows(min_row=2, max_col=10, values_only=True):
        
        if row[COL_NUMERO] is None:
            continue
            
        # Mapeo estricto de las 10 columnas de tu Excel de la verdad
        numero = int(float(str(row[COL_NUMERO]).strip()))
        is_mpp = 1 if row[COL_MPP] else 0
        
        plan_2024 = str(row[COL_PLAN_2024]).strip() if row[COL_PLAN_2024] else None
        mensualidad_2024 = clean_money_value(row[COL_MENSUALIDAD_2024])
        gb_2024 = clean_gb_value(row[COL_GB_2024])
        
        plan_2026 = str(row[COL_PLAN_2026]).strip() if row[COL_PLAN_2026] else None
        mensualidad_2026 = clean_money_value(row[COL_MENSUALIDAD_2026])
        
        # --- AQUÍ ESTÁ LO QUE TE HABÍA MOCHADO ---
        gb_base_2026 = clean_gb_value(row[COL_GB_BASE_2026])       # Columna 7: GB normales del plan
        gb_promocion_2026 = clean_gb_value(row[COL_GB_PROMOCION_2026])  # Columna 8: GB con la promoción ganada
        
        cost_difference = clean_money_value(row[COL_DIFERENCIA_2024_2026])  # Columna 9: Diferencia de los $100
        
        id_usuario = None
        
        # Empaquetamos la tupla con las 11 variables para la base de datos
        lines_to_insert.append((
            numero, id_usuario, is_mpp,
            plan_2024, mensualidad_2024, gb_2024,
            plan_2026, mensualidad_2026, gb_base_2026, gb_promocion_2026,
            cost_difference
        ))
        
    # Inserción limpia con todos los testigos guardados
    cursor.executemany("""
    INSERT OR IGNORE INTO lineas_telcel (
        numero, id_usuario, is_mpp,
        plan_2024, mensualidad_2024, gb_2024,
        plan_2026, mensualidad_2026, gb_base_2026, gb_promocion_2026,
        cost_difference
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, lines_to_insert)
    
    print(f"¡Listo, carnal! Inyectadas {len(lines_to_insert)} líneas con el histórico y los gigas completos.")

# El mismo candado aquí para evitar cargas de datos por accidente
if __name__ == "__main__":
    connecction = sqlite3.connect("agrocisa_core.db")
    cursor = connecction.cursor()
    excel_wb = Path.home() / "git" / "pablo-contexto" / "Archivos_Responsivas" / "Directorio.xlsx"
    
    fill_branches(cursor)
    fill_departments(cursor)
    fill_positions(cursor)
    fill_box(cursor)
    fill_conditions(cursor)
    fill_hd_type(cursor)
    fill_renew(cursor)
    fill_chargers(cursor)
    fill_phone_plans(cursor)
    fill_mobile_phones_2026(cursor)
    fill_mobile_lines(cursor,excel_wb)
    
    connecction.commit()
    connecction.close()