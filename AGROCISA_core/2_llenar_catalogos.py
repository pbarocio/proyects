from db_config import get_connection
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
    INSERT IGNORE INTO sucursales (nombre_sucursal) 
    VALUES (%s);
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
        ("Corporativo Operativo",),
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
        ("Sin Asignar",),
        ("Sistemas",),
        ("Staff",),
        ("Vigilancia",),
    ]

    cursor.executemany("""
    INSERT IGNORE INTO departamentos (nombre_departamento) 
    VALUES (%s);
    """, departments_list)

    print(f"¡Se han cargado {cursor.rowcount} 'departamentos' nuevos al catálogo de agrocisa_core.db!")
    
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
        ("Director",),
        ("Diseñador Gráfico",),
        ("DMS",),
        ("Encargado de Refacciones Sucursal",),
        ("Gerente de Sucursal",),
        ("Guardia",),
        ("Implementero",),
        ("Jefa Crédito y Cobranza",),
        ("Jefa de Finanzas",),
        ("Jefe de Agricultura Inteligente",),
        ("Jefe de Capital Humano",),
        ("Jefe de Compras",),
        ("Jefe de Contabilidad",),
        ("Jefe de Mantenimiento",),
        ("Jefe de Marketing",),
        ("Jefe de Refacciones",),
        ("Jefe de Servicio",),
        ("Jefe de Servicio Administrativo",),
        ("Jefe de Servicio Operativo",),
        ("Jefe de Sistemas",),
        ("Jefe de Staff",),
        ("Jefe de Taller",),
        ("Jefe de Técnicos",),
        ("Jefe de Técnicos Gama Alta",),
        ("Jefe de Ventas Construcción",),
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
        ("Técnico Dinamómetro",),
        ("Telemetría",),
    ]

    cursor.executemany("""
    INSERT IGNORE INTO puestos (nombre_puesto) 
    VALUES (%s);
    """, positions_list)

    print(f"¡Se han cargado {cursor.rowcount} puestos nuevos al catálogo de agrocisa_core.db!")
    
def fill_box(cursor):
    box_list = [
        ("Con caja",),
        ("Sin caja",),
    ]

    cursor.executemany("""
    INSERT IGNORE INTO caja (caja_opcion) 
    VALUES (%s);
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
    INSERT IGNORE INTO condicion (condicion_opcion) 
    VALUES (%s);
    """, condition_list)

    print(f"¡Se han cargado {cursor.rowcount} condicion_opcion nuevas al catálogo de agrocisa_core.db!")

def fill_hd_type(cursor):
    hd_type_list = [
        ("HDD",),
        ("SSD",),
        ("M2VMe",),
    ]

    cursor.executemany("""
    INSERT IGNORE INTO hdd_tipo (hdd_opcion) 
    VALUES (%s);
    """, hd_type_list)

    print(f"¡Se han cargado {cursor.rowcount} hd_tipo nuevas al catálogo de agrocisa_core.db!")
    
def fill_renew(cursor):
    renew_list = [
        ("Sí",),
        ("No",),
    ]

    cursor.executemany("""
    INSERT IGNORE INTO renovacion (renovacion_opcion) 
    VALUES (%s);
    """, renew_list)

    print(f"¡Se han cargado {cursor.rowcount} 'renovacion_opciones' nuevas al catálogo de agrocisa_core.db!")
    
def fill_chargers(cursor):
    charger_list = [
        ("CON Cargador Original y Cable Original",),
        ("CON Cargador Original y Cable Genérico",),
        ("CON Cargador y Cable Genéricos",),
        ("CON Cargador original SIN cable",),
        ("CON Cargador genérico SIN Cable",),
        ("Sólo Cable",),
        ("SIN Cargador y SIN Cable",),
    ]

    cursor.executemany("""
    INSERT IGNORE INTO cargadores (cargador_opcion) 
    VALUES (%s);
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

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '%s'
    cursor.executemany("""
    INSERT IGNORE INTO planes_telcel_2026 (nombre_plan, mensualidad, datos_incluidos) 
    VALUES (%s, %s, %s);
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
        ("Samsung S26 Ultra 512GB", 29999),
        ("Honor X5 Plus", 800)
    ]

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '%s'
    cursor.executemany("""
    INSERT IGNORE INTO equipos_2026 (marca_modelo, precio) 
    VALUES (%s, %s);
    """, mobile_phones_list)

    print(f"¡Se han cargado {cursor.rowcount} 'equipos_2026' nuevos al catálogo!")

