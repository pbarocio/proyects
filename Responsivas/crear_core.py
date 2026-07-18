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
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS box (
        id_caja INTEGER PRIMARY KEY AUTOINCREMENT,
        caja_type TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'box' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS condition (
        id_condition INTEGER PRIMARY KEY AUTOINCREMENT,
        condition_status TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'condition' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hd_type (
        id_hd_type INTEGER PRIMARY KEY AUTOINCREMENT,
        hd_type_name TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'hd_type' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS renew (
        id_renew_option INTEGER PRIMARY KEY AUTOINCREMENT,
        renew_option TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'renew' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chargers (
        id_charger_option INTEGER PRIMARY KEY AUTOINCREMENT,
        charger_option TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'chargers' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS phone_plans_2026 (
        id_plan INTEGER PRIMARY KEY AUTOINCREMENT,
        plan_type TEXT NOT NULL UNIQUE,
        monthly_charge INTEGER NOT NULL,
        mobile_data REAL NOT NULL
    );
    """)
    
    print("¡Tabla 'phone_plans_2026' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mobile_phones_2026 (
        id_mobile_phone INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        price INTEGER NOT NULL
    );
    """)
    
    print("¡Tabla 'mobile_phones_2026' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mobile_lines (
        phone_number TEXT PRIMARY KEY,
        id_usuario INTEGER NULL,
        id_plan_2026 INTEGER,
        is_mpp TEXT NULL,
        
        -- EL HISTÓRICO COMPLETO (Sin mutilaciones, carnal)
        plan_2024 TEXT,
        mensualidad_2024 REAL,
        gb_2024 REAL,
        
        plan_2026 TEXT,
        mensualidad_2026 REAL,
        gb_base_2026 REAL,         -- <-- Aquí guardamos la columna 7 que te borré
        gb_promocion_2026 REAL,    -- <-- Aquí van tus 105 GB o los 22.5 GB
        cost_difference REAL
        );
    """)
    
    print("¡Tabla 'mobile_lines' creada exitosamente en agrocisa_core.db!")

    conexion.commit()
    conexion.close()

# EL CANDADO SUPREMO:
# __name__ es una variable interna de Python. Si ejecutas el archivo directo en la consola, 
# Python le asigna el valor "__main__". Si lo asigna, corre la función main(). 
# Si alguien intenta importarlo desde otro script, __name__ valdrá otra cosa y la función NO se ejecutará.
if __name__ == "__main__":
    main()