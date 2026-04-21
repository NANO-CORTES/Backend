FROM python:3.11-slim
<<<<<<< HEAD

# 1. Instalamos librerías del sistema necesarias para PostgreSQL y validación de archivos
RUN apt-get update && apt-get install -y \
    libmagic1 \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2. Copiamos e instalamos desde el archivo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. EL TRUCO FINAL: Forzamos la instalación de 'tenacity' por si el paso anterior falló
RUN pip install tenacity requests python-magic

COPY ./app ./app

EXPOSE 8002

# 4. Aseguramos que corra en el puerto correcto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
=======
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
>>>>>>> feature/mis-cambios
