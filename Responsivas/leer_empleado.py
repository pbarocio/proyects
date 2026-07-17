import openpyxl
from datetime import datetime
from num2words import num2words

# 1. Abrir el Excel
archivo_excel = "Directorio.xlsx"
libro = openpyxl.load_workbook(archivo_excel, data_only=True)

# 2. Seleccionar la hoja
hoja = libro["Inventario Celulares"]

# 3. Leer encabezados (fila 1) para saber qué columna es qué
encabezados = []
for celda in hoja[1]:
    encabezados.append(celda.value)

# print("📋 ENCABEZADOS:")
# for i, encabezado in enumerate(encabezados):
#     print(f"{i}: {encabezado}")

ultima_fila = hoja.max_row

def normalize_date(date_raw):
    if date_raw is None and not date_raw:
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

#5 NORMALIZAR EL NÚMERO DE COLUMNA CON NOMBRE
COL_NUMERO = 1
COL_PLAN = 2
COL_MEGAS = 4
COL_EQUIPO = 5
COL_IMEI = 6
COL_SERIE = 7
COL_CONDICION = 9
COL_CARGADOR = 10
COL_CAJA = 11
COL_FECHA = 12
COL_COMENTARIOS = 13
COL_PRECIO = 15
COL_NOMBRE = 16
COL_SUCURSAL = 17
COL_DEPARTAMENTO = 18
COL_PUESTO = 19
COL_GMAIL = 20
COL_AGROCISA = 21


for fila in range(2, ultima_fila + 1):
    # 4. Leer la fila 2 (primer empleado)
    fila_empleado = hoja[fila]
    #6 Luego, al leer la fila:
    fecha = normalize_date(fila_empleado[COL_FECHA].value)
    nombre = normalize_values(fila_empleado[COL_NOMBRE].value)
    sucursal = normalize_values(fila_empleado[COL_SUCURSAL].value)
    departamento = normalize_values(fila_empleado[COL_DEPARTAMENTO].value)
    puesto = normalize_values(fila_empleado[COL_PUESTO].value)
    equipo = normalize_values(fila_empleado[COL_EQUIPO].value)
    numero = normalize_values(fila_empleado[COL_NUMERO].value)
    imei = normalize_values(fila_empleado[COL_IMEI].value)
    numero_serie = normalize_values(fila_empleado[COL_SERIE].value)
    cuenta_gmail = normalize_values(fila_empleado[COL_GMAIL].value)
    cuenta_agrocisa = normalize_values(fila_empleado[COL_AGROCISA].value)
    megas = normalize_mb(fila_empleado[COL_MEGAS].value)
    condicion = normalize_values(fila_empleado[COL_CONDICION].value)
    cargador = normalize_values(fila_empleado[COL_CARGADOR].value)
    caja = normalize_values(fila_empleado[COL_CAJA].value)
    coments = normalize_values(fila_empleado[COL_COMENTARIOS].value)
    precio, precio_letra = normalize_price(fila_empleado[COL_PRECIO].value)

    
    if not imei is None and not imei == "Sin dato":
        contexto = {}
        contexto = {
            'fecha' : fecha,
            'nombre_empleado': nombre,
            'sucursal': sucursal,
            'departamento' : departamento,
            'puesto': puesto,
            'equipo': equipo,
            'numero' : numero,
            'imei': imei,
            'serie': numero_serie,
            'cuenta_gmail' : cuenta_gmail,
            'cuenta_agrocisa' : cuenta_agrocisa,
            'megas' : megas,
            "condicion" : condicion,
            "cargador" : cargador,
            "caja" : caja,
            "comentarios" : coments,
            'precio': precio,
            'precio_letras': precio_letra
        }
        
        # 6. Mostrar datos
        print("=" * 175)
        print(f"👤 Empleado: {nombre} | 📍 Sucursal: {sucursal} | 💼 Departamento: {departamento} | 🪪 Puesto: {puesto}")
        print(f"📧 Correo de Google: {cuenta_gmail} | 📧 Correo Corporativo: {cuenta_agrocisa}")
        print(f"📱 Equipo: {equipo} | 🗒️ IMEI: {imei} | 📋 Serie: {numero_serie} |  🔖 Condición {condicion} | 🔌 Cargador: {cargador} | 📦 Caja: {caja}")
        print(f" 📞 Cel: {numero} | 📡 Datos incluidos en el plan: {megas} GB | 🗣️ Comentarios: {coments}")
        print(f"🗓️ Fecha: {fecha} | 💵 Precio ${precio} ({precio_letra})")

print("=" * 175)