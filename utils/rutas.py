import os
import sys

def obtener_base_dir():
    """
    Devuelve el directorio base del proyecto, compatible con .py y .exe.
    """
    if getattr(sys, 'frozen', False):  # Si está congelado como .exe
        return os.path.dirname(sys.executable)
    else:  # En modo .py
        return os.path.dirname(os.path.abspath(__file__))

def obtener_ruta_db():
    """
    Devuelve la ruta absoluta a db/gestion_documentos.db
    """
    return os.path.join(obtener_base_dir(), "db", "gestion_documentos.db")

def obtener_ruta_clave():
    """
    Devuelve la ruta absoluta al archivo clave.key
    """
    return os.path.join(obtener_base_dir(), "clave.key")

def ruta_recurso(rel_path):
    """
    Devuelve la ruta absoluta a cualquier recurso relativo desde la base.
    """
    return os.path.join(obtener_base_dir(), rel_path)
