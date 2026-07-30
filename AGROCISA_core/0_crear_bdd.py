# 0_crear_bdd.py
from db_config import get_connection_nueva
from db_config import get_files_path
import pymysql

def crear_base_datos():
    # Conecta SIN database (porque NO EXISTE)
    conexion = get_connection_nueva()
    if conexion is None:
        print("❌ No se pudo conectar a MariaDB")
        return
    
    cursor = conexion.cursor()
    environment = get_files_path()
    
    try:
        # Crear la base de datos
        cursor.execute("""
            CREATE DATABASE IF NOT EXISTS agrocisa_core 
            CHARACTER SET utf8mb4 
            COLLATE utf8mb4_unicode_ci
        """)
        print("✅ Base de datos 'agrocisa_core' creada/verificada")
        
        # Dar permisos al usuario sobre la BDD
        cursor.execute(f"GRANT ALL PRIVILEGES ON agrocisa_core.* TO '{environment['db_user']}'@'localhost'")
        cursor.execute("FLUSH PRIVILEGES")
        
        conexion.commit()
        print("✅ Permisos asignados")
        
    except pymysql.Error as e:
        print(f"❌ Error al crear la BDD: {e}")
        conexion.rollback()
    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    crear_base_datos()