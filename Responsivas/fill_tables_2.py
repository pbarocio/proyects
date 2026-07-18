import openpyxl
import sqlite3
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

def cargar_inventario_maestro(db_path, excel_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    sheet = wb['Historico_Lineas_2026']
    
    lines_to_insert = []
    
    # max_col=10 para asegurar que leemos desde Teléfono hasta Diferencia completo
    for row in sheet.iter_rows(min_row=2, max_col=10, values_only=True):
        
        if row[0] is None:
            continue
            
        # Mapeo estricto de las 10 columnas de tu Excel de la verdad
        phone_number = str(row[0]).split('.')[0].strip()
        is_mpp = str(row[1]).strip() if row[1] else None
        
        plan_2024 = str(row[2]).strip() if row[2] else None
        mensualidad_2024 = clean_money_value(row[3])
        gb_2024 = clean_gb_value(row[4])
        
        plan_2026 = str(row[5]).strip() if row[5] else None
        mensualidad_2026 = clean_money_value(row[6])
        
        # --- AQUÍ ESTÁ LO QUE TE HABÍA MOCHADO ---
        gb_base_2026 = clean_gb_value(row[7])       # Columna 7: GB normales del plan
        gb_promocion_2026 = clean_gb_value(row[8])  # Columna 8: GB con la promoción ganada
        
        cost_difference = clean_money_value(row[9])  # Columna 9: Diferencia de los $100
        
        id_usuario = None
        id_plan_2026 = plan_2026 
        
        # Empaquetamos la tupla con las 11 variables para la base de datos
        lines_to_insert.append((
            phone_number, id_usuario, id_plan_2026, is_mpp,
            plan_2024, mensualidad_2024, gb_2024,
            plan_2026, mensualidad_2026, gb_base_2026, gb_promocion_2026,
            cost_difference
        ))
        
    # Inserción limpia con todos los testigos guardados
    cursor.executemany("""
    INSERT OR IGNORE INTO mobile_lines (
        phone_number, id_usuario, id_plan_2026, is_mpp,
        plan_2024, mensualidad_2024, gb_2024,
        plan_2026, mensualidad_2026, gb_base_2026, gb_promocion_2026,
        cost_difference
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, lines_to_insert)
    
    conn.commit()
    conn.close()
    
    print(f"¡Listo, carnal! Inyectadas {len(lines_to_insert)} líneas con el histórico y los gigas completos.")

if __name__ == "__main__":
    connecction = sqlite3.connect("agrocisa_core.db")
    cursor = connecction.cursor()
    excel_wb = Path.home() / "git" / "pablo-contexto" / "Archivos_Responsivas" / "Directorio.xlsx"
    db_path = "agrocisa_core.db"
    cargar_inventario_maestro(db_path, excel_wb)
    