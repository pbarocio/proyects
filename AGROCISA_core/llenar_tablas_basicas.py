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
    INSERT OR IGNORE INTO departamentos (nombre_departamento) 
    VALUES (?);
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
        ("Samsung S26 Ultra 512GB", 29999),
        ("Honor X5 Plus", 800)
    ]

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '?'
    cursor.executemany("""
    INSERT OR IGNORE INTO equipos_2026 (marca_modelo, precio) 
    VALUES (?, ?);
    """, mobile_phones_list)

    print(f"¡Se han cargado {cursor.rowcount} 'equipos_2026' nuevos al catálogo!")

def fill_mail_type(cursor):
    mail_type = [
        ("CORPORATIVO",),
        ("GMAIL",)
    ]

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '?'
    cursor.executemany("""
    INSERT OR IGNORE INTO tipos_correos_electronicos (tipo_correo) 
    VALUES (?);
    """, mail_type)

    print(f"¡Se han cargado {cursor.rowcount} 'tipos_correos_electronicos' nuevos al catálogo!")

def fill_mail_status(cursor):
    mail_status = [
        ("ACTIVO",),
        ("INACTIVO",)
    ]

    # En el INSERT mapeamos las 3 columnas correspondientes a las 3 '?'
    cursor.executemany("""
    INSERT OR IGNORE INTO estatus_correos_electronicos (estatus_correo) 
    VALUES (?);
    """, mail_status)

    print(f"¡Se han cargado {cursor.rowcount} 'estatus_correos' nuevos al catálogo!")

# El mismo candado aquí para evitar cargas de datos por accidente
if __name__ == "__main__":
    connecction = sqlite3.connect("agrocisa_core.db")
    cursor = connecction.cursor()
    excel_wb = Path.home() / "git" / "proyects" / "AGROCISA_core" / "Directorio.xlsx"
    
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
    
    connecction.commit()
    connecction.close()