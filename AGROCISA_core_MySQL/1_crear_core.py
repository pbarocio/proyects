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
    CREATE TABLE IF NOT EXISTS hdd_tipo (
        id_hdd_tipo INTEGER PRIMARY KEY AUTOINCREMENT,
        hdd_opcion TEXT NOT NULL UNIQUE
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
        CREATE TABLE IF NOT EXISTS tipos_correos_electronicos (
            id_tipo_correo INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_correo TEXT
        );
    """)
    
    print("¡Tabla 'tipos_correos_electronicos' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS estatus_correos_electronicos (
                id_estatus_correo INTEGER PRIMARY KEY AUTOINCREMENT,
                estatus_correo TEXT
            );
    """)
    
    print("¡Tabla 'estatus_correos' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatus_empleados (
            id_estatus_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
            estatus_empleado TEXT
        );
    """)
    
    print("¡Tabla 'estatus_empleado' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatus_celulares (
            id_estatus_celular INTEGER PRIMARY KEY AUTOINCREMENT,
            estatus_celular TEXT
        );
    """)
        
    print("¡Tabla 'estatus_celular' creada exitosamente en agrocisa_core.db!")
    
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
            zona TEXT,
            id_estatus_empleado INTEGER,
            FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal),
            FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento),
            FOREIGN KEY (id_puesto) REFERENCES puestos(id_puesto),
            FOREIGN KEY (numero_telefono) REFERENCES lineas_telcel(numero),
            FOREIGN KEY (id_estatus_empleado) REFERENCES estatus_empleados(id_estatus_empleado)
        );
        """)
    print("¡Tabla 'empleados' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS correos_electronicos (
            id_correo INTEGER PRIMARY KEY AUTOINCREMENT,
            direccion_correo TEXT NOT NULL,
            password TEXT,
            id_tipo_correo INTEGER,
            id_estatus_correo INTEGER,
            codigo_empleado INTEGER,
            FOREIGN KEY (id_tipo_correo) REFERENCES tipos_correos_electronicos(id_tipo_correo)
            FOREIGN KEY (id_estatus_correo) REFERENCES estatus_correos_electronicos(id_estatus_correo)
            FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo)
        );
    """)
        
    print("¡Tabla 'correos_electrónicos' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatus_linea_telefonica (
            id_estatus_linea INTEGER PRIMARY KEY AUTOINCREMENT,
            estatus_linea TEXT
        );
    """)
            
    print("¡Tabla 'estatus_linea_telefonica' creada exitosamente en agrocisa_core.db!")
    
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
            gb_2026 REAL,
            gb_promocion_2026 REAL,
            diferencia_2024_2026 REAL,
            id_estatus_linea INTEGER,
            FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo) ON DELETE SET NULL,
            FOREIGN KEY (id_estatus_linea) REFERENCES estatus_linea_telefonica (id_estatus_linea)
            );
    """)
        
    print("¡Tabla 'lineas_telefonicas' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_celulares (
        numero_renovacion INTEGER NULL,
        imei INTEGER PRIMARY KEY UNIQUE NOT NULL,
        numero_serie TEXT,
        mac_address TEXT,
        comentarios TEXT NULL,
        observaciones TEXT NULL,
        numero INTEGER NULL,
        id_equipo INTEGER NOT NULL,
        id_condicion INTEGER NULL,
        id_cargador INTEGER NULL,
        id_caja INTEGER NULL,
        fecha_entrega DATETIME,
        codigo_empleado INTEGER NULL,
        id_estatus_celular INTEGER,
        
        FOREIGN KEY (numero) REFERENCES lineas_telefonicas (numero)
        FOREIGN KEY (id_equipo) REFERENCES equipos_2026(id_equipo),
        FOREIGN KEY (id_condicion) REFERENCES condicion(id_condicion),
        FOREIGN KEY (id_cargador) REFERENCES cargadores(id_cargador),
        FOREIGN KEY (id_caja) REFERENCES caja(id_caja),
        FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo)
        FOREIGN KEY (id_estatus_celular) REFERENCES estatus_celulares(id_estatus_celular)
        );
    """)
    
    print("¡Tabla 'inventario_celulares' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatus_cpu (
            id_estatus_cpu INTEGER PRIMARY KEY AUTOINCREMENT,
            estatus_cpu TEXT
        );
    """)
            
    print("¡Tabla 'estatus_cpu' creada exitosamente en agrocisa_core.db!")  

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_cpu (
        hostname TEXT PRIMARY KEY NOT NULL,
        procesador TEXT,
        datos_memoria_ram TEXT,
        memoria_ram TEXT,
        id_hdd_tipo INTEGER,
        datos_almacenamiento TEXT,
        almacenamiento TEXT,
        motherboard TEXT,
        sistema_operativo TEXT,
        mac_address_lan TEXT,
        mac_address_wifi TEXT,
        precio INTEGER,
        comentarios TEXT,
        observaciones TEXT,
        fecha_mantenimiento DATETIME,
        id_condicion INTEGER,
        id_renovacion INTEGER,
        fecha_entrega DATETIME,
        codigo_empleado INTEGER,
        id_estatus_cpu INTEGER,
        
        FOREIGN KEY (id_hdd_tipo) REFERENCES hdd_tipo (id_hdd_tipo),
        FOREIGN KEY (id_condicion) REFERENCES condicion (id_condicion)
        FOREIGN KEY (id_renovacion) REFERENCES renovacion(id_renovacion),
        FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo),
        FOREIGN KEY (id_estatus_cpu) REFERENCES estatus_cpu(id_estatus_cpu)
        );
    """)
            
    print("¡Tabla 'inventario_cpu' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatus_laptops (
            id_estatus_laptops INTEGER PRIMARY KEY AUTOINCREMENT,
            estatus_laptop TEXT
        );
    """)
            
    print("¡Tabla 'estatus_laptops' creada exitosamente en agrocisa_core.db!")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_laptops (
        hostname TEXT,
        marca TEXT,
        modelo TEXT,
        numero_serie TEXT PRIMARY KEY NOT NULL,
        procesador TEXT,
        datos_memoria_ram TEXT,
        memoria_ram TEXT,
        datos_almacenamiento TEXT,
        almacenamiento TEXT,
        motherboard TEXT,
        sistema_operativo TEXT,
        mac_address_lan TEXT,
        mac_address_wifi TEXT,
        precio INTEGER,
        comentarios TEXT,
        observaciones TEXT,
        id_hdd_tipo INTEGER,
        id_cargador INTEGER,
        id_condicion INTEGER,
        id_renovacion INTEGER,
        fecha_entrega DATETIME,
        codigo_empleado INTEGER,
        id_estatus_laptop INTEGER,
        
        FOREIGN KEY (id_hdd_tipo) REFERENCES hdd_tipo (id_hdd_tipo),
        FOREIGN KEY (id_cargador) REFERENCES cargadores (id_cargador)
        FOREIGN KEY (id_condicion) REFERENCES condicion (id_condicion)
        FOREIGN KEY (id_renovacion) REFERENCES renovacion(id_renovacion),
        FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo),
        FOREIGN KEY (id_estatus_laptop) REFERENCES estatus_laptops(id_estatus_laptop)
        );
    """)
            
    print("¡Tabla 'inventario_laptops' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatus_monitores (
            id_estatus_monitor INTEGER PRIMARY KEY AUTOINCREMENT,
            estatus_monitor TEXT
        );
    """)
            
    print("¡Tabla 'estatus_monitores' creada exitosamente en agrocisa_core.db!")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_monitores (
        hostname TEXT,
        marca TEXT,
        modelo TEXT,
        numero_serie TEXT PRIMARY KEY NOT NULL,
        resolucion TEXT,
        precio INTEGER,
        comentarios TEXT,
        observaciones TEXT,
        id_condicion INTEGER,
        id_renovacion INTEGER,
        fecha_entrega DATETIME,
        codigo_empleado INTEGER,
        id_estatus_monitor INTEGER,
        
        FOREIGN KEY (id_condicion) REFERENCES condicion (id_condicion),
        FOREIGN KEY (id_renovacion) REFERENCES renovacion(id_renovacion),
        FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo),
        FOREIGN KEY (id_estatus_monitor) REFERENCES estatus_monitores(id_estatus_monitor)
        );
    """)
            
    print("¡Tabla 'inventario_monitores' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatus_tablets (
            id_estatus_tablet INTEGER PRIMARY KEY AUTOINCREMENT,
            estatus_tablet TEXT
        );
    """)
            
    print("¡Tabla 'estatus_tablets' creada exitosamente en agrocisa_core.db!")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_tablets (
        marca TEXT,
        modelo TEXT,
        imei INTEGER,
        numero_serie TEXT PRIMARY KEY NOT NULL,
        mac_address TEXT,
        precio INTEGER,
        comentarios TEXT,
        observaciones TEXT,
        id_condicion INTEGER,
        id_cargador INTEGER,
        fecha_entrega DATETIME,
        codigo_empleado INTEGER,
        id_estatus_tablet INTEGER,
        
        FOREIGN KEY (id_condicion) REFERENCES condicion (id_condicion)
        FOREIGN KEY (id_cargador) REFERENCES cargadores(id_cargador),
        FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo),
        FOREIGN KEY (id_estatus_tablet) REFERENCES estatus_tablets(id_estatus_tablet)
        );
    """)
    
    print("¡Tabla 'inventario_tablets' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsivas_celulares (
        id_responsiva_celular INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_entrega DATETIME NOT NULL,
        codigo_empleado INTEGER,
        numero INTEGER,
        imei INTEGER,
        
        FOREIGN KEY (codigo_empleado) REFERENCES empleados (codigo)
        FOREIGN KEY (numero) REFERENCES lineas_telefonicas(numero),
        FOREIGN KEY (imei) REFERENCES inventario_celulares(imei)
        );
    """)
        
    print("¡Tabla 'responsivas_celulares' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsivas_cpu (
        id_responsiva_cpu INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_entrega DATETIME NOT NULL,
        codigo_empleado INTEGER,
        hostname TEXT,
        
        FOREIGN KEY (codigo_empleado) REFERENCES empleados (codigo),
        FOREIGN KEY (hostname) REFERENCES inventario_cpu(hostname)
        );
    """)
        
    print("¡Tabla 'responsivas_cpu' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsivas_laptops (
        id_responsiva_cpu INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_entrega DATETIME NOT NULL,
        codigo_empleado INTEGER,
        numero_serie TEXT,
        
        FOREIGN KEY (codigo_empleado) REFERENCES empleados (codigo),
        FOREIGN KEY (numero_serie) REFERENCES inventario_laptops(numero_serie)
        );
    """)
        
    print("¡Tabla 'responsivas_laptops' creada exitosamente en agrocisa_core.db!")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsivas_monitores (
        id_responsiva_cpu INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_entrega DATETIME NOT NULL,
        codigo_empleado INTEGER,
        numero_serie TEXT,
        
        FOREIGN KEY (codigo_empleado) REFERENCES empleados (codigo),
        FOREIGN KEY (numero_serie) REFERENCES inventario_monitores(numero_serie)
        );
    """)
        
    print("¡Tabla 'responsivas_monitores' creada exitosamente en agrocisa_core.db!")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsivas_tablets (
        id_responsiva_cpu INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha_entrega DATETIME NOT NULL,
        codigo_empleado INTEGER,
        numero_serie TEXT,
        
        FOREIGN KEY (codigo_empleado) REFERENCES empleados (codigo),
        FOREIGN KEY (numero_serie) REFERENCES inventario_tablets(numero_serie)
        );
    """)
        
    print("¡Tabla 'responsivas_tablets' creada exitosamente en agrocisa_core.db!")
    
    conexion.commit()
    conexion.close()

# EL CANDADO SUPREMO:
# __name__ es una variable interna de Python. Si ejecutas el archivo directo en la consola, 
# Python le asigna el valor "__main__". Si lo asigna, corre la función main(). 
# Si alguien intenta importarlo desde otro script, __name__ valdrá otra cosa y la función NO se ejecutará.
if __name__ == "__main__":
    main()