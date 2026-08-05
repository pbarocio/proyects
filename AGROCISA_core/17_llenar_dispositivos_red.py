import pandas as pd
import numpy as np
from db_config import get_files_path, get_engine, get_connection

# Mostrar todas las filas
pd.set_option('display.max_rows', None)

# Mostrar todas las columnas
pd.set_option('display.max_columns', None)

# Mostrar texto completo (sin truncar)
pd.set_option('display.max_colwidth', None)
        
path = get_files_path()
red_agrocisa = path["red_agrocisa"]
directorio_nuevo = path['directorio_nuevo']

df_dispositivos_red_completo = pd.read_excel(
    red_agrocisa,
    sheet_name="Corporativo",
).copy()

df_dispositivos_red_completo.rename(columns={
  'Sucursal' : 'sucursal',
  'Tipo' : 'tipo',
  'Marca' : 'marca',
  'Modelo' : 'modelo',
  'No. de Serie' : 'numero_serie',
  'MAC-Address LAN' :'mac_address_lan',
  'MAC-Address WLAN' : 'mac_address_wlan',
  'Puerto' : 'puerto_admin',
  'Hostname' : 'hostname',
  'Usuario' : 'usuario_admin_default',
  'Nuevo Usuario' : 'nuevo_usuario',
  'Password' : 'password_admin_default',
  'Nuevo Password' : 'password_nuevo',
  'SSID' : 'ssid',
  'WPA2-PSK' : 'password_wpa',
  'Ubicación' : 'ubicacion_fisica',
}, inplace=True)

df_dispositivos_red_completo["modo_wpa"] = "WPA2-PSK"

engine = get_engine()

df_sucursales = pd.read_sql_query("SELECT id_sucursal, nombre_sucursal FROM sucursales", con=engine)

df_dispositivos_red_completo = df_dispositivos_red_completo.merge(
  df_sucursales,
  left_on='sucursal',
  right_on='nombre_sucursal',
  how='left',
)

df_dispositivos_red_completo = df_dispositivos_red_completo.replace({np.nan: None})

print(f"\"{len(df_dispositivos_red_completo)}\" dispositivos de red listos para inyectar")

with pd.ExcelWriter(directorio_nuevo, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df_dispositivos_red_completo.to_excel(writer, sheet_name='Dispostivos de Red', index=False)

connecction = get_connection()
cursor = connecction.cursor()

for index, row in df_dispositivos_red_completo.iterrows():
    # 1. Insertamos en la tabla principal
    sql_red = """
        INSERT INTO dispositivos_red (
            id_sucursal, tipo, marca, modelo, numero_serie, 
            mac_address_lan, mac_address_wlan, ubicacion_fisica
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    val_red = (
        row['id_sucursal'], row['tipo'], row['marca'], row['modelo'], 
        row['numero_serie'], row['mac_address_lan'], row['mac_address_wlan'], row['ubicacion_fisica']
    )
    cursor.execute(sql_red, val_red)
    
    # ¡AQUÍ ESTÁ LA MAGIA! Recuperas el ID recién creado
    id_creado = cursor.lastrowid
    
    # 2. Tabla dispositivos_accesos
    if any([row['hostname'], row['usuario_admin_default'], row['password_admin_default'], row['password_nuevo']]):
        sql_accesos = """
        INSERT INTO dispositivos_accesos (
            id_dispositivo, hostname, usuario_admin_default, 
            password_admin_default, nuevo_usuario, password_nuevo, puerto_admin
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        val_accesos = (
        id_creado, row['hostname'], row['usuario_admin_default'], 
        row['password_admin_default'], row['nuevo_usuario'], row['password_nuevo'], row['puerto_admin']
        )
        cursor.execute(sql_accesos, val_accesos)
        
    # 3. Si la fila tiene datos de Wi-Fi, insertamos en dispositivos_wifi
    if pd.notna(row['ssid']) or pd.notna(row['password_wpa']):
        sql_wifi = """
            INSERT INTO dispositivos_wifi (
                id_dispositivo, ssid, modo_wpa, password_wpa
            ) VALUES (%s, %s, %s, %s)
        """
        val_wifi = (id_creado, row['ssid'], row['modo_wpa'], row['password_wpa'])
        cursor.execute(sql_wifi, val_wifi)

# Al final del ciclo tiras el commit
connecction.commit()
connecction.close()

print(f"\"{len(df_dispositivos_red_completo)}\" dispositivos de red inyectados correctamente... ")