import tkinter as tk
from db.database import crear_bd
from interfaces.login import Login
from interfaces.menu_principal import MenuPrincipal
from interfaces.ver_documentos import VerDocumentos
from interfaces.ver_enlaces import VerEnlaces
from interfaces.subir_documento import SubirDocumento
from interfaces.Calendario import Calendario
from interfaces.crear_usuario import CrearUsuario  # ✅ NUEVO IMPORT

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Control de Documentos Oficiales")
        self.resizable(False, False)

        crear_bd()  # Crea la base de datos si no existe

        self.current_frame = None
        self.mostrar_pantalla(Login)

    def mostrar_pantalla(self, pantalla_class, **kwargs):
        # Destruir pantalla anterior si existe
        if self.current_frame is not None:
            self.current_frame.destroy()

        # Crear nueva pantalla
        nueva_pantalla = pantalla_class(self, **kwargs) if kwargs else pantalla_class(self)
        nueva_pantalla.pack(fill="both", expand=True)
        self.current_frame = nueva_pantalla

        # Ajustar tamaño automáticamente según la pantalla
        pantalla_nombre = pantalla_class.__name__

        if pantalla_nombre in ("Login", "CrearUsuario"):  # ✅ Añadido CrearUsuario
            self.geometry("650x350")
        else:
            self.geometry("900x500")

if __name__ == "__main__":
    app = App()
    app.mainloop()