def fill_mail_type(cursor):
    mail_type = [
        ("CORPORATIVO",),
        ("GMAIL",)
    ]

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '%s'
    cursor.executemany("""
    INSERT IGNORE INTO tipos_correos_electronicos (tipo_correo) 
    VALUES (%s);
    """, mail_type)

    print(f"¡Se han cargado {cursor.rowcount} 'tipos_correos_electronicos' nuevos al catálogo!")

def fill_mail_status(cursor):
    mail_status = [
        ("ACTIVO",),
        ("INACTIVO",)
    ]

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '%s'
    cursor.executemany("""
    INSERT IGNORE INTO estatus_correos_electronicos (estatus_correo) 
    VALUES (%s);
    """, mail_status)

    print(f"¡Se han cargado {cursor.rowcount} 'estatus_correos' nuevos al catálogo!")
    
def fill_employee_status(cursor):
    employee_status = [
        ("ACTIVO",),
        ("INACTIVO",)
    ]
    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '%s'
    cursor.executemany("""
    INSERT IGNORE INTO estatus_empleados (estatus_empleado) 
    VALUES (%s);
    """, employee_status)

    print(f"¡Se han cargado {cursor.rowcount} 'estatus_empleado' nuevos al catálogo!")
    
def fill_mobile_phone_status(cursor):
    mobile_phone_status = [
        ("ACTIVO",),
        ("INACTIVO",)
    ]

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '%s'
    cursor.executemany("""
    INSERT IGNORE INTO estatus_celulares (estatus_celular) 
    VALUES (%s);
    """, mobile_phone_status)

    print(f"¡Se han cargado {cursor.rowcount} 'estatus_celulares' nuevos al catálogo!")
    
def fill_mobile_line_status(cursor):
    mobile_line_status = [
        ("ACTIVO",),
        ("INACTIVO",)
    ]

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '%s'
    cursor.executemany("""
    INSERT IGNORE INTO estatus_linea_telefonica (estatus_linea) 
    VALUES (%s);
    """, mobile_line_status)

    print(f"¡Se han cargado {cursor.rowcount} 'estatus_linea_telefonica' nuevos al catálogo!")
    
def fill_cpu_status(cursor):
    cpu_status = [
        ("ACTIVO",),
        ("INACTIVO",)
    ]

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '%s'
    cursor.executemany("""
    INSERT IGNORE INTO estatus_cpu (estatus_cpu) 
    VALUES (%s);
    """, cpu_status)

    print(f"¡Se han cargado {cursor.rowcount} 'estatus_cpu' nuevos al catálogo!")
    
def fill_laptops_status(cursor):
    laptops_status = [
        ("ACTIVO",),
        ("INACTIVO",)
    ]

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '%s'
    cursor.executemany("""
    INSERT IGNORE INTO estatus_laptops (estatus_laptop) 
    VALUES (%s);
    """, laptops_status)

    print(f"¡Se han cargado {cursor.rowcount} 'estatus_laptop' nuevos al catálogo!")

def fill_monitor_status(cursor):
    monitor_status = [
        ("ACTIVO",),
        ("INACTIVO",)
    ]

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '%s'
    cursor.executemany("""
    INSERT IGNORE INTO estatus_monitores (estatus_monitor) 
    VALUES (%s);
    """, monitor_status)

    print(f"¡Se han cargado {cursor.rowcount} 'estatus_monitor' nuevos al catálogo!")
            
def fill_tablets_status(cursor):
    tablets_status = [
        ("ACTIVO",),
        ("INACTIVO",)
    ]

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '%s'
    cursor.executemany("""
    INSERT IGNORE INTO estatus_tablets (estatus_tablet) 
    VALUES (%s);
    """, tablets_status)

    print(f"¡Se han cargado {cursor.rowcount} 'estatus_tablets' nuevos al catálogo!")

# El mismo candado aquí para evitar cargas de datos por accidente
if __name__ == "__main__":
    connecction = get_connection()
    cursor = connecction.cursor()
    #excel_wb = Path.home() / "git" / "proyects" / "AGROCISA_core" / "Directorio 2026-07-21 martes.xlsx"
    
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
    fill_mail_type(cursor)
    fill_mail_status(cursor)
    fill_employee_status(cursor)
    fill_mobile_phone_status(cursor)
    fill_mobile_line_status(cursor)
    fill_cpu_status(cursor) 
    fill_monitor_status(cursor)
    fill_tablets_status(cursor)
    connecction.commit()
    connecction.close()