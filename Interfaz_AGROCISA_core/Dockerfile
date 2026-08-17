# 1. Base oficial de Python
FROM python:3.11-slim

# 2. Carpeta de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar el requirements.txt limpio
COPY requirements.txt .

# 4. Instalar las dependencias exactas
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiar todo tu código (app.py, módulos, templates, etc.)
COPY . .

# 6. Puerto de Streamlit
EXPOSE 8501

# 7. Ejecutar Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]