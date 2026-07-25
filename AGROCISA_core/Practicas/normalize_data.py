from datetime import datetime
from num2words import num2words

def normalize_date(date_raw):
    if date_raw is None or not date_raw:
        return "Sin asignar"
    
    if isinstance(date_raw, datetime):
        week_days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        year_monts = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        day = week_days[date_raw.weekday()]
        day_number = date_raw.day
        date_mont = year_monts[date_raw.month]
        date_year = date_raw.year
        
        return f"{day} {day_number} de {date_mont} de {date_year}"

def normalize_values(values_raw):
    if values_raw is None:
        return "Sin dato"
    
    if isinstance(values_raw, float) or isinstance (values_raw, int):
        return int(values_raw)
    
    return str(values_raw).strip()

def normalize_mb(mb_raw):
    if mb_raw is None or not mb_raw:
        return "No hay número asignado"
    
    return mb_raw

def normalize_price(price_raw):
    if price_raw is None or isinstance(price_raw, str):
        return "0.00", "Sin Asignar"
    
    if isinstance(price_raw, float) or isinstance(price_raw, int):
        return f"{int(price_raw):,}", f"{num2words(price_raw, lang = 'es').upper()} PESOS 00/100 M.N."