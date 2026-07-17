import sqlite3

def main():
    # Toda la lógica de creación va aquí adentro protegida
    conexion = sqlite3.connect("agrocisa_core.db")
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS branches (
        id_branch INTEGER PRIMARY KEY AUTOINCREMENT,
        branch_name TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'sucursales' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id_department INTEGER PRIMARY KEY AUTOINCREMENT,
        department_name TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'departments' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS positions (
        id_position INTEGER PRIMARY KEY AUTOINCREMENT,
        position_name TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'positions' creada exitosamente en agrocisa_core.db!")

    conexion.commit()
    conexion.close()

# EL CANDADO SUPREMO:
# __name__ es una variable interna de Python. Si ejecutas el archivo directo en la consola, 
# Python le asigna el valor "__main__". Si lo asigna, corre la función main(). 
# Si alguien intenta importarlo desde otro script, __name__ valdrá otra cosa y la función NO se ejecutará.
if __name__ == "__main__":
    main()