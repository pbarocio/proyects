import openpyxl
import pathlib
import normalize_data as nd
from config import get_config
# 1. Abrir el Excel
config = get_config()
files_dir = config["files_dir"]
archivo_excel = files_dir / "Directorio.xlsx"
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
    fecha = nd.normalize_date(fila_empleado[COL_FECHA].value)
    nombre = nd.normalize_values(fila_empleado[COL_NOMBRE].value)
    sucursal = nd.normalize_values(fila_empleado[COL_SUCURSAL].value)
    departamento = nd.normalize_values(fila_empleado[COL_DEPARTAMENTO].value)
    puesto = nd.normalize_values(fila_empleado[COL_PUESTO].value)
    equipo = nd.normalize_values(fila_empleado[COL_EQUIPO].value)
    numero = nd.normalize_values(fila_empleado[COL_NUMERO].value)
    imei = nd.normalize_values(fila_empleado[COL_IMEI].value)
    numero_serie = nd.normalize_values(fila_empleado[COL_SERIE].value)
    cuenta_gmail = nd.normalize_values(fila_empleado[COL_GMAIL].value)
    cuenta_agrocisa = nd.normalize_values(fila_empleado[COL_AGROCISA].value)
    megas = nd.normalize_mb(fila_empleado[COL_MEGAS].value)
    condicion = nd.normalize_values(fila_empleado[COL_CONDICION].value)
    cargador = nd.normalize_values(fila_empleado[COL_CARGADOR].value)
    caja = nd.normalize_values(fila_empleado[COL_CAJA].value)
    coments = nd.normalize_values(fila_empleado[COL_COMENTARIOS].value)
    precio, precio_letra = nd.normalize_price(fila_empleado[COL_PRECIO].value)

    
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
            'gigas' : megas,
            "condicion" : condicion,
            "cargador" : cargador,
            "caja" : caja,
            "observaciones" : coments,
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