# consultas.py
from database import obtener_conexion

def obtener_sucursales():
    conn = obtener_conexion()  # """Trae las sucursales de MariaDB y las regresa como diccionario: {"Corporativo": 1, ...}"""
    sucursales_map = {}
    if conn:
        cursor = conn.cursor()
        query = "SELECT id_sucursal, nombre_sucursal FROM sucursales" # Traemos la llave primaria y el nombre
        cursor.execute(query)
        registros = cursor.fetchall()

        for id_suc, nombre in registros: # Armamos el diccionario: {"Nombre de Sucursal": ID}
            sucursales_map[nombre] = id_suc

        cursor.close()
        conn.close()

    return sucursales_map

def obtener_departamentos():
    conn = obtener_conexion()  # """Trae las sucursales de MariaDB y las regresa como diccionario: {"Corporativo": 1, ...}"""
    departamentos_map = {}
    if conn:
        cursor = conn.cursor()
        query = "SELECT id_departamento, nombre_departamento FROM departamentos" # Traemos la llave primaria y el nombre
        cursor.execute(query)
        registros = cursor.fetchall()

        for id_dep, nombre in registros: # Armamos el diccionario: {"Nombre de Sucursal": ID}
            departamentos_map[nombre] = id_dep

        cursor.close()
        conn.close()

    return departamentos_map

def obtener_puestos():
    conn = obtener_conexion()
    puestos_map = {}
    if conn:
        cursor = conn.cursor()
        query = "SELECT id_puesto, nombre_puesto FROM puestos"
        cursor.execute(query)
        registros = cursor.fetchall()
        
        for id_pue, nombre in registros:
            puestos_map[nombre] = id_pue
        
        cursor.close()
        conn.close()
    
    return puestos_map

def obtener_zonas():
    conn = obtener_conexion()
    
def existe_empleado(codigo):
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        query = "SELECT codigo FROM empleados WHERE codigo = %s"
        cursor.execute(query, (codigo,))
        resultado = cursor.fetchone()
        cursor.close()
        conn.close()
        return resultado is not None
    return False

def guardar_empleado(codigo, apellido_paterno, apellido_materno, nombre, sucursal, departamento, puesto):
    """Recibe los datos del formulario y los mete a MariaDB"""
    numero_telefono = None
    id_estatus_empleado = 1
    conn = obtener_conexion()
    if conn:
        cursor = conn.cursor()
        query = """
            INSERT IGNORE INTO empleados (codigo, apellido_paterno, apellido_materno, nombre, id_sucursal, id_departamento, id_puesto, numero_telefono, id_estatus_empleado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        valores = (codigo, apellido_paterno, apellido_materno, nombre, sucursal, departamento, puesto, numero_telefono, id_estatus_empleado)
        
        cursor.execute(query, valores)
        conn.commit()
        cursor.close()
        conn.close()
        return True
    return False