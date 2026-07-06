# 🛠️ Monitoreo de enlaces MikroTik – Script en Bash

Soy ingeniero de sistemas con experiencia en redes, mainframe y automatización legacy.  
Este repositorio documenta un proyecto real: monitoreo automatizado de enlaces WAN en 5 sucursales con notificaciones por Telegram.

## 🧑‍💻 Perfil técnico (resumido)

- Ingeniero en Computación (CENEVAL), especialidad en Sistemas Digitales.
- CCNA v4.0 completo (Cisco, consola, routing/switching).
- Experiencia en NOC, SysAdmin, Mainframe (COBOL, CICS, TSO).
- Automatización con scripts `.bat` y lógica en PHP/MySQL.
- Actualmente Jefe de Sistemas en Agrocisa (5 sucursales, MikroTik, VLANs, failover, ZeroTier).

## 🎯 Qué hace el script

- Inspección síncrona: Se conecta por SSH a 5 routers MikroTik usando puerto y llaves específicas enlazadas al usuario de monitoreo.
- Extrae el estado de cada enlace desde la tabla de rutas (activo, respaldo, caído).
- Persistencia en RAM (SSOT): Define al arranque o una interrupción en un Punto Único de Verdad con los estados esperados de la red para comparar o tener datos correctos.
- Guarda un histórico diario en CSV con fecha, hora, sucursal, enlace, gateway, distancia y estado.
- Mantiene un archivo `Estado-actual.csv` con el último estado conocido de cada enlace.
- Cuando un enlace se cae, registra el timestamp de caída y lo conserva entre ejecuciones.
- Calcula los minutos transcurridos y envía una alerta por Telegram si la caída supera los 20 minutos (solo una vez, en el rango de 20 a 24 minutos).
- Cuando el enlace se recupera, envía otra alerta al instante.
- Corre cada 5 minutos vía `cron` (autónomo, sin depender del entorno).

## 📁 Estructura del repo
```
monitoreo-mikrotik/
├── monitoreo_enlaces.sh # Script principal (con alertas y persistencia)
├── README.md # Este archivo
└── logs/ # Se genera localmente (CSV histórico y estado actual)
```

## 🔧 Instalación rápida

1. Clonar el repo.
2. Ajustar IPs, puerto, usuario y ruta de la llave SSH en el script.
3. Agregar a crontab (por ejemplo, cada 5 minutos):

```bash
*/5 * * * * /bin/bash /ruta/al/monitoreo_enlaces.sh
```

4. Configurar el bot de Telegram (token y chat ID) dentro del script.

## 📌 Tecnologías usadas
- Bash (arrays asociativos, timestamps, redirecciones, bucles)

- OpenSSH (conexiones a routers, llaves RSA 2048)

- cron (ejecución automática)

- API de Telegram (notificaciones)

- MikroTik CLI (tabla de rutas)

## 🚀 Estado actual
- ✅ Monitoreo de 5 sucursales (y sitio caído completo)

- ✅ Detección de caída de enlaces (flag Is o No route to host)

- ✅ Persistencia de timestamps entre ejecuciones

- ✅ Alertas por Telegram (caída y recuperación, con retardo de 20 min)

- ✅ Histórico diario en CSV

- ✅ Contador de ejecuciones como métrica

- ✅ Arranque en frío (SSOT con valores por defecto)

## 📞 Contacto
Este repo es mi portafolio público. Casos de éxito (migración de APs, eliminación de proveedores chantajistas, failover, etc.) disponibles en mi CV y LinkedIn.

Última actualización: junio 2026