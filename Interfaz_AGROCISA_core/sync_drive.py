import os
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from database import obtener_conexion

SPREADSHEET_ID = "1FCJPGoTNAPjmBoZFt7VfdkLgsP7Q1431PJ_wgXvKbS4"
CREDS_PATH = Path(__file__).parent / "credentials.json"

def obtener_lista_distribucion_df():
    conn = obtener_conexion()
    query = """
        SELECT 
            CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS Nombre,
            s.nombre_sucursal AS Sucursal,
            d.nombre_departamento AS Departamento,
            p.nombre_puesto AS Puesto,
            ce.correo_gmail AS `Correo Gmail`,
            ce.correo_corporativo AS `Correo Institucional`,
            ic.numero AS Celular
        FROM empleados e
        LEFT JOIN sucursales s ON e.id_sucursal = s.id_sucursal
        LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento
        LEFT JOIN puestos p ON e.id_puesto = p.id_puesto
        LEFT JOIN (
            SELECT 
                TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) AS cod_clean,
                MAX(CASE WHEN id_tipo_correo = 2 THEN direccion_correo END) AS correo_gmail,
                MAX(CASE WHEN id_tipo_correo = 1 THEN direccion_correo END) AS correo_corporativo
            FROM correos_electronicos
            WHERE id_estatus_correo = 1
            GROUP BY cod_clean
        ) ce ON TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR)) = ce.cod_clean
        LEFT JOIN (
            SELECT 
                TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) AS cod_clean, 
                MAX(numero) AS numero
            FROM inventario_celulares
            WHERE codigo_empleado IS NOT NULL 
              AND numero IS NOT NULL 
              AND TRIM(numero) != ''
            GROUP BY cod_clean
        ) ic ON TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR)) = ic.cod_clean
        WHERE e.id_estatus_empleado = 1
        ORDER BY Nombre ASC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def auto_sincronizar_google_sheet():
    try:
        if not CREDS_PATH.exists():
            return False, f"No existe credentials.json en {CREDS_PATH}"

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(str(CREDS_PATH), scopes=scopes)
        client = gspread.authorize(creds)

        df = obtener_lista_distribucion_df()
        df = df.fillna("")

        sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Colaboradores")
        sheet.clear()

        valores = [df.columns.values.tolist()] + df.astype(str).values.tolist()
        sheet.update("A1", valores)
        return True, "OK"
    except Exception as e:
        err_msg = str(e)
        print(f"⚠️ Error al sincronizar con Google Sheets: {err_msg}")
        return False, err_msg