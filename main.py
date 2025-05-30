# main.py
import os
import sys
import tkinter as tk
from tkinter import messagebox
from db.database import crear_bd
from interfaces.login import Login
from utils.programar_tarea import programar_tarea_verificacion
from utils.crypto_utils import generar_clave

# Ruta base dependiendo de si es .exe o .py
BASE_DIR = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__))

# ✅ Ruta a la clave de cifrado
CLAVE_PATH = os.path.join(BASE_DIR, "clave.key")
if not os.path.exists(CLAVE_PATH):
    generar_clave()

# ✅ Ejecutar tarea programada
programar_tarea_verificacion()

# ✅ Crear la base de datos en la carpeta /DBS si no existe
crear_bd()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Control de Documentos Oficiales")
        self.resizable(False, False)
        self.current_frame = None
        self.mostrar_pantalla(Login)

    def mostrar_pantalla(self, pantalla_class, **kwargs):
        try:
            # 🔁 Destruir el frame anterior
            if self.current_frame:
                self.current_frame.destroy()

            # 🔁 Crear nueva pantalla
            nueva_pantalla = pantalla_class(self, **kwargs)
            nueva_pantalla.pack(fill="both", expand=True)
            self.current_frame = nueva_pantalla

            # ✅ Ajustar tamaño de ventana
            nombre_pantalla = pantalla_class.__name__
            if nombre_pantalla in ("Login", "CrearUsuario"):
                width, height = 700, 400
            else:
                width, height = 900, 550

            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = int((screen_width - width) / 2)
            y = int((screen_height - height) / 2)
            self.geometry(f"{width}x{height}+{x}+{y}")

            print(f"[DEBUG] Cambio a: {nombre_pantalla}")

        except Exception as e:
            import traceback
            with open("pantalla_error_log.txt", "w", encoding="utf-8") as f:
                f.write(traceback.format_exc())
            messagebox.showerror("Error crítico", "Ocurrió un error al cambiar de pantalla.\n\nDetalles en pantalla_error_log.txt")

if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except Exception as e:
        import traceback
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(traceback.format_exc())
