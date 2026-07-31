import pymysql
import pandas as pd

DB_CONFIG = {
    'host': 'localhost',      # Tu servidor MariaDB
    'user': 'agrocisa_admin',
    'password': '4GR0C154#SIS',
    'database': 'agrocisa_core',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

def obtener_metricas_generales():
    conn = get_db_connection()
    with conn.cursor() as cursor:
        # 1. Total Empleados Activos
        cursor.execute("SELECT COUNT(*) AS total FROM empleados WHERE id_estatus_empleado = 1;")
        empleados_activos = cursor.fetchone()['total']
        
        # 2. Total Equipos Asignados (Suma de los 5 inventarios donde hay codigo_empleado)
        query_asignados = """
        SELECT 
            (SELECT COUNT(*) FROM inventario_celulares_2026 WHERE codigo_empleado IS NOT NULL) +
            (SELECT COUNT(*) FROM inventario_cpu WHERE codigo_empleado IS NOT NULL) +
            (SELECT COUNT(*) FROM inventario_laptops WHERE codigo_empleado IS NOT NULL) +
            (SELECT COUNT(*) FROM inventario_monitores WHERE codigo_empleado IS NOT NULL) +
            (SELECT COUNT(*) FROM inventario_tablets WHERE codigo_empleado IS NOT NULL) AS total_asignados;
        """
        cursor.execute(query_asignados)
        equipos_asignados = cursor.fetchone()['total_asignados']
        
    conn.close()
    return empleados_activos, equipos_asignados

def obtener_resumen_inventario():
    conn = get_db_connection()
    
    # Query que unifica los 5 inventarios respetando tus nombres de tablas
    query = """
    SELECT 'Celulares' AS Tipo, COUNT(*) AS Total, 
           SUM(CASE WHEN codigo_empleado IS NOT NULL THEN 1 ELSE 0 END) AS Asignados,
           SUM(CASE WHEN codigo_empleado IS NULL THEN 1 ELSE 0 END) AS Disponibles
    FROM inventario_celulares_2026
    
    UNION ALL
    
    SELECT 'CPUs' AS Tipo, COUNT(*) AS Total, 
           SUM(CASE WHEN codigo_empleado IS NOT NULL THEN 1 ELSE 0 END) AS Asignados,
           SUM(CASE WHEN codigo_empleado IS NULL THEN 1 ELSE 0 END) AS Disponibles
    FROM inventario_cpu
    
    UNION ALL
    
    SELECT 'Laptops' AS Tipo, COUNT(*) AS Total, 
           SUM(CASE WHEN codigo_empleado IS NOT NULL THEN 1 ELSE 0 END) AS Asignados,
           SUM(CASE WHEN codigo_empleado IS NULL THEN 1 ELSE 0 END) AS Disponibles
    FROM inventario_laptops
    
    UNION ALL
    
    SELECT 'Monitores' AS Tipo, COUNT(*) AS Total, 
           SUM(CASE WHEN codigo_empleado IS NOT NULL THEN 1 ELSE 0 END) AS Asignados,
           SUM(CASE WHEN codigo_empleado IS NULL THEN 1 ELSE 0 END) AS Disponibles
    FROM inventario_monitores
    
    UNION ALL
    
    SELECT 'Tablets' AS Tipo, COUNT(*) AS Total, 
           SUM(CASE WHEN codigo_empleado IS NOT NULL THEN 1 ELSE 0 END) AS Asignados,
           SUM(CASE WHEN codigo_empleado IS NULL THEN 1 ELSE 0 END) AS Disponibles
    FROM inventario_tablets;
    """
    
    df_resumen = pd.read_sql_query(query, conn)
    conn.close()
    return df_resumen