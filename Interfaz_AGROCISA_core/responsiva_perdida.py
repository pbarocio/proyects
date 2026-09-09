import sqlite3
import pandas as pd

conexion = sqlite3.connect("agrocisa_core.db")

# 1. Responsivas totales
total = pd.read_sql_query("SELECT COUNT(*) as total FROM responsivas_celulares", conexion)
print(f"Responsivas totales: {total['total'][0]}")

# 2. Responsivas sin IMEI en inventario
sin_imei = pd.read_sql_query("""
    SELECT r.* 
    FROM responsivas_celulares r
    LEFT JOIN inventario_celulares ic ON r.imei = ic.imei
    WHERE ic.imei IS NULL
""", conexion)
print(f"Responsivas sin IMEI en inventario: {len(sin_imei)}")
if len(sin_imei) > 0:
    print(sin_imei[['id_responsiva_celular', 'imei']])

# 3. Responsivas sin id_equipo en equipos_2026
sin_equipo = pd.read_sql_query("""
    SELECT r.id_responsiva_celular, r.imei, ic.id_equipo
    FROM responsivas_celulares r
    JOIN inventario_celulares ic ON r.imei = ic.imei
    LEFT JOIN equipos_2026 eq ON ic.id_equipo = eq.id_equipo
    WHERE eq.id_equipo IS NULL
""", conexion)
print(f"Responsivas sin id_equipo en equipos_2026: {len(sin_equipo)}")
if len(sin_equipo) > 0:
    print(sin_equipo[['id_responsiva_celular', 'imei', 'id_equipo']])

# 4. Responsivas sin id_condicion en condicion
sin_condicion = pd.read_sql_query("""
    SELECT r.id_responsiva_celular, r.imei, ic.id_condicion
    FROM responsivas_celulares r
    JOIN inventario_celulares ic ON r.imei = ic.imei
    LEFT JOIN condicion c ON ic.id_condicion = c.id_condicion
    WHERE c.id_condicion IS NULL
""", conexion)
print(f"Responsivas sin id_condicion en condicion: {len(sin_condicion)}")
if len(sin_condicion) > 0:
    print(sin_condicion[['id_responsiva_celular', 'imei', 'id_condicion']])

# 5. Responsivas sin id_cargador en cargadores
sin_cargador = pd.read_sql_query("""
    SELECT r.id_responsiva_celular, r.imei, ic.id_cargador
    FROM responsivas_celulares r
    JOIN inventario_celulares ic ON r.imei = ic.imei
    LEFT JOIN cargadores ca ON ic.id_cargador = ca.id_cargador
    WHERE ca.id_cargador IS NULL
""", conexion)
print(f"Responsivas sin id_cargador en cargadores: {len(sin_cargador)}")
if len(sin_cargador) > 0:
    print(sin_cargador[['id_responsiva_celular', 'imei', 'id_cargador']])

# 6. Responsivas sin id_caja en caja
sin_caja = pd.read_sql_query("""
    SELECT r.id_responsiva_celular, r.imei, ic.id_caja
    FROM responsivas_celulares r
    JOIN inventario_celulares ic ON r.imei = ic.imei
    LEFT JOIN caja ON ic.id_caja = caja.id_caja
    WHERE caja.id_caja IS NULL
""", conexion)
print(f"Responsivas sin id_caja en caja: {len(sin_caja)}")
if len(sin_caja) > 0:
    print(sin_caja[['id_responsiva_celular', 'imei', 'id_caja']])

conexion.close()