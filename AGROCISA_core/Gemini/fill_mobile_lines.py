import sqlite3
import openpyxl
from pathlib import Path

def clean_money_value(value):
    if value is None or str(value).strip() in ('N/A', ''):
        return None
    clean_val = str(value).replace('$', '').replace(',', '').strip()
    return float(clean_val)

def clean_gb_value(value):
    if value is None or str(value).strip() in ('N/A', ''):
        return None
    clean_val = str(value).replace(',', '.').strip()
    return float(clean_val)

def fill_mobile_lines(cursor, excel_path):
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    sheet = wb['Historico_Lineas_2026']
    
    COL_NUMERO = 0
    COL_MPP = 1
    COL_PLAN_2024 = 2
    COL_MENSUALIDAD_2024 = 3
    COL_GB_2024 = 4
    COL_PLAN_2026 = 5
    COL_MENSUALIDAD_2026 = 6
    COL_GB_BASE_2026 = 7
    COL_GB_PROMOCION_2026 = 8
    COL_DIFERENCIA_2024_2026 = 9
    
    lines_to_insert = []
    
    # max_col=10 para asegurar que leemos desde Teléfono hasta Diferencia completo
    for row in sheet.iter_rows(min_row=2, max_col=10, values_only=True):
        
        if row[COL_NUMERO] is None:
            continue
            
        # Mapeo estricto de las 10 columnas de tu Excel de la verdad
        numero = int(float(str(row[COL_NUMERO]).strip()))
        is_mpp = 1 if row[COL_MPP] else 0
        
        plan_2024 = str(row[COL_PLAN_2024]).strip() if row[COL_PLAN_2024] else None
        mensualidad_2024 = clean_money_value(row[COL_MENSUALIDAD_2024])
        gb_2024 = clean_gb_value(row[COL_GB_2024])
        
        plan_2026 = str(row[COL_PLAN_2026]).strip() if row[COL_PLAN_2026] else None
        mensualidad_2026 = clean_money_value(row[COL_MENSUALIDAD_2026])
        
        # --- AQUÍ ESTÁ LO QUE TE HABÍA MOCHADO ---
        gb_base_2026 = clean_gb_value(row[COL_GB_BASE_2026])       # Columna 7: GB normales del plan
        gb_promocion_2026 = clean_gb_value(row[COL_GB_PROMOCION_2026])  # Columna 8: GB con la promoción ganada
        
        cost_difference = clean_money_value(row[COL_DIFERENCIA_2024_2026])  # Columna 9: Diferencia de los $100
        
        codigo_usuario = None
        
        # Empaquetamos la tupla con las 11 variables para la base de datos
        lines_to_insert.append((
            numero, codigo_usuario, is_mpp,
            plan_2024, mensualidad_2024, gb_2024,
            plan_2026, mensualidad_2026, gb_base_2026, gb_promocion_2026,
            cost_difference
        ))
        
    # Inserción limpia con todos los testigos guardados
    cursor.executemany("""
    INSERT OR IGNORE INTO lineas_telefonicas (
        numero, codigo_empleado, is_mpp,
        plan_2024, mensualidad_2024, gb_2024,
        plan_2026, mensualidad_2026, gb_base_2026, gb_promocion_2026,
        cost_difference
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, lines_to_insert)
    
    print(f"¡Listo, carnal! Inyectadas {len(lines_to_insert)} líneas con el histórico y los gigas completos.")


if __name__ == "__main__":
    connecction = sqlite3.connect("agrocisa_core.db")
    cursor = connecction.cursor()
    excel_wb = Path.home() / "git" / "proyects" / "AGROCISA_core" / "Directorio.xlsx"
    
    fill_mobile_lines(cursor)
    connecction.commit()
    connecction.close()