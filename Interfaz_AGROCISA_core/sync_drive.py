import os
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from database import obtener_conexion

SPREADSHEET_ID = "1FCJPGoTNAPjmBoZFt7VfdkLgsP7Q1431PJ_wgXvKbS4"
CREDS_PATH = Path(__file__).parent / "credentials.json"

def obtener_lista_distribucion_df():
    """Genera la lista de distribución leyendo directamente desde MariaDB."""
    conn = obtener_conexion()
    if not conn:
        return pd.DataFrame()

    query = """
        SELECT 
            CONCAT_WS(' ', e.nombre, e.apellido_paterno, e.apellido_materno) AS Nombre,
            COALESCE(s.nombre_sucursal, 'SIN SUCURSAL') AS Sucursal,
            COALESCE(d.nombre_departamento, 'SIN DEPARTAMENTO') AS Departamento,
            COALESCE(p.nombre_puesto, 'SIN PUESTO') AS Puesto,
            COALESCE(ce.correo_gmail, '') AS `Correo Gmail`,
            COALESCE(ce.correo_corporativo, '') AS `Correo Institucional`,
            COALESCE(lt.numero, ic.numero, '') AS Celular
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
            WHERE id_estatus_correo = 1 AND codigo_empleado IS NOT NULL
            GROUP BY cod_clean
        ) ce ON TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR)) = ce.cod_clean
        LEFT JOIN (
            SELECT 
                TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) AS cod_clean,
                MAX(numero) AS numero
            FROM lineas_telefonicas
            WHERE codigo_empleado IS NOT NULL AND TRIM(numero) != ''
            GROUP BY cod_clean
        ) lt ON TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR)) = lt.cod_clean
        LEFT JOIN (
            SELECT 
                TRIM(LEADING '0' FROM CAST(codigo_empleado AS CHAR)) AS cod_clean, 
                MAX(numero) AS numero
            FROM inventario_celulares
            WHERE codigo_empleado IS NOT NULL AND numero IS NOT NULL AND TRIM(numero) != ''
            GROUP BY cod_clean
        ) ic ON TRIM(LEADING '0' FROM CAST(e.codigo AS CHAR)) = ic.cod_clean
        WHERE e.id_estatus_empleado = 1
        ORDER BY 
            Sucursal ASC, 
            Departamento ASC, 
            Puesto ASC, 
            Nombre ASC
    """
    try:
        df = pd.read_sql(query, conn)
        conn.close()

        if not df.empty:
            # Filtrar solo colaboradores que tengan al menos 1 medio de contacto asignado
            mascara_contacto = (
                (df["Correo Gmail"].astype(str).str.strip() != "") |
                (df["Correo Institucional"].astype(str).str.strip() != "") |
                (df["Celular"].astype(str).str.strip() != "")
            )
            df = df[mascara_contacto].reset_index(drop=True)

        return df
    except Exception as e:
        conn.close()
        print(f"⚠️ Error al consultar lista de distribución: {e}")
        return pd.DataFrame()

def auto_sincronizar_google_sheet():
    """Autentica con la Service Account y actualiza la hoja 'Colaboradores' en Google Drive."""
    try:
        if not CREDS_PATH.exists():
            return False, f"No existe credentials.json en la ruta: {CREDS_PATH}"

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_file(str(CREDS_PATH), scopes=scopes)
        client = gspread.authorize(creds)

        df = obtener_lista_distribucion_df()
        if df.empty:
            return False, "No se encontraron colaboradores activos con medios de contacto asignados."

        df = df.fillna("")

        # Apertura de hoja y vaciado previo para consistencia
        sheet = client.open_by_key(SPREADSHEET_ID).worksheet("Colaboradores")
        sheet.clear()

        # Inserción con cabeceras completas
        valores = [df.columns.values.tolist()] + df.astype(str).values.tolist()
        sheet.update(range_name="A1", values=valores)
        return True, "OK"
    except Exception as e:
        err_msg = str(e)
        print(f"⚠️ Error al sincronizar con Google Sheets: {err_msg}")
        return False, err_msg