FROM python:3.11-slim

# Evita que Python genere archivos .pyc y fuerza salida en consola inmediata
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Copiamos e instalamos dependencias primero (aprovecha la caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copiamos el código fuente limpio
COPY . .

# 3. Comando que ejecuta el script al arrancar el contenedor
CMD ["python", "main.py"]