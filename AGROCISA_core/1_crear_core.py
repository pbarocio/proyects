from db_config import get_connection


def main():
    # Toda la lógica de creación va aquí adentro protegida
    conexion = get_connection()
    cursor = conexion.cursor()
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sucursales (
        id_sucursal INT PRIMARY KEY AUTO_INCREMENT,
        nombre_sucursal VARCHAR(100) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'sucursales' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS departamentos (
        id_departamento INT PRIMARY KEY AUTO_INCREMENT,
        nombre_departamento VARCHAR(100) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'departamentos' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS puestos (
        id_puesto INT PRIMARY KEY AUTO_INCREMENT,
        nombre_puesto VARCHAR(100) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'puestos' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS caja (
        id_caja INT PRIMARY KEY AUTO_INCREMENT,
        caja_opcion VARCHAR(100) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'caja' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS condicion (
        id_condicion INT PRIMARY KEY AUTO_INCREMENT,
        condicion_opcion VARCHAR(100) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'condicion' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hdd_tipo (
        id_hdd_tipo INT PRIMARY KEY AUTO_INCREMENT,
        hdd_opcion VARCHAR(100) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'hd_tipo' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS renovacion (
        id_renovacion INT PRIMARY KEY AUTO_INCREMENT,
        renovacion_opcion VARCHAR(100) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'renovacion' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cargadores (
        id_cargador INT PRIMARY KEY AUTO_INCREMENT,
        cargador_opcion VARCHAR(100) NOT NULL UNIQUE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'cargadores' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS planes_telcel_2026 (
        id_plan INT PRIMARY KEY AUTO_INCREMENT,
        nombre_plan VARCHAR(100) NOT NULL UNIQUE,
        mensualidad INT NOT NULL,
        datos_incluidos DECIMAL(10,2) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'planes_telcel_2026' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS modelos_celulares (
        id_modelo INT PRIMARY KEY AUTO_INCREMENT,
        marca_modelo VARCHAR(100) NOT NULL UNIQUE,
        precio VARCHAR(5) NOT NULL,
        ano_renovacion VARCHAR(4) NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'modelos_celulares' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tipos_correos_electronicos (
            id_tipo_correo INT PRIMARY KEY AUTO_INCREMENT,
            tipo_correo VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'tipos_correos_electronicos' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS estatus_correos_electronicos (
                id_estatus_correo INT PRIMARY KEY AUTO_INCREMENT,
                estatus_correo VARCHAR(100)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'estatus_correos' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatus_empleados (
            id_estatus_empleado INT PRIMARY KEY AUTO_INCREMENT,
            estatus_empleado VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'estatus_empleado' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatus_celulares (
            id_estatus_celular INT PRIMARY KEY AUTO_INCREMENT,
            estatus_celular VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
        
    print("¡Tabla 'estatus_celular' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatus_linea_telefonica (
            id_estatus_linea INT PRIMARY KEY AUTO_INCREMENT,
            estatus_linea VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
            
    print("¡Tabla 'estatus_linea_telefonica' creada exitosamente en agrocisa_core.db!")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatus_cpu (
            id_estatus_cpu INT PRIMARY KEY AUTO_INCREMENT,
            estatus_cpu VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
            
    print("¡Tabla 'estatus_cpu' creada exitosamente en agrocisa_core.db!") 

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatus_laptops (
            id_estatus_laptops INT PRIMARY KEY AUTO_INCREMENT,
            estatus_laptop VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
            
    print("¡Tabla 'estatus_laptops' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatus_monitores (
            id_estatus_monitor INT PRIMARY KEY AUTO_INCREMENT,
            estatus_monitor VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
            
    print("¡Tabla 'estatus_monitores' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estatus_tablets (
            id_estatus_tablet INT PRIMARY KEY AUTO_INCREMENT,
            estatus_tablet VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
            
    print("¡Tabla 'estatus_tablets' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleados (
            codigo VARCHAR(20) PRIMARY KEY,
            apellido_paterno VARCHAR(100),
            apellido_materno VARCHAR(100),
            nombre VARCHAR(100),
            id_sucursal INT,
            id_departamento INT,
            id_puesto INT,
            numero_telefono VARCHAR(20),
            id_estatus_empleado INT,
            FOREIGN KEY (id_sucursal) REFERENCES sucursales(id_sucursal),
            FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento),
            FOREIGN KEY (id_puesto) REFERENCES puestos(id_puesto),
            FOREIGN KEY (numero_telefono) REFERENCES lineas_telcel(numero),
            FOREIGN KEY (id_estatus_empleado) REFERENCES estatus_empleados(id_estatus_empleado)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """)
    
    print("¡Tabla 'empleados' creada exitosamente en agrocisa_core.db!")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lineas_telefonicas (
            numero VARCHAR(20) PRIMARY KEY,
            is_mpp BOOLEAN NULL,
            knox BOOLEAN NULL,
            comentarios TEXT,
            plan_2024 VARCHAR(100),
            mensualidad_2024 DECIMAL(10,2),
            gb_2024 DECIMAL(10,2),
            plan_2026 VARCHAR(100),
            mensualidad_2026 DECIMAL(10,2),
            gb_2026 DECIMAL(10,2),
            gb_promocion_2026 DECIMAL(10,2),
            diferencia_2024_2026 DECIMAL(10,2),
            codigo_empleado VARCHAR(20) NULL,
            id_estatus_linea INT,
            FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo) ON DELETE SET NULL,
            FOREIGN KEY (id_estatus_linea) REFERENCES estatus_linea_telefonica (id_estatus_linea)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
        
    print("¡Tabla 'lineas_telefonicas' creada exitosamente en agrocisa_core.db!")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS correos_electronicos (
            id_correo INT PRIMARY KEY AUTO_INCREMENT,
            direccion_correo VARCHAR(200) NOT NULL,
            password VARCHAR(100),
            alias TEXT,
            comentarios TEXT,
            id_tipo_correo INT,
            id_estatus_correo INT,
            codigo_empleado VARCHAR(20),
            FOREIGN KEY (id_tipo_correo) REFERENCES tipos_correos_electronicos(id_tipo_correo),
            FOREIGN KEY (id_estatus_correo) REFERENCES estatus_correos_electronicos(id_estatus_correo),
            FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'correos_electrónicos' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_celulares (
        numero_renovacion VARCHAR(20) NULL,
        imei VARCHAR(20) PRIMARY KEY UNIQUE NOT NULL,
        numero_serie VARCHAR(100),
        mac_address VARCHAR(100),
        comentarios TEXT NULL,
        observaciones TEXT NULL,
        numero VARCHAR(20) NULL,
        id_modelo INT NOT NULL,
        id_condicion INT NULL,
        id_cargador INT NULL,
        id_caja INT NULL,
        fecha_entrega DATE,
        codigo_empleado VARCHAR(20) NULL,
        id_estatus_celular INT,
        
        FOREIGN KEY (numero) REFERENCES lineas_telefonicas (numero),
        FOREIGN KEY (id_modelo) REFERENCES modelos_celulares (id_modelo),
        FOREIGN KEY (id_condicion) REFERENCES condicion(id_condicion),
        FOREIGN KEY (id_cargador) REFERENCES cargadores(id_cargador),
        FOREIGN KEY (id_caja) REFERENCES caja(id_caja),
        FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo),
        FOREIGN KEY (id_estatus_celular) REFERENCES estatus_celulares(id_estatus_celular)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'inventario_celulares' creada exitosamente en agrocisa_core.db!") 

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_cpu (
        id_cpu INT AUTO_INCREMENT PRIMARY KEY,
        hostname VARCHAR(100),
        marca VARCHAR(100),
        modelo VARCHAR(100),
        numero_serie VARCHAR(100),
        procesador VARCHAR(100),
        datos_memoria_ram VARCHAR(100),
        memoria_ram VARCHAR(100),
        id_hdd_tipo INT,
        datos_almacenamiento VARCHAR(100),
        almacenamiento VARCHAR(100),
        motherboard VARCHAR(100),
        sistema_operativo VARCHAR(100),
        mac_address_lan VARCHAR(100),
        mac_address_wlan VARCHAR(100),
        precio INT,
        comentarios TEXT,
        observaciones TEXT,
        fecha_mantenimiento DATE,
        id_condicion INT,
        id_renovacion INT,
        fecha_entrega DATE,
        codigo_empleado VARCHAR(20),
        id_estatus_cpu INT,
        
        FOREIGN KEY (id_hdd_tipo) REFERENCES hdd_tipo (id_hdd_tipo),
        FOREIGN KEY (id_condicion) REFERENCES condicion (id_condicion),
        FOREIGN KEY (id_renovacion) REFERENCES renovacion(id_renovacion),
        FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo),
        FOREIGN KEY (id_estatus_cpu) REFERENCES estatus_cpu(id_estatus_cpu)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
            
    print("¡Tabla 'inventario_cpu' creada exitosamente en agrocisa_core.db!")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_laptops (
        hostname VARCHAR(100),
        marca VARCHAR(100),
        modelo VARCHAR(100),
        numero_serie VARCHAR(100) PRIMARY KEY NOT NULL,
        procesador VARCHAR(100),
        datos_memoria_ram VARCHAR(100),
        memoria_ram VARCHAR(100),
        datos_almacenamiento VARCHAR(100),
        almacenamiento VARCHAR(100),
        motherboard VARCHAR(100),
        sistema_operativo VARCHAR(100),
        mac_address_lan VARCHAR(100),
        mac_address_wlan VARCHAR(100),
        precio INT,
        comentarios TEXT,
        observaciones TEXT,
        id_hdd_tipo INT,
        id_cargador INT,
        id_condicion INT,
        id_renovacion INT,
        fecha_entrega DATE,
        codigo_empleado VARCHAR(20),
        id_estatus_laptops INT,
        
        FOREIGN KEY (id_hdd_tipo) REFERENCES hdd_tipo (id_hdd_tipo),
        FOREIGN KEY (id_cargador) REFERENCES cargadores (id_cargador),
        FOREIGN KEY (id_condicion) REFERENCES condicion (id_condicion),
        FOREIGN KEY (id_renovacion) REFERENCES renovacion(id_renovacion),
        FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo),
        FOREIGN KEY (id_estatus_laptops) REFERENCES estatus_laptops(id_estatus_laptops)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
            
    print("¡Tabla 'inventario_laptops' creada exitosamente en agrocisa_core.db!")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_monitores (
        hostname VARCHAR(100),
        marca VARCHAR(100),
        modelo VARCHAR(100),
        numero_serie VARCHAR(100) PRIMARY KEY NOT NULL,
        resolucion VARCHAR(100),
        precio INT,
        comentarios TEXT,
        observaciones TEXT,
        id_condicion INT,
        id_renovacion INT,
        fecha_entrega DATE,
        codigo_empleado VARCHAR(20),
        id_estatus_monitor INT,
        
        FOREIGN KEY (id_condicion) REFERENCES condicion (id_condicion),
        FOREIGN KEY (id_renovacion) REFERENCES renovacion(id_renovacion),
        FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo),
        FOREIGN KEY (id_estatus_monitor) REFERENCES estatus_monitores(id_estatus_monitor)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
            
    print("¡Tabla 'inventario_monitores' creada exitosamente en agrocisa_core.db!")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario_tablets (
        marca VARCHAR(100),
        modelo VARCHAR(100),
        imei VARCHAR(20),
        numero_serie VARCHAR(100) PRIMARY KEY NOT NULL,
        mac_address VARCHAR(100),
        precio INT,
        comentarios TEXT,
        observaciones TEXT,
        id_condicion INT,
        id_cargador INT,
        fecha_entrega DATE,
        codigo_empleado VARCHAR(20),
        id_estatus_tablet INT,
        
        FOREIGN KEY (id_condicion) REFERENCES condicion (id_condicion),
        FOREIGN KEY (id_cargador) REFERENCES cargadores(id_cargador),
        FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo),
        FOREIGN KEY (id_estatus_tablet) REFERENCES estatus_tablets(id_estatus_tablet)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    print("¡Tabla 'inventario_tablets' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsivas_celulares (
        id_responsiva_celular INT PRIMARY KEY AUTO_INCREMENT,
        fecha_entrega DATE NOT NULL,
        codigo_empleado VARCHAR(20),
        numero VARCHAR(20),
        imei VARCHAR(20),
        
        FOREIGN KEY (codigo_empleado) REFERENCES empleados(codigo),
        FOREIGN KEY (numero) REFERENCES lineas_telefonicas(numero),
        FOREIGN KEY (imei) REFERENCES inventario_celulares(imei)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
        
    print("¡Tabla 'responsivas_celulares' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsivas_cpu (
        id_responsiva_cpu INT PRIMARY KEY AUTO_INCREMENT,
        id_cpu INT,
        fecha_entrega DATE NOT NULL,
        codigo_empleado VARCHAR(20),
        
        FOREIGN KEY (codigo_empleado) REFERENCES empleados (codigo),
        FOREIGN KEY (id_cpu) REFERENCES inventario_cpu(id_cpu)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
        
    print("¡Tabla 'responsivas_cpu' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsivas_laptops (
        id_responsiva_cpu INT PRIMARY KEY AUTO_INCREMENT,
        fecha_entrega DATE NOT NULL,
        codigo_empleado VARCHAR(20),
        numero_serie VARCHAR(100),
        
        FOREIGN KEY (codigo_empleado) REFERENCES empleados (codigo),
        FOREIGN KEY (numero_serie) REFERENCES inventario_laptops(numero_serie)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
        
    print("¡Tabla 'responsivas_laptops' creada exitosamente en agrocisa_core.db!")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsivas_monitores (
        id_responsiva_cpu INT PRIMARY KEY AUTO_INCREMENT,
        fecha_entrega DATE NOT NULL,
        codigo_empleado VARCHAR(20),
        numero_serie VARCHAR(100),
        
        FOREIGN KEY (codigo_empleado) REFERENCES empleados (codigo),
        FOREIGN KEY (numero_serie) REFERENCES inventario_monitores(numero_serie)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
        
    print("¡Tabla 'responsivas_monitores' creada exitosamente en agrocisa_core.db!")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS responsivas_tablets (
        id_responsiva_cpu INT PRIMARY KEY AUTO_INCREMENT,
        fecha_entrega DATE NOT NULL,
        codigo_empleado VARCHAR(20),
        numero_serie VARCHAR(100),
        
        FOREIGN KEY (codigo_empleado) REFERENCES empleados (codigo),
        FOREIGN KEY (numero_serie) REFERENCES inventario_tablets(numero_serie)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
        
    print("¡Tabla 'responsivas_tablets' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dispositivos_red (
        id_dispositivo INT PRIMARY KEY AUTO_INCREMENT,
        id_sucursal INT NOT NULL,
        tipo VARCHAR(100),
        marca VARCHAR(100),
        modelo VARCHAR(100),
        numero_serie VARCHAR(100),
        mac_address_lan VARCHAR(100),
        mac_address_wlan VARCHAR(100),
        ubicacion_fisica VARCHAR(100)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
            
    print("¡Tabla 'dispositivos_red' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dispositivos_accesos (
        id_dispositivo INT,
        hostname VARCHAR(100),
        usuario_admin_default VARCHAR(100),
        password_admin_default VARCHAR(100),
        nuevo_usuario VARCHAR(100),
        password_nuevo VARCHAR(100),
        puerto_admin VARCHAR(100),
        
        FOREIGN KEY (id_dispositivo) REFERENCES dispositivos_red (id_dispositivo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
            
    print("¡Tabla 'dispositivos_accesos' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dispositivos_wifi (
        id_dispositivo INT,
        ssid VARCHAR(100),
        modo_wpa VARCHAR(100),
        password_wpa VARCHAR(100),
        
        FOREIGN KEY (id_dispositivo) REFERENCES dispositivos_red (id_dispositivo)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
            
    print("¡Tabla 'dispositivos_wifi' creada exitosamente en agrocisa_core.db!")
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    conexion.commit()
    conexion.close()

# EL CANDADO SUPREMO:
# __name__ es una variable interna de Python. Si ejecutas el archivo directo en la consola, 
# Python le asigna el valor "__main__". Si lo asigna, corre la función main(). 
# Si alguien intenta importarlo desde otro script, __name__ valdrá otra cosa y la función NO se ejecutará.
if __name__ == "__main__":
    main()