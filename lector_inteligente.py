import cv2
import pytesseract
from PIL import Image, ImageOps, ImageFilter
import pandas as pd
import os
import re
import shutil
import platform
from datetime import datetime

# 1. AJUSTE NUBE: Configuración inteligente de rutas
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    CARPETA_PROYECTO = r'C:\Proyecto_OCR'
else:
    # Ruta estándar para Linux (Render)
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'
    CARPETA_PROYECTO = os.getcwd()

CARPETA_DESCARGAS = os.path.join(CARPETA_PROYECTO, 'descargas')
CARPETA_PROCESADOS = os.path.join(CARPETA_PROYECTO, 'procesados')
ARCHIVO_EXCEL = os.path.join(CARPETA_PROYECTO, 'datos_extraidos.csv')

# Crear carpetas si no existen
for carpeta in [CARPETA_DESCARGAS, CARPETA_PROCESADOS]:
    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

# --- AJUSTE FINAL: Función de Preprocesamiento integrada ---
def mejorar_imagen_ocr(ruta_imagen):
    """Aplica filtros para que Tesseract lea mejor (Grises, Contraste y Nitidez)"""
    try:
        with Image.open(ruta_imagen) as img:
            img = img.convert('L') # Escala de grises
            img = ImageOps.autocontrast(img) # Mejorar contraste
            img = img.filter(ImageFilter.SHARPEN) # Aumentar nitidez
            return img
    except Exception as e:
        print(f"⚠️ Error mejorando imagen: {e}")
        return Image.open(ruta_imagen)

def limpiar_texto_general(texto):
    if not texto: return "Desconocido"
    limpio = texto.replace("nÃºmero", "numero").replace("Â", "").replace("©", "")
    return limpio.strip()

def extraer_solo_telefono(texto):
    telefono = re.sub(r'[^0-9+]', '', texto)
    if len(telefono) < 7:
        return "Revisión Manual"
    return telefono

def procesar_imagen_especifica(nombre_imagen):
    ruta_img = os.path.join(CARPETA_DESCARGAS, nombre_imagen)
    
    try:
        # Usamos la imagen MEJORADA con los filtros de tu compañera
        imagen_preprocesada = mejorar_imagen_ocr(ruta_img)
        texto_raw = pytesseract.image_to_string(imagen_preprocesada, lang='spa')
    except Exception as e:
        print(f"❌ No se pudo leer {nombre_imagen}: {e}")
        return

    if texto_raw.strip():
        lineas = [l for l in texto_raw.split('\n') if l.strip()]
        nombre_raw = lineas[0] if len(lineas) > 0 else "Desconocido"
        
        nombre_limpio = limpiar_texto_general(nombre_raw)
        telefono_limpio = extraer_solo_telefono(texto_raw)

        nuevo_registro = {
            'Fecha_Captura': [datetime.now().strftime("%d/%m/%Y %H:%M")],
            'Empresa_Nombre': [nombre_limpio],
            'Telefono_Limpio': [telefono_limpio],
            'Imagen_Referencia': [nombre_imagen],
            'Estado': ['Verificado' if telefono_limpio != "Revisión Manual" else 'Incompleto']
        }
        
        df = pd.DataFrame(nuevo_registro)

        if not os.path.isfile(ARCHIVO_EXCEL):
            df.to_csv(ARCHIVO_EXCEL, index=False, encoding='utf-8-sig')
        else:
            df.to_csv(ARCHIVO_EXCEL, mode='a', index=False, header=False, encoding='utf-8-sig')
        
        print(f"✅ Guardado: {nombre_limpio} | {telefono_limpio}")
        
        # Movemos a procesados
        shutil.move(ruta_img, os.path.join(CARPETA_PROCESADOS, nombre_imagen))
        print(f"📦 Archivo archivado.")
        
    else:
        print(f"⚠️ {nombre_imagen}: No se detectó texto legible.")

def escanear_y_procesar_todo():
    if not os.path.exists(CARPETA_DESCARGAS):
        print(f"❌ La carpeta {CARPETA_DESCARGAS} no existe.")
        return

    archivos = [f for f in os.listdir(CARPETA_DESCARGAS) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    if not archivos:
        print("📭 No hay imágenes nuevas.")
        return

    print(f"📂 Encontradas {len(archivos)} imágenes. Iniciando pipeline...")
    for foto in archivos:
        procesar_imagen_especifica(foto)

if __name__ == "__main__":
    escanear_y_procesar_todo()