import tkinter as tk
from tkinter import filedialog, messagebox
from tkcalendar import DateEntry
from PIL import Image, ImageTk
import sqlite3
import shutil
import os
import fitz  # PyMuPDF
import tempfile
import sys
from utils.crypto_utils import encriptar_archivo


def obtener_ruta_recurso(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class SubirDocumento(tk.Frame):
    def __init__(self, master, id_usuario_actual=None):
        super().__init__(master, bg="white")
        self.master = master
        self.master.geometry("900x500")
        self.pack(fill="both", expand=True)
        self.id_usuario_actual = id_usuario_actual

        tk.Label(self, text="Control de Caducidad de Documentos Oficiales",
                 font=("Helvetica", 10, "bold"), bg="white", fg="gray").place(x=10, y=5)
        tk.Label(self, text="Subir Documentos",
                 font=("Helvetica", 16, "bold"), bg="white", fg="black").place(x=10, y=25)

        def ir_a_menu():
            from interfaces.menu_principal import MenuPrincipal
            self.master.mostrar_pantalla(MenuPrincipal, id_usuario_actual=self.id_usuario_actual)

        tk.Button(self, text="← Volver al menú", bg="white", bd=0, font=("Arial", 9, "bold"),
                  fg="black", cursor="hand2", command=ir_a_menu).place(x=750, y=20)

        canvas_top = tk.Canvas(self, width=900, height=2, bg="white", highlightthickness=0)
        canvas_top.place(x=0, y=60)
        canvas_top.create_line(0, 1, 900, 1, fill="black", width=2)

        canvas_div = tk.Canvas(self, width=2, height=460, bg="white", highlightthickness=0)
        canvas_div.place(x=220, y=60)
        canvas_div.create_line(1, 0, 1, 460, fill="black", width=1)

        self.crear_formulario()

        self.scroll_canvas = tk.Canvas(self, bg="white", width=620, height=360)
        self.scroll_canvas.place(x=250, y=80)

        self.scroll_frame = tk.Frame(self.scroll_canvas, bg="white")
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.scroll_canvas.yview)
        self.scrollbar.place(x=870, y=80, height=360)

        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scroll_window = self.scroll_canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind("<Configure>", lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))

        self.pdf_imgs = []

        tk.Button(self, text="Ver documento", bg="#abe3f9", width=25, command=self.ver_documento).place(x=20, y=400)
        tk.Button(self, text="Guardar documento", bg="#abe3f9", width=25, command=self.guardar_documento).place(x=20, y=440)

    def crear_formulario(self):
        frame = tk.Frame(self, bg="white")
        frame.place(x=20, y=80)

        tk.Label(frame, text="Nombre del documento:", bg="white").pack(anchor="w")
        self.entry_nombre = tk.Entry(frame, width=30)
        self.entry_nombre.pack(pady=5)

        tk.Label(frame, text="Fecha de vencimiento:", bg="white").pack(anchor="w")
        self.fecha_vencimiento = DateEntry(frame, width=20, background='lightblue', foreground='black',
                                           date_pattern='yyyy-mm-dd')
        self.fecha_vencimiento.pack(pady=5)

        tk.Label(frame, text="URL del trámite oficial:", bg="white").pack(anchor="w")
        self.entry_url = tk.Entry(frame, width=30)
        self.entry_url.pack(pady=5)

        tk.Button(frame, text="Elegir archivo", bg="#d9f2f9", width=20, command=self.seleccionar_archivo).pack(pady=10)

        self.label_archivo = tk.Label(frame, text="", bg="white", wraplength=180)
        self.label_archivo.pack()

    def seleccionar_archivo(self):
        ruta = filedialog.askopenfilename(title="Seleccionar documento",
                                          filetypes=[("Archivos PDF", "*.pdf"), ("Todos los archivos", "*.*")])
        if ruta:
            self.ruta_original = ruta
            self.label_archivo.config(text=os.path.basename(ruta))
            if ruta.lower().endswith(".pdf"):
                self.mostrar_pdf_en_scroll(ruta)

    def mostrar_pdf_en_scroll(self, ruta_pdf):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.pdf_imgs.clear()

        try:
            doc = fitz.open(ruta_pdf)
            for i in range(min(5, len(doc))):
                pagina = doc.load_page(i)
                pix = pagina.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
                temp_img_path = os.path.join(tempfile.gettempdir(), f"pagina_{i}.png")
                pix.save(temp_img_path)

                img = Image.open(temp_img_path).resize((580, 750))
                img_tk = ImageTk.PhotoImage(img)
                self.pdf_imgs.append(img_tk)
                tk.Label(self.scroll_frame, image=img_tk, bg="white").pack(pady=5)
        except Exception as e:
            messagebox.showerror("Vista previa fallida", str(e))

    def ver_documento(self):
        ruta_archivo = getattr(self, 'ruta_original', None)
        if ruta_archivo and os.path.exists(ruta_archivo):
            try:
                os.startfile(ruta_archivo)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{e}")
        else:
            messagebox.showwarning("Sin archivo", "Primero selecciona un archivo para visualizar.")

    def guardar_documento(self):
        nombre = self.entry_nombre.get()
        fecha = self.fecha_vencimiento.get_date()
        url = self.entry_url.get()
        ruta_archivo = getattr(self, 'ruta_original', None)

        if not nombre or not fecha or not url or not ruta_archivo:
            messagebox.showwarning("Faltan datos", "Por favor completa todos los campos.")
            return

        carpeta_destino = os.path.join("documentos_subidos")
        os.makedirs(carpeta_destino, exist_ok=True)
        nombre_archivo = os.path.basename(ruta_archivo)
        nueva_ruta = os.path.join(carpeta_destino, nombre_archivo)

        try:
            shutil.copy(ruta_archivo, nueva_ruta)
            encriptar_archivo(nueva_ruta)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo copiar o cifrar el archivo: {e}")
            return

        conn = sqlite3.connect("gestion_documentos.db")
        cursor = conn.cursor()

        cursor.execute("INSERT INTO Enlaces_Oficiales (nombre_tramite, url) VALUES (?, ?)", (nombre, url))
        id_enlace = cursor.lastrowid

        cursor.execute("""
            INSERT INTO Documentos (id_usuario, id_enlace, nombre_documento, ruta_archivo, fecha_vencimiento)
            VALUES (?, ?, ?, ?, ?)
        """, (self.id_usuario_actual, id_enlace, nombre, nueva_ruta, fecha))

        conn.commit()
        conn.close()
        messagebox.showinfo("Éxito", "Documento guardado y cifrado correctamente.")
