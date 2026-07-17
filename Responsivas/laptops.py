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
hoja = libro["Inventario Laptop"]

# 3. Leer encabezados (fila 1) para saber qué columna es qué
encabezados = []
for celda in hoja[1]:
    encabezados.append(celda.value)

# print("📋 ENCABEZADOS:")
# for i, encabezado in enumerate(encabezados):
#     print(f"{i}: {encabezado}")

ultima_fila = hoja.max_row

# #5 NORMALIZAR EL NÚMERO DE COLUMNA CON NOMBRE
COL_HOST = 0
COL_PRECIO = 1
COL_CONDICION = 2
COL_CARGADOR = 3
COL_OBSERVACIONES = 4
COL_FECHA = 5
COL_MARCA = 6
COL_MODELO = 7
COL_SERIE = 8
COL_USUARIO = 18
COL_SUCURSAL = 19
COL_DEPARTAMENTO = 20
COL_PUESTO = 21
COL_GMAIL = 22
COL_CORPORATIVO = 23

for fila in range(2, ultima_fila + 1):
    # 4. Leer la fila 2 (primer empleado)
    fila_empleado = hoja[fila]
    #6 Luego, al leer la fila:
    fecha = nd.normalize_date(fila_empleado[COL_FECHA].value)
    usuario = nd.normalize_values(fila_empleado[COL_USUARIO].value)
    sucursal = nd.normalize_values(fila_empleado[COL_SUCURSAL].value)
    departamento = nd.normalize_values(fila_empleado[COL_DEPARTAMENTO].value)
    puesto = nd.normalize_values(fila_empleado[COL_PUESTO].value)
    marca = nd.normalize_values(fila_empleado[COL_MARCA].value)
    modelo = nd.normalize_values(fila_empleado[COL_MODELO].value)
    numero_serie = nd.normalize_values(fila_empleado[COL_SERIE].value)
    cuenta_gmail = nd.normalize_values(fila_empleado[COL_GMAIL].value)
    cuenta_agrocisa = nd.normalize_values(fila_empleado[COL_CORPORATIVO].value)
    condicion = nd.normalize_values(fila_empleado[COL_CONDICION].value)
    cargador = nd.normalize_values(fila_empleado[COL_CARGADOR].value)
    coments = nd.normalize_values(fila_empleado[COL_OBSERVACIONES].value)
    precio, precio_letra = nd.normalize_price(fila_empleado[COL_PRECIO].value)

    
    if not marca is None and not marca == "Sin dato":
        contexto = {}
        contexto = {
            'fecha' : fecha,
            'nombre_empleado': usuario,
            'sucursal': sucursal,
            'departamento' : departamento,
            'puesto': puesto,
            'marca': marca,
            'modelo' : modelo,
            'serie': numero_serie,
            'cuenta_gmail' : cuenta_gmail,
            'cuenta_agrocisa' : cuenta_agrocisa,
            "condicion" : condicion,
            "cargador" : cargador,
            "observaciones" : coments,
            'precio': precio,
            'precio_letras': precio_letra
        }
        
        # 6. Mostrar datos
        print("=" * 175)
        print(f"👤 Empleado: {usuario} | 📍 Sucursal: {sucursal} | 💼 Departamento: {departamento} | 🪪 Puesto: {puesto}")
        print(f"📧 Correo de Google: {cuenta_gmail} | 📧 Correo Corporativo: {cuenta_agrocisa}")
        print(f"💻 Marca y Modelo {marca} {modelo} | 📋 Serie: {numero_serie} |  🔖 Condición {condicion} | 🔌 Cargador: {cargador}")
        print(f"🗓️ Fecha: {fecha} | 💵 Precio ${precio} ({precio_letra}) | 🗣️ Comentarios: {coments}")

print("=" * 175)