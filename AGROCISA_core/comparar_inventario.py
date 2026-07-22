import sqlite3
import pandas as pd
from pathlib import Path

# --- RUTAS DE ARCHIVO Y BDD ---
archivo_excel = Path("/home/pbarocio/git/proyects/AGROCISA_core/Archivos_Responsivas/Directorio.xlsx")
db_path = "agrocisa_core.db"

# 1. Cargar datos del Excel original (forzando string para no deformar números)
df_excel = pd.read_excel(archivo_excel, sheet_name='Inventario Celulares', dtype=str)

# 2. Cargar lo que realmente quedó insertado en la Base de Datos
conexion = sqlite3.connect(db_path)
df_db = pd.read_sql_query("SELECT * FROM inventario_celulares", conexion)
conexion.close()

# 3. Limpiar IMEIs y Series para hacer un match limpio
df_excel['imei_clean'] = df_excel['IMEI'].astype(str).str.replace(r'\D', '', regex=True)
df_db['imei_clean'] = df_db['imei'].astype(str).str.replace(r'\D', '', regex=True)

# 4. Encontrar registros del Excel que NO están en la Base de Datos
df_faltantes = df_excel[~df_excel['imei_clean'].isin(df_db['imei_clean'])].copy()

# 5. Generar archivo Excel con la comparación
salida_excel = "reporte_diferencias.xlsx"
with pd.ExcelWriter(salida_excel, engine='openpyxl') as writer:
    df_faltantes.to_excel(writer, sheet_name='Faltantes_en_BD', index=False)
    df_db.to_excel(writer, sheet_name='Insertados_en_BD', index=False)

print("="*60)
print(f"Total registros en Excel: {len(df_excel)}")
print(f"Total registros en BD:    {len(df_db)}")
print(f"Total FALTANTES:          {len(df_faltantes)}")
print("="*60)

if not df_faltantes.empty:
    print("\n⚠️ REGISTRO(S) FALTANTE(S) ENCONTRADO(S):")
    print(df_faltantes[['Renovación', 'Número', 'Marca-Modelo', 'IMEI', 'Número de Serie']])
    print(f"\nSe generó el archivo '{salida_excel}' con las dos pestañas para comparar.")
else:
    print("\n¡A huevo! No falta ningún registro, las cantidades cuadran exacto.")