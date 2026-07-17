import sqlite3

def main():
    connecction = sqlite3.connect("agrocisa_core.db")
    cursor = connecction.cursor()

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

    connecction.commit()
    print(f"¡Se han cargado {cursor.rowcount} positions nuevas al catálogo de agrocisa_core.db!")
    connecction.close()

# El mismo candado aquí para evitar cargas de datos por accidente
if __name__ == "__main__":
    main()