# pipeline.py
import subprocess
import sys
import time

def run_script(script_name):
    print(f"\n🚀 Ejecutando {script_name}...")
    # Ejecuta el script con el mismo Python que está corriendo esto
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {script_name} completado con éxito")
        # Opcional: imprime la salida para ver si todo bien
        # print(result.stdout) 
        return True
    else:
        print(f"❌ ERROR en {script_name}")
        print(f"Error: {result.stderr}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🏁 INICIANDO PIPELINE DE AGROCISA")
    print("=" * 50)
    
    # Lista de tus scripts en el ORDEN exacto
    scripts = [
        "0_crear_bdd.py",      # Crea la BDD si no existe
        "1_crear_core.py",     # Crea las tablas
        "2_llenar_catalogos.py", 
        # "3_importar_empleados.py",
        # # ... y así hasta el 15
        # "15_generar_responsivas.py"
    ]
    
    start_time = time.time()
    
    for script in scripts:
        if not run_script(script):
            print("🚨 Pipeline detenido por error.")
            sys.exit(1)
    
    end_time = time.time()
    print("\n" + "=" * 50)
    print(f"🎉 PIPELINE COMPLETADO en {round(end_time - start_time, 2)} segundos")
    print("=" * 50)