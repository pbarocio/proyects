import sqlite3

def main():
    # Toda la lógica de creación va aquí adentro protegida
    conexion = sqlite3.connect("agrocisa_core.db")
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sucursales (
        id_sucursal INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_sucursal TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'sucursales' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departmentos (
        id_departmento INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_departamento TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'departamentos' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS puestos (
        id_puesto INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_puesto TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'puestos' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS caja (
        id_caja INTEGER PRIMARY KEY AUTOINCREMENT,
        caja_opcion TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'caja' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS condicion (
        id_condicion INTEGER PRIMARY KEY AUTOINCREMENT,
        condicion_opcion TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'condicion' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hd_tipo (
        id_hd_tipo INTEGER PRIMARY KEY AUTOINCREMENT,
        hd_opcion TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'hd_tipo' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS renovacion (
        id_renovacion INTEGER PRIMARY KEY AUTOINCREMENT,
        renovacion_opcion TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'renovacion' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cargadores (
        id_cargador INTEGER PRIMARY KEY AUTOINCREMENT,
        cargador_opcion TEXT NOT NULL UNIQUE
    );
    """)
    
    print("¡Tabla 'cargadores' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS planes_telcel_2026 (
        id_plan INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_plan TEXT NOT NULL UNIQUE,
        mensualidad INTEGER NOT NULL,
        datos_incluidos REAL NOT NULL
    );
    """)
    
    print("¡Tabla 'planes_telcel_2026' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS equipos_2026 (
        id_equipo INTEGER PRIMARY KEY AUTOINCREMENT,
        marca_modelo TEXT NOT NULL UNIQUE,
        precio INTEGER NOT NULL
    );
    """)
    
    print("¡Tabla 'equipos_2026' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lineas_telcel (
        numero INTEGER PRIMARY KEY,
        id_usuario INTEGER NULL,
        is_mpp INTEGER NULL,
        plan_2024 TEXT,
        mensualidad_2024 REAL,
        gb_2024 REAL,
        plan_2026 TEXT,
        mensualidad_2026 REAL,
        gb_base_2026 REAL,
        gb_promocion_2026 REAL,
        cost_difference REAL
        );
    """)
    
    print("¡Tabla 'lineas_telcel' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS empleados (
        codigo INTEGER PRIMARY KEY,
        apellido_paterno TEXT,
        apellido_materno TEXT,
        nombre TEXT,
        numero_telefono INTEGER UNIQUE,
        FOREIGN KEY (numero_telefono) REFERENCES lineas_telcel(numero)
    );
    """)
    print("¡Tabla 'empleados' creada exitosamente en agrocisa_core.db!")

    conexion.commit()
    conexion.close()

# EL CANDADO SUPREMO:
# __name__ es una variable interna de Python. Si ejecutas el archivo directo en la consola, 
# Python le asigna el valor "__main__". Si lo asigna, corre la función main(). 
# Si alguien intenta importarlo desde otro script, __name__ valdrá otra cosa y la función NO se ejecutará.
if __name__ == "__main__":
    main()