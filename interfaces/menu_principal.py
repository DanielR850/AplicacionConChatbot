import tkinter as tk
from PIL import Image, ImageTk
import os
import sys

from interfaces.subir_documento import SubirDocumento
from interfaces.ver_documentos import VerDocumentos
from interfaces.ver_enlaces import VerEnlaces
from interfaces.login import Login
from interfaces.Calendario import Calendario
from interfaces.ChatbotPantalla import ChatbotPantalla

def obtener_ruta_recurso(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

class MenuPrincipal(tk.Frame):
    def __init__(self, master, id_usuario_actual):
        super().__init__(master, bg="white")
        self.master = master
        self.id_usuario_actual = id_usuario_actual
        self.master.geometry("900x500")
        self.pack(fill="both", expand=True)

        # --------- Encabezado ---------
        tk.Label(self, text="Control de Caducidad de Documentos Oficiales",
                 font=("Helvetica", 10, "bold"), bg="white", fg="gray").place(x=10, y=5)
        tk.Label(self, text="Menú Principal",
                 font=("Helvetica", 16, "bold"), bg="white", fg="black").place(x=10, y=25)

        # --------- Funciones navegación ---------
        def ir_a_subir_documento():
            self.master.mostrar_pantalla(SubirDocumento, id_usuario_actual=self.id_usuario_actual)

        def ir_a_documentos_cargados():
            self.master.mostrar_pantalla(VerDocumentos, id_usuario_actual=self.id_usuario_actual)

        def ir_a_enlaces():
            self.master.mostrar_pantalla(VerEnlaces, id_usuario_actual=self.id_usuario_actual)

        def ir_a_documentos_vencidos():
            self.master.mostrar_pantalla(VerDocumentos, id_usuario_actual=self.id_usuario_actual, filtro="vencidos")

        def ir_a_notificaciones():
            self.master.mostrar_pantalla(VerDocumentos, id_usuario_actual=self.id_usuario_actual, filtro="proximos")

        def ir_a_calendario():
            self.master.mostrar_pantalla(Calendario, id_usuario_actual=self.id_usuario_actual)

        def cerrar_sesion():
            self.master.mostrar_pantalla(Login)

        def ir_a_chatbot():
            self.master.mostrar_pantalla(ChatbotPantalla, id_usuario_actual=self.id_usuario_actual)



        tk.Button(self, text="📅", font=("Arial", 12), bg="white", bd=0, cursor="hand2",
                  command=ir_a_calendario, activebackground="white").place(x=760, y=15)

        tk.Button(self, text="← Salir", font=("Arial", 10), bg="white", bd=0, cursor="hand2",
                command=cerrar_sesion, activebackground="white").place(x=800, y=15)



        # --------- Línea superior ---------
        canvas_top = tk.Canvas(self, width=900, height=2, bg="white", highlightthickness=0)
        canvas_top.place(x=0, y=60)
        canvas_top.create_line(0, 1, 900, 1, fill="black", width=2)

        # --------- Menú lateral ---------
        botones = [
            ("Subir\nDocumentos", 80, ir_a_subir_documento),
            ("Documentos\nCargados", 140, ir_a_documentos_cargados),
            ("Chatbot\nDocumental", 200, ir_a_chatbot),
            ("Documentos\nVencidos", 260, ir_a_documentos_vencidos),
        ]

        for texto, y, funcion in botones:
            tk.Button(self, text=texto, font=("Arial", 10), bg="#abe3f9",
                      width=20, height=2, relief="flat", cursor="hand2",
                      command=funcion).place(x=20, y=y)

        # --------- Línea divisoria ---------
        canvas_div = tk.Canvas(self, width=2, height=500, bg="white", highlightthickness=0)
        canvas_div.place(x=220, y=60)
        canvas_div.create_line(1, 0, 1, 500, fill="black", width=1)

        # --------- Imagen decorativa central ---------
        ruta_img_central = obtener_ruta_recurso(os.path.join("assets", "image5.png"))
        if os.path.exists(ruta_img_central):
            img = Image.open(ruta_img_central).resize((180, 180))
            doc_tk = ImageTk.PhotoImage(img)
            tk.Label(self, image=doc_tk, bg="white").place(x=450, y=140)
            self.doc_tk = doc_tk  # Evita que se elimine la referencia
