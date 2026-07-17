import sqlite3

def main():
    connecction = sqlite3.connect("agrocisa_core.db")
    cursor = connecction.cursor()

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

    connecction.commit()
    print(f"¡Se han cargado {cursor.rowcount} sucursales nuevas al catálogo de agrocisa_core.db!")
    connecction.close()

# El mismo candado aquí para evitar cargas de datos por accidente
if __name__ == "__main__":
    main()