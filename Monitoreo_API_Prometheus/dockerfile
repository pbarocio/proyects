# 1. Imagen base ligera de Python
FROM python:3.12-slim

# 2. Carpeta de trabajo dentro del contenedor
WORKDIR /app

# 3. Forzar salida inmediata de logs a la terminal
ENV PYTHONUNBUFFERED=1

# 4. Aprovechar el caché de capas para las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar el resto del código del proyecto
COPY . .

# 6. Comando de arranque
CMD ["python", "main.py"]