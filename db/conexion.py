import os
import sys
import sqlite3

def obtener_ruta_db():
    base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))
    ruta_db = os.path.join(base_dir, "DBS", "gestion_documentos.db")
    os.makedirs(os.path.dirname(ruta_db), exist_ok=True)
    return ruta_db

def conectar():
    ruta = obtener_ruta_db()
    return sqlite3.connect(ruta)
