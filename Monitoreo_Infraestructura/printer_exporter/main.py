import asyncio
import json
from prometheus_client import start_http_server, Gauge
from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd
)

# Métricas
PRINTER_UP = Gauge('printer_up', 'Disponibilidad SNMP (1=Online, 0=Offline)', ['printer_name', 'host', 'branch'])
TONER_LEVEL = Gauge('printer_toner_level_percent', 'Nivel de tóner (%)', ['printer_name', 'host', 'brand', 'branch'])
PRINTER_STATUS = Gauge('printer_status_code', 'Estado (2=OK, 3=Imprimiendo, 5=Error)', ['printer_name', 'host', 'brand', 'branch'])

# OIDs Estándar RFC 3805
OID_MAX_CAP = '.1.3.6.1.2.1.43.11.1.1.8.1.1'
OID_CUR_LEVEL = '.1.3.6.1.2.1.43.11.1.1.9.1.1'
OID_STATUS = '.1.3.6.1.2.1.25.3.2.1.5.1'

def load_printers():
    """Carga el inventario actualizado desde el JSON en cada ciclo."""
    try:
        with open('printers.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error leyendo printers.json: {e}")
        return []

async def snmp_get(host, oid, community='public'):
    try:
        target = await UdpTransportTarget.create((host, 161), timeout=2, retries=1)
        errorIndication, errorStatus, errorIndex, varBinds = await get_cmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0),
            target,
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )
        if errorIndication or errorStatus:
            return None
        for varBind in varBinds:
            return int(varBind[1])
    except Exception as e:
        return None

async def check_printers():
    printers = load_printers()
    
    if not printers:
        print("⚠️ No hay impresoras configuradas o falló la lectura del JSON.")
        return

    for p in printers:
        print(f"🔍 Consultando {p['name']} ({p['host']})...")
        status = await snmp_get(p['host'], OID_STATUS)
        
        # Si ni siquiera responde el estado, la declaramos DOWN
        if status is None:
            print(f"❌ {p['name']} no respondió SNMP o falló el DNS.")
            PRINTER_UP.labels(printer_name=p['name'], host=p['host'], branch=p['branch']).set(0)
            continue
        
        PRINTER_UP.labels(printer_name=p['name'], host=p['host'], branch=p['branch']).set(1)
        PRINTER_STATUS.labels(printer_name=p['name'], host=p['host'], brand=p['brand'], branch=p['branch']).set(status)

        # Consultar tóner
        max_cap = await snmp_get(p['host'], OID_MAX_CAP)
        cur_level = await snmp_get(p['host'], OID_CUR_LEVEL)
        print(f"   📊 [Debug] {p['name']} -> Status: {status}, MaxCap: {max_cap}, CurLevel: {cur_level}")

        # Evaluación inteligente de tóner para Brother / RICOH
        if cur_level == -3 or (max_cap and max_cap > 0 and cur_level > 0):
            percent = (cur_level / max_cap * 100) if (max_cap and max_cap > 0 and cur_level > 0) else 100.0
            TONER_LEVEL.labels(printer_name=p['name'], host=p['host'], brand=p['brand'], branch=p['branch']).set(percent)
        elif cur_level == 0:
            TONER_LEVEL.labels(printer_name=p['name'], host=p['host'], brand=p['brand'], branch=p['branch']).set(0.0)

async def main():
    start_http_server(9120)
    print("🚀 Exporter SNMP activo en :9120...")
    while True:
        await check_printers()
        await asyncio.sleep(60)

if __name__ == '__main__':
    asyncio.run(main())