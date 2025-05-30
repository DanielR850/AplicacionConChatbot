import os
import tempfile
from cryptography.fernet import Fernet
import shutil
import uuid
from utils.rutas import obtener_ruta_clave
KEY_FILE = obtener_ruta_clave()


def generar_clave():
    clave = Fernet.generate_key()
    with open(KEY_FILE, "wb") as archivo:
        archivo.write(clave)

def cargar_clave():
    if not os.path.exists(KEY_FILE):
        generar_clave()
    with open(KEY_FILE, "rb") as archivo:
        return archivo.read()

def encriptar_archivo(ruta_archivo):
    clave = cargar_clave()
    fernet = Fernet(clave)

    with open(ruta_archivo, "rb") as file:
        datos = file.read()

    datos_encriptados = fernet.encrypt(datos)

    with open(ruta_archivo, "wb") as file:
        file.write(datos_encriptados)

def desencriptar_archivo(ruta_cifrada):
    try:
        clave = cargar_clave()
        fernet = Fernet(clave)

        with open(ruta_cifrada, "rb") as file:
            datos = file.read()

        datos_desencriptados = fernet.decrypt(datos)

        nombre = os.path.basename(ruta_cifrada)
        nombre_unico = f"{uuid.uuid4().hex}_{nombre}"
        ruta_temp = os.path.join("temp", nombre_unico)
        os.makedirs("temp", exist_ok=True)

        with open(ruta_temp, "wb") as file:
            file.write(datos_desencriptados)

        print(f"✅ Archivo desencriptado temporal: {ruta_temp}")
        return os.path.abspath(ruta_temp)

    except Exception as e:
        print(f"❌ Error al desencriptar {ruta_cifrada}: {e}")
        return None
