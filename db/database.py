import sqlite3
import os
import sys

def crear_bd():
    # Obtener la ruta absoluta correcta incluso en el .exe
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    ruta_db = os.path.join(base_dir, "..", "gestion_documentos.db")
    ruta_db = os.path.abspath(ruta_db)

    conn = sqlite3.connect(ruta_db)
    cursor = conn.cursor()

    # Crear tabla Usuarios
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_usuario TEXT NOT NULL,
            correo TEXT UNIQUE,
            contraseña TEXT NOT NULL
        );
    """)

    # Crear tabla Enlaces_Oficiales
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Enlaces_Oficiales (
            id_enlace INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_tramite TEXT NOT NULL,
            url TEXT NOT NULL
        );
    """)

    # Crear tabla Documentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Documentos (
            id_documento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            id_enlace INTEGER NOT NULL,
            nombre_documento TEXT NOT NULL,
            ruta_archivo TEXT NOT NULL,
            fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_vencimiento DATE NOT NULL,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
            FOREIGN KEY (id_enlace) REFERENCES Enlaces_Oficiales(id_enlace) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()

