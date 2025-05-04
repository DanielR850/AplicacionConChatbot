import os
import tempfile
from cryptography.fernet import Fernet

KEY_FILE = "clave.key"

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

def desencriptar_archivo(ruta_archivo):
    clave = cargar_clave()
    fernet = Fernet(clave)

    with open(ruta_archivo, "rb") as file:
        datos_encriptados = file.read()

    datos_desencriptados = fernet.decrypt(datos_encriptados)

    # Crear archivo temporal desencriptado
    nombre = os.path.basename(ruta_archivo)
    temp_dir = os.path.join(tempfile.gettempdir(), "desencriptado")
    os.makedirs(temp_dir, exist_ok=True)
    ruta_temp = os.path.join(temp_dir, f"des_{nombre}")

    with open(ruta_temp, "wb") as file:
        file.write(datos_desencriptados)

    return ruta_temp  # Devuelve ruta temporal
