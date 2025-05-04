import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import os
import fitz  # pymupdf
import webbrowser
from utils.crypto_utils import desencriptar_archivo  # Asegúrate de tener esta función

class VerDocumentos(tk.Frame):
    def __init__(self, master, id_usuario_actual, filtro=None):
        super().__init__(master, bg="white")
        self.master = master
        self.master.geometry("900x500")
        self.pack(fill="both", expand=True)
        self.filtro = filtro
        self.id_usuario_actual = id_usuario_actual
        self.entrada_busqueda = None
        self.resultado_documentos = []

        self.titulo_superior()
        self.mostrar_documentos()

    def titulo_superior(self):
        tk.Label(self, text="Control de Caducidad de Documentos Oficiales",
                 font=("Helvetica", 10, "bold"), bg="white", fg="gray").place(x=10, y=5)
        tk.Label(self, text="Documentos Cargados",
                 font=("Helvetica", 16, "bold"), bg="white", fg="black").place(x=10, y=25)

        # Botón SALIR arriba a la derecha
        tk.Button(self, text="← Salir", font=("Arial", 10), bg="white", fg="black", bd=0,
                  cursor="hand2", command=self.volver_menu, activebackground="white").place(x=800, y=15)

        # Campo de búsqueda
        self.entrada_busqueda = tk.Entry(self, width=30, font=("Arial", 10))
        self.entrada_busqueda.place(x=300, y=25)
        tk.Button(self, text="🔍", font=("Arial", 10), bg="white", bd=0, cursor="hand2",
                  command=self.mostrar_documentos).place(x=540, y=23)

        # Línea divisoria
        canvas = tk.Canvas(self, width=900, height=2, bg="white", highlightthickness=0)
        canvas.place(x=0, y=60)
        canvas.create_line(0, 1, 900, 1, fill="black", width=2)

    def mostrar_documentos(self):
        if hasattr(self, 'frame_docs'):
            self.frame_docs.destroy()

        conn = sqlite3.connect("gestion_documentos.db")
        cursor = conn.cursor()

        query = """
            SELECT d.id_documento, d.nombre_documento, d.ruta_archivo, e.url 
            FROM Documentos d
            JOIN Enlaces_Oficiales e ON d.id_enlace = e.id_enlace
            WHERE d.id_usuario = ?
        """
        params = [self.id_usuario_actual]

        if self.filtro == "proximos":
            query += " AND d.fecha_vencimiento BETWEEN date('now') AND date('now', '+7 days')"
        elif self.filtro == "vencidos":
            query += " AND d.fecha_vencimiento < date('now')"

        cursor.execute(query, params)
        documentos = cursor.fetchall()
        conn.close()

        texto_busqueda = self.entrada_busqueda.get().strip().lower() if self.entrada_busqueda else ""
        if texto_busqueda:
            documentos = [doc for doc in documentos if texto_busqueda in doc[1].lower()]

        self.frame_docs = tk.Frame(self, bg="white")
        self.frame_docs.place(x=50, y=80)

        for i, (id_doc, nombre, ruta, url) in enumerate(documentos):
            contenedor = tk.Frame(self.frame_docs, bg="white", bd=1, relief="solid")
            contenedor.grid(row=i // 4, column=i % 4, padx=15, pady=15)

            ruta_temporal = desencriptar_archivo(ruta)
            imagen = self.generar_miniatura(ruta_temporal)
            img_tk = ImageTk.PhotoImage(imagen)

            btn = tk.Button(contenedor, image=img_tk, bg="white", bd=0,
                            command=lambda d=id_doc: self.ver_enlaces_doc(d))
            btn.image = img_tk
            btn.pack()

            tk.Label(contenedor, text=nombre, bg="white", wraplength=120,
                     justify="center").pack(pady=2)

            tk.Button(contenedor, text="🗑 Eliminar", font=("Arial", 8), bg="#ffcccc", bd=0,
                      command=lambda d=id_doc: self.eliminar_documento(d)).pack(pady=3)

    def generar_miniatura(self, ruta):
        try:
            doc = fitz.open(ruta)
            pagina = doc.load_page(0)
            pix = pagina.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
            img_path = os.path.join("temp", f"{os.path.basename(ruta)}.png")
            os.makedirs("temp", exist_ok=True)
            pix.save(img_path)
            img = Image.open(img_path).resize((120, 120))
            return img
        except Exception:
            return Image.new("RGB", (120, 120), color="gray")

    def eliminar_documento(self, id_documento):
        confirm = messagebox.askyesno("Confirmar eliminación", "¿Estás seguro de eliminar este documento?")
        if confirm:
            conn = sqlite3.connect("gestion_documentos.db")
            cursor = conn.cursor()

            cursor.execute("SELECT ruta_archivo FROM Documentos WHERE id_documento = ?", (id_documento,))
            ruta = cursor.fetchone()
            if ruta and os.path.exists(ruta[0]):
                os.remove(ruta[0])

            cursor.execute("DELETE FROM Documentos WHERE id_documento = ?", (id_documento,))
            conn.commit()
            conn.close()

            messagebox.showinfo("Eliminado", "Documento eliminado correctamente.")
            self.mostrar_documentos()

    def ver_enlaces_doc(self, id_documento):
        from interfaces.ver_enlaces import VerEnlaces
        self.master.mostrar_pantalla(VerEnlaces, id_documento=id_documento, id_usuario_actual=self.id_usuario_actual)

    def volver_menu(self):
        from interfaces.menu_principal import MenuPrincipal
        self.master.mostrar_pantalla(MenuPrincipal, id_usuario_actual=self.id_usuario_actual)
