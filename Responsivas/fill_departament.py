import sqlite3

def main():
    connecction = sqlite3.connect("agrocisa_core.db")
    cursor = connecction.cursor()

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

    connecction.commit()
    print(f"¡Se han cargado {cursor.rowcount} departments nuevas al catálogo de agrocisa_core.db!")
    connecction.close()

# El mismo candado aquí para evitar cargas de datos por accidente
if __name__ == "__main__":
    main()