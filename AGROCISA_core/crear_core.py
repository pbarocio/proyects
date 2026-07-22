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
    CREATE TABLE IF NOT EXISTS departamentos (
        id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
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
    CREATE TABLE IF NOT EXISTS lineas_telefonicas (
        numero INTEGER PRIMARY KEY,
        codigo_empleado INTEGER NULL,
        is_mpp INTEGER NULL,
        plan_2024 TEXT,
        mensualidad_2024 REAL,
        gb_2024 REAL,
        plan_2026 TEXT,
        mensualidad_2026 REAL,
        gb_base_2026 REAL,
        gb_promocion_2026 REAL,
        cost_difference REAL,
        FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo) ON DELETE SET NULL
        );
    """)
    
    print("¡Tabla 'lineas_telcel' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS empleados (
        codigo INTEGER PRIMARY KEY,
        apellido_paterno TEXT,
        apellido_materno TEXT,
        nombre TEXT,
        id_sucursal INTEGER,
        id_departamento INTEGER,
        id_puesto INTEGER,
        numero_telefono INTEGER,
        FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal),
        FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento),
        FOREIGN KEY (id_puesto) REFERENCES puestos(id_puesto),
        FOREIGN KEY (numero_telefono) REFERENCES lineas_telcel(numero)
    );
    """)
    print("¡Tabla 'empleados' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS correos_electronicos (
            id_correo INTEGER PRIMARY KEY AUTOINCREMENT,
            direccion_correo TEXT UNIQUE NOT NULL,
            password TEXT,
            tipo_correo TEXT,
            codigo_empleado INTEGER,
            estatus TEXT DEFAULT 'ACTIVO',
            FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo)
        );
    """)
    
    print("¡Tabla 'correos_electrónicos' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_celulares (
        id_celular INTEGER PRIMARY KEY AUTOINCREMENT,
        
        -- DATOS ÚNICOS DEL HARDWARE
        numero_renovacion INTEGER NULL,             -- Sacada de la hoja 'Inventario Celulares'
        imei TEXT UNIQUE NOT NULL,                  -- Sacada de la hoja 'Inventario Celulares'
        numero_serie TEXT,                          -- Sacada de la hoja 'Inventario Celulares'
        mac_address TEXT,                           -- Sacada de la hoja 'Inventario Celulares'
        fecha_entrega DATE NULL,                    -- (Dato temporal para no hacer cagadero, una vez que se migre a la BDD oficial se quita)... Para no volver a leer el excel y hacer un desmadre de script
        comentarios TEXT NULL,                      -- Sacada de la hoja 'Inventario Celulares (Comentarios libres para responsivas)'
        observaciones TEXT NULL,                    -- Sacada de la hoja 'Inventario Celulares (observaciones libres para TI)'
        
        -- FOREIGN KEYS A CATÁLOGOS BASE
        numero INTEGER NULL,                        -- FK a 'lineas_telefonicas' (numero) -- Para responsiva(gb_promocion_2026)
        id_equipo INTEGER NOT NULL,                 -- FK a 'equipos_2026' (id_equipo) Para responsiva -- (Marca_Modelo,Precio)
        id_condicion INTEGER NULL,                  -- FK a 'condicion' (condicion_opcion) Para responsiva(condicion_opcion) -- Sacada de la hoja 'Inventario Celulares'
        id_cargador INTEGER NULL,                   -- FK a 'cargadores' (id_cargador) Pra responsiva (cargador_opcion) -- Sacada de la hoja 'Inventario Celulares
        id_caja INTEGER NULL,                       -- FK a 'caja' (caja_opcion) -- Sacada de la hoja 'Inventario Celulares
        codigo_empleado INTEGER NULL,               -- FK a 'empleados' (codigo) --- De aquí con consulta sacamos Nombre Completo, Sucursal, Puesto, Correo Gmail, Correo Institucional
        
        -- DEFINICIÓN OFICIAL DE RELACIONES
        FOREIGN KEY (numero) REFERENCES lineas_telefonicas (numero)
        FOREIGN KEY (id_equipo) REFERENCES equipos_2026(id_equipo),
        FOREIGN KEY (id_condicion) REFERENCES condicion(condicion_opcion),
        FOREIGN KEY (id_cargador) REFERENCES cargadores(id_cargador),
        FOREIGN KEY (id_caja) REFERENCES cajas(caja_opcion),
        FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo)
        );
    """)
    
    print("¡Tabla 'inventario_celulares' creada exitosamente en agrocisa_core.db!")
    
    conexion.commit()
    conexion.close()

# EL CANDADO SUPREMO:
# __name__ es una variable interna de Python. Si ejecutas el archivo directo en la consola, 
# Python le asigna el valor "__main__". Si lo asigna, corre la función main(). 
# Si alguien intenta importarlo desde otro script, __name__ valdrá otra cosa y la función NO se ejecutará.
if __name__ == "__main__":
    main()