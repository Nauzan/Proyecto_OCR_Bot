# Usamos una imagen base de Python
FROM python:3.9-slim

# Instalamos Tesseract OCR y dependencias de sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1-mesa-glx \
    && apt-get clean

# Creamos las carpetas necesarias
WORKDIR /app
RUN mkdir -p descargas procesados

# Copiamos tus archivos al servidor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Comando para iniciar tu script
CMD ["python", "lector_inteligente.py"]