from db.conexion import conectar

def crear_bd():
    conn = conectar()
    cursor = conn.cursor()

    print(f"[DEBUG] Base de datos en: {conn}")  # opcional

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            correo TEXT UNIQUE NOT NULL,
            contraseña TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Enlaces_Oficiales (
            id_enlace INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_tramite TEXT NOT NULL,
            url TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Documentos (
            id_documento INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER NOT NULL,
            id_enlace INTEGER NOT NULL,
            nombre_documento TEXT NOT NULL,
            ruta_archivo TEXT NOT NULL,
            fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fecha_vencimiento DATE NOT NULL,
            dias_aviso INTEGER DEFAULT NULL,
            correo_aviso TEXT DEFAULT NULL,
            FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
            FOREIGN KEY (id_enlace) REFERENCES Enlaces_Oficiales(id_enlace) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()
