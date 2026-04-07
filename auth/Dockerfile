# Imagen base de Python
FROM python:3.11-slim

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copiar e instalar dependencias primero
# (esto aprovecha el caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Puerto que expone este microservicio
EXPOSE 8002

# Comando para arrancar el servidor
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
