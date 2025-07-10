# Usar una imagen base de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar los archivos de requisitos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la aplicación
COPY . .

# Crear un volumen para la base de datos
VOLUME ["/app/data"]

# Variable de entorno para la base de datos
ENV DB_PATH=/app/data/technicians.db

# Comando para ejecutar la aplicación
CMD ["python", "main.py"]
