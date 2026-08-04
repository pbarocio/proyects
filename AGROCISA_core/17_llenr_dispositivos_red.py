import pandas as pd
from db_config import get_files_path

# Mostrar todas las filas
pd.set_option('display.max_rows', None)

# Mostrar todas las columnas
pd.set_option('display.max_columns', None)

# Mostrar texto completo (sin truncar)
pd.set_option('display.max_colwidth', None)

# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS dispositivos_red (
#     id_dispositivo INT PRIMARY KEY AUTO_INCREMENT,
#     id_sucursal INT NOT NULL,
#     tipo VARCHAR(100),
#     marca VARCHAR(100),
#     modelo VARCHAR(100),
#     numero_serie(100),
#     mac_address_lan VARCHAR(100),
#     mac_address_wlan VARCHAR(100),
#     ubicacion_fisica VARCHAR(100)
#     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
# """)
        
# print("¡Tabla 'dispositivos_red' creada exitosamente en agrocisa_core.db!")

# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS dispositivos_accesos (
#     id_dispositivo INT PRIMARY KEY AUTO_INCREMENT,
#     hostname VARCHAR(100),
#     usuario_admin_default VARCHAR(100),
#     password_admin_default VARCHAR(100),
#     password_nuevo VARCHAR(100),
#     puerto_admin VARCHAR(100)
    
#     FOREIGN KEY id_dispositivo REFERENCES dispositivos_red (id_dispositivo)
#     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
# """)
        
# print("¡Tabla 'dispositivos_accesos' creada exitosamente en agrocisa_core.db!")

# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS dispositivos_wifi (
#     id_dispositivo INT,
#     ssid VARCHAR(100),
#     modo_wpa VARCHAR(100),
#     password_wpa VARCHAR(100),
    
#     FOREIGN KEY (id_dispositivo) REFERENCES dispositivos_red (id_dispositivo)
#     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
# """)
        
# print("¡Tabla 'dispositivos_wifi' creada exitosamente en agrocisa_core.db!")
        
path = get_files_path()
red_agrocisa = path["red_agrocisa"]

df_dispositivos_red = pd.read_excel(
    red_agrocisa,
    sheet_name="Corporativo",
).copy()

df_dispositivos_red.rename(columns={
  'Sucursal' : 'sucursal',
  'Tipo' : 'tipo',
  'Marca' : 'marca',
  'Modelo' : 'modelo',
  'No. Serie' : 'numero_serie',
  'MAC-Address LAN' :'mac_address_lan',
  'MAC-Address WAN' : 'mac_address_wlan',
  'Puerto' : 'puerto_admin',
  'Hostname' : 'hostname',
  'Usuario' : 'usuario_admin_default',
  'Password' : 'password_admin_default',
  'Nuevo Password' : 'password_nuevo',
  'SSID' : 'ssid',
  'WPA2-PSK' : 'password_wpa',
  'Ubicación' : 'ubicacion_fisica',
}, inplace=True)