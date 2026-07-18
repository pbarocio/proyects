import sqlite3
import openpyxl
from pathlib import Path

def fill_branches(cursor):
    branches_list = [
        ("Corporativo",),
        ("La Barca",),
        ("La Piedad",),
        ("Morelia",),
        ("Pénjamo",),
        ("Poncitlán",),
        ("Zona Altos",)
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO branches (branch_name) 
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
    INSERT OR IGNORE INTO departments (department_name) 
    VALUES (?);
    """, departments_list)

    print(f"¡Se han cargado {cursor.rowcount} departments nuevas al catálogo de agrocisa_core.db!")
    
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
    INSERT OR IGNORE INTO positions (position_name) 
    VALUES (?);
    """, positions_list)

    print(f"¡Se han cargado {cursor.rowcount} positions nuevas al catálogo de agrocisa_core.db!")
    
def fill_box(cursor):
    box_list = [
        ("Con caja",),
        ("Sin caja",),
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO box (caja_type) 
    VALUES (?);
    """, box_list)

    print(f"¡Se han cargado {cursor.rowcount} box nuevas al catálogo de agrocisa_core.db!")

def fill_conditions(cursor):
    condition_list = [
        ("Nuevo (a)",),
        ("Usado (a)",),
        ("Buenas condiciones",),
        ("Media vida",),
        ("Obsoleto (a)",),
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO condition (condition_status) 
    VALUES (?);
    """, condition_list)

    print(f"¡Se han cargado {cursor.rowcount} condition nuevas al catálogo de agrocisa_core.db!")

def fill_hd_type(cursor):
    hd_type_list = [
        ("HDD",),
        ("SSD",),
        ("M2VMe",),
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO hd_type (hd_type_name) 
    VALUES (?);
    """, hd_type_list)

    print(f"¡Se han cargado {cursor.rowcount} hd_type nuevas al catálogo de agrocisa_core.db!")
    
def fill_renew(cursor):
    renew_list = [
        ("Sí",),
        ("No",),
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO renew (renew_option) 
    VALUES (?);
    """, renew_list)

    print(f"¡Se han cargado {cursor.rowcount} renew nuevas al catálogo de agrocisa_core.db!")
    
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
    INSERT OR IGNORE INTO chargers (charger_option) 
    VALUES (?);
    """, charger_list)

    print(f"¡Se han cargado {cursor.rowcount} 'charger_options' nuevas al catálogo de agrocisa_core.db!")
    
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
    INSERT OR IGNORE INTO phone_plans_2026 (plan_type, monthly_charge, mobile_data) 
    VALUES (?, ?, ?);
    """, plans_list)

    print(f"¡Se han cargado {cursor.rowcount} 'phone_plans_2026' nuevos al catálogo!")
    
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
    INSERT OR IGNORE INTO mobile_phones_2026 (name, price) 
    VALUES (?, ?);
    """, mobile_phones_list)

    print(f"¡Se han cargado {cursor.rowcount} 'mobile_phones_2026' nuevos al catálogo!")

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
    
    lines_to_insert = []
    
    # max_col=10 para asegurar que leemos desde Teléfono hasta Diferencia completo
    for row in sheet.iter_rows(min_row=2, max_col=10, values_only=True):
        
        if row[0] is None:
            continue
            
        # Mapeo estricto de las 10 columnas de tu Excel de la verdad
        phone_number = str(row[0]).split('.')[0].strip()
        is_mpp = str(row[1]).strip() if row[1] else None
        
        plan_2024 = str(row[2]).strip() if row[2] else None
        mensualidad_2024 = clean_money_value(row[3])
        gb_2024 = clean_gb_value(row[4])
        
        plan_2026 = str(row[5]).strip() if row[5] else None
        mensualidad_2026 = clean_money_value(row[6])
        
        # --- AQUÍ ESTÁ LO QUE TE HABÍA MOCHADO ---
        gb_base_2026 = clean_gb_value(row[7])       # Columna 7: GB normales del plan
        gb_promocion_2026 = clean_gb_value(row[8])  # Columna 8: GB con la promoción ganada
        
        cost_difference = clean_money_value(row[9])  # Columna 9: Diferencia de los $100
        
        id_usuario = None
        id_plan_2026 = plan_2026 
        
        # Empaquetamos la tupla con las 11 variables para la base de datos
        lines_to_insert.append((
            phone_number, id_usuario, id_plan_2026, is_mpp,
            plan_2024, mensualidad_2024, gb_2024,
            plan_2026, mensualidad_2026, gb_base_2026, gb_promocion_2026,
            cost_difference
        ))
        
    # Inserción limpia con todos los testigos guardados
    cursor.executemany("""
    INSERT OR IGNORE INTO mobile_lines (
        phone_number, id_usuario, id_plan_2026, is_mpp,
        plan_2024, mensualidad_2024, gb_2024,
        plan_2026, mensualidad_2026, gb_base_2026, gb_promocion_2026,
        cost_difference
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
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