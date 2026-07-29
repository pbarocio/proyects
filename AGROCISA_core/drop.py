# drop_db.py
from db_config import get_connection_nueva
from db_config import environment_info
import pymysql

def drop_database():
    conexion = get_connection_nueva()
    if conexion is None:
        print("❌ No se pudo conectar a MariaDB")
        return
    
    cursor = conexion.cursor()
    
    try:
        # OJO: Aquí va el nombre de TU base de datos (el que tienes en .env)
        cursor.execute("DROP DATABASE IF EXISTS agrocisa_core")
        print("🗑️ Base de datos 'agrocisa_core' eliminada (si existía)")
        conexion.commit()
        
    except pymysql.Error as e:
        print(f"❌ Error al eliminar la BDD: {e}")
        conexion.rollback()
    finally:
        cursor.close()
        conexion.close()

if __name__ == "__main__":
    print("⚠️  VAS A ELIMINAR LA BASE DE DATOS COMPLETA")
    confirm = input("¿Estás seguro? (escribe 'SI' para continuar): ")
    if confirm == "SI":
        drop_database()
        print("✅ Listo. Ejecuta 'python pipeline.py' para recrear todo.")
    else:
        print("Operación cancelada.")