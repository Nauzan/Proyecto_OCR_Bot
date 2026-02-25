import os
from telethon import TelegramClient

# Credenciales (verificadas y listas)
api_id = '28284962'
api_hash = 'da9c6e1da389494f1f35f5d022355c0a'
nombre_sesion = 'sesion_christian'

# Creamos la carpeta de descargas automáticamente si no existe
if not os.path.exists('descargas'):
    os.makedirs('descargas')
    print("Carpeta 'descargas' creada exitosamente.")

# Creamos el cliente de Telegram
client = TelegramClient(nombre_sesion, api_id, api_hash)

async def main():
    print("Conectando al sistema de Telegram...")
    
    try:
        # CAMBIO REALIZADO: Cambiamos 'telegram' por 'me' para leer tus Mensajes Guardados
        async for message in client.iter_messages('me', limit=10):
            # Limpiamos el texto para evitar errores si el mensaje es None
            texto = message.text[:50].replace('\n', ' ') if message.text else "Sin texto"
            print(f"ID: {message.id} | Texto: {texto}...")
            
            # Verificamos si el mensaje tiene contenido multimedia (foto)
            if message.photo:
                print(f"Descargando imagen del mensaje {message.id}...")
                # Especificamos la ruta correcta dentro de la carpeta descargas
                path = await message.download_media(file='descargas/')
                print(f"¡Imagen guardada en: {path}!")
    except Exception as e:
        print(f"Ocurrió un error durante la extracción: {e}")

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())