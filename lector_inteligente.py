import cv2
import pytesseract
from PIL import Image, ImageOps, ImageFilter
import pandas as pd
import os
import re
import shutil
import platform
import http.server
import socketserver
import threading
import telebot
from datetime import datetime

# --- 1. CONFIGURACIÓN DE RUTAS ---
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    CARPETA_PROYECTO = r'C:\Proyecto_OCR'
else:
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
    CARPETA_PROYECTO = os.getcwd()

CARPETA_DESCARGAS = os.path.join(CARPETA_PROYECTO, 'descargas')
ARCHIVO_EXCEL = os.path.join(CARPETA_PROYECTO, 'datos_extraidos.csv')

for carpeta in [CARPETA_DESCARGAS]:
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

# --- 2. CONEXIÓN CON TELEGRAM ---
# Render usará la variable de entorno que ya configuraste
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# --- 3. SERVIDOR DE SALUD PARA RENDER ---
def responder_a_render():
    PORT = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"📡 Servidor de salud activo en puerto {PORT}")
        httpd.serve_forever()

# --- 4. LÓGICA DE PROCESAMIENTO OCR ---
def mejorar_imagen_ocr(ruta_imagen):
    with Image.open(ruta_imagen) as img:
        img = img.convert('L') 
        img = ImageOps.autocontrast(img) 
        img = img.filter(ImageFilter.SHARPEN) 
        return img

def extraer_solo_telefono(texto):
    numeros = re.findall(r'\+?\d[\d\s-]{7,}\d', texto)
    return numeros[0] if numeros else "No encontrado"

# --- 5. EL BOT ESCUCHA EL GRUPO ---
@bot.message_handler(content_types=['photo'])
def manejar_foto(message):
    try:
        print(f"📸 Foto recibida de {message.from_user.first_name}")
        
        # Descargar la foto
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        ruta_temp = os.path.join(CARPETA_DESCARGAS, f"foto_{message.chat.id}.jpg")
        
        with open(ruta_temp, 'wb') as new_file:
            new_file.write(downloaded_file)

        # Procesar con OCR
        img_prep = mejorar_imagen_ocr(ruta_temp)
        texto_raw = pytesseract.image_to_string(img_prep, lang='spa')
        
        # Extraer Datos
        lineas = [l.strip() for l in texto_raw.split('\n') if l.strip()]
        empresa = lineas[0] if lineas else "Desconocido"
        telefono = extraer_solo_telefono(texto_raw)

        # Responder al grupo inmediatamente
        respuesta = (f"✅ **¡Lectura Exitosa!**\n\n"
                     f"🏢 **Empresa:** {empresa}\n"
                     f"📞 **Teléfono:** {telefono}\n"
                     f"🕒 **Fecha:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        bot.reply_to(message, respuesta)
        print(f"✅ Datos enviados al grupo: {empresa}")

    except Exception as e:
        print(f"❌ Error: {e}")
        bot.reply_to(message, "⚠️ Error al procesar la imagen.")

if __name__ == "__main__":
    # Iniciar servidor de salud
    threading.Thread(target=responder_a_render, daemon=True).start()
    
    # Iniciar el Bot (Polling)
    print("🚀 Bot iniciado y escuchando Telegram...")
    bot.infinity_polling()
