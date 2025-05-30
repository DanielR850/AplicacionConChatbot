import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys
import sqlite3

from interfaces.subir_documento import SubirDocumento
from interfaces.ver_documentos import VerDocumentos
from interfaces.ver_enlaces import VerEnlaces
from interfaces.login import Login
from interfaces.Calendario import Calendario
from interfaces.exportar_reportes import ExportarReportes
from interfaces.chatbot_basico import ChatbotBasico  # Asegúrate de que esté creado

# --- Ruta de ejecución (funciona en .py y .exe) ---
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.abspath(".")

IMG_PATH = os.path.join(BASE_DIR, "assets", "image5.png")

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

        # --------- Botones top ---------
        tk.Button(self, text="📅", font=("Arial", 12), bg="white", bd=0, cursor="hand2",
                  command=self.ir_a_calendario, activebackground="white").place(x=760, y=15)

        tk.Button(self, text="← Salir", font=("Arial", 10), bg="white", bd=0, cursor="hand2",
                  command=self.cerrar_sesion, activebackground="white").place(x=800, y=15)

        canvas_top = tk.Canvas(self, width=900, height=2, bg="white", highlightthickness=0)
        canvas_top.place(x=0, y=60)
        canvas_top.create_line(0, 1, 900, 1, fill="black", width=2)

        # --------- Botones laterales ---------
        botones = [
            ("Subir\nDocumentos", 80, self.ir_a_subir_documento),
            ("Documentos\nCargados", 140, self.ir_a_documentos_cargados),
            ("Chatbot\nBásico", 200, self.ir_a_chatbot),
            ("Documentos\nVencidos", 260, self.ir_a_documentos_vencidos),
            ("Exportar\nReporte", 320, self.ir_a_exportar_reportes),
            ("📧 Enviar\nCorreos Ahora", 380, self.enviar_correos)
        ]

        for texto, y, funcion in botones:
            tk.Button(self, text=texto, font=("Arial", 10), bg="#abe3f9",
                      width=20, height=2, relief="flat", cursor="hand2",
                      command=funcion).place(x=20, y=y)

        # --------- Línea divisoria ---------
        canvas_div = tk.Canvas(self, width=2, height=500, bg="white", highlightthickness=0)
        canvas_div.place(x=220, y=60)
        canvas_div.create_line(1, 0, 1, 500, fill="black", width=1)

        # --------- Cargar imagen diferida ---------
        self.after(100, self.cargar_imagen)

    def cargar_imagen(self):
        try:
            if os.path.exists(IMG_PATH):
                img = Image.open(IMG_PATH).resize((180, 180))
                self.doc_tk = ImageTk.PhotoImage(img)
                tk.Label(self, image=self.doc_tk, bg="white").place(x=450, y=140)
        except Exception as e:
            print(f"[❌ Imagen] Error al cargar la imagen: {e}")

    # --- Navegación ---
    def ir_a_subir_documento(self):
        self.master.mostrar_pantalla(SubirDocumento, id_usuario_actual=self.id_usuario_actual)

    def ir_a_documentos_cargados(self):
        self.master.mostrar_pantalla(VerDocumentos, id_usuario_actual=self.id_usuario_actual)

    def ir_a_enlaces(self):
        self.master.mostrar_pantalla(VerEnlaces, id_usuario_actual=self.id_usuario_actual)

    def ir_a_documentos_vencidos(self):
        self.master.mostrar_pantalla(VerDocumentos, id_usuario_actual=self.id_usuario_actual, filtro="vencidos")

    def ir_a_notificaciones(self):
        self.master.mostrar_pantalla(VerDocumentos, id_usuario_actual=self.id_usuario_actual, filtro="proximos")

    def ir_a_exportar_reportes(self):
        self.master.mostrar_pantalla(ExportarReportes, id_usuario_actual=self.id_usuario_actual)

    def ir_a_calendario(self):
        self.master.mostrar_pantalla(Calendario, id_usuario_actual=self.id_usuario_actual)

    def ir_a_chatbot(self):
        self.master.mostrar_pantalla(ChatbotBasico, id_usuario_actual=self.id_usuario_actual)

    def cerrar_sesion(self):
        self.master.mostrar_pantalla(Login)

    def enviar_correos(self):
        try:
            from utils.verificador import verificar_vencimientos
            verificar_vencimientos()
            messagebox.showinfo("✅ Listo", "Se verificaron los documentos y se enviaron correos (si correspondía).")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo ejecutar verificación:\n{e}")