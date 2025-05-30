import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import os
import fitz
import time
import sys
from db.conexion import conectar
from utils.crypto_utils import desencriptar_archivo

class VerDocumentos(tk.Frame):
    def __init__(self, master, id_usuario_actual, filtro=None, pantalla_anterior=None):
        super().__init__(master, bg="white")
        self.master = master
        self.master.geometry("900x550")
        self.pack(fill="both", expand=True)
        self.id_usuario_actual = id_usuario_actual
        self.filtro = filtro
        self.pantalla_anterior = pantalla_anterior
        self.entrada_busqueda = None
        self.resultado_documentos = []
        self.contenedores_documentos = {}

        self.titulo_superior()
        self.mostrar_documentos()

    def titulo_superior(self):
        tk.Label(self, text="Control de Caducidad de Documentos Oficiales",
                 font=("Helvetica", 10, "bold"), bg="white", fg="gray").place(x=10, y=5)
        tk.Label(self, text="Documentos Cargados",
                 font=("Helvetica", 16, "bold"), bg="white", fg="black").place(x=10, y=25)

        tk.Button(self, text="← Salir", font=("Arial", 10), bg="white", fg="black", bd=0,
                  cursor="hand2", command=self.volver_menu, activebackground="white").place(x=800, y=15)

        self.entrada_busqueda = tk.Entry(self, width=30, font=("Arial", 10))
        self.entrada_busqueda.place(x=300, y=25)
        tk.Button(self, text="🔍", font=("Arial", 10), bg="white", bd=0, cursor="hand2",
                  command=self.mostrar_documentos).place(x=540, y=23)

        canvas = tk.Canvas(self, width=900, height=2, bg="white", highlightthickness=0)
        canvas.place(x=0, y=60)
        canvas.create_line(0, 1, 900, 1, fill="black", width=2)

    def mostrar_documentos(self):
        if hasattr(self, 'frame_docs'):
            self.frame_docs.destroy()

        self.frame_docs = tk.Frame(self, bg="white")
        self.frame_docs.place(x=50, y=80)
        self.imagenes_cache = []
        self.contenedores_documentos = {}

        loading = tk.Label(self.frame_docs, text="⏳ Cargando documentos...", font=("Arial", 12), bg="white", fg="gray")
        loading.pack(pady=20)
        self.update_idletasks()

        conn = conectar()
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

        self.documentos_validos = [(id_doc, nombre, ruta, url)
                                   for id_doc, nombre, ruta, url in documentos
                                   if ruta and os.path.exists(ruta)]

        texto_busqueda = self.entrada_busqueda.get().strip().lower()
        if texto_busqueda:
            self.documentos_validos = [doc for doc in self.documentos_validos if texto_busqueda in doc[1].lower()]

        loading.destroy()
        self.indice_actual = 0
        self.cargar_documento_con_delay()

    def cargar_documento_con_delay(self):
        if self.indice_actual >= len(self.documentos_validos):
            return

        id_doc, nombre, ruta, url = self.documentos_validos[self.indice_actual]
        contenedor = tk.Frame(self.frame_docs, bg="white", bd=1, relief="solid")
        contenedor.grid(row=self.indice_actual // 4, column=self.indice_actual % 4, padx=15, pady=15)
        self.contenedores_documentos[id_doc] = contenedor

        ruta_temporal = desencriptar_archivo(ruta)
        if ruta_temporal and os.path.exists(ruta_temporal):
            imagen = self.generar_miniatura(ruta_temporal)
        else:
            imagen = Image.new("RGB", (120, 120), color="gray")

        img_tk = ImageTk.PhotoImage(imagen)
        self.imagenes_cache.append(img_tk)

        tk.Button(contenedor, image=img_tk, bg="white", bd=0,
                  command=lambda d=id_doc: self.ver_enlaces_doc(d)).pack()

        tk.Label(contenedor, text=nombre, bg="white", wraplength=120, justify="center").pack(pady=2)

        tk.Button(contenedor, text="🗑 Eliminar", font=("Arial", 8), bg="#ffcccc", bd=0,
                  command=lambda d=id_doc: self.eliminar_documento(d)).pack(pady=3)

        self.indice_actual += 1
        self.after(100, self.cargar_documento_con_delay)

    def generar_miniatura(self, ruta):
        try:
            if not ruta or not os.path.exists(ruta):
                raise FileNotFoundError("No se encontró el archivo desencriptado")

            with fitz.open(ruta) as doc:
                pagina = doc.load_page(0)
                pix = pagina.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
                nombre_base = os.path.basename(ruta).replace(" ", "_")
                img_path = os.path.join("temp", f"{nombre_base}.png")
                os.makedirs("temp", exist_ok=True)
                pix.save(img_path)

            return Image.open(img_path).resize((120, 120))
        except Exception as e:
            print(f"⚠️ Error generando miniatura para {ruta}: {e}")
            return Image.new("RGB", (120, 120), color="gray")

    def eliminar_documento(self, id_documento):
        if not messagebox.askyesno("Confirmar eliminación", "¿Estás seguro de eliminar este documento?"):
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT ruta_archivo FROM Documentos WHERE id_documento = ?", (id_documento,))
        fila = cursor.fetchone()

        if not fila:
            conn.close()
            messagebox.showerror("Error", "No se encontró el documento.")
            return

        ruta_archivo = fila[0]
        cursor.execute("SELECT COUNT(*) FROM Documentos WHERE ruta_archivo = ?", (ruta_archivo,))
        cantidad_usos = cursor.fetchone()[0]

        cursor.execute("DELETE FROM Documentos WHERE id_documento = ?", (id_documento,))
        conn.commit()
        conn.close()

        if cantidad_usos <= 1 and os.path.exists(ruta_archivo):
            try:
                os.remove(ruta_archivo)
            except Exception as e:
                print(f"⚠️ No se pudo borrar archivo: {e}")

        if id_documento in self.contenedores_documentos:
            self.contenedores_documentos[id_documento].destroy()
            del self.contenedores_documentos[id_documento]

        messagebox.showinfo("Eliminado", "Documento eliminado correctamente.")

    def ver_enlaces_doc(self, id_documento):
        from interfaces.ver_enlaces import VerEnlaces
        self.master.mostrar_pantalla(
            VerEnlaces,
            id_documento=id_documento,
            id_usuario_actual=self.id_usuario_actual,
            pantalla_anterior=self.__class__,
            filtro=self.filtro
        )

    def volver_menu(self):
        if self.pantalla_anterior:
            self.master.mostrar_pantalla(
                self.pantalla_anterior,
                id_usuario_actual=self.id_usuario_actual,
                filtro=self.filtro
            )
        else:
            from interfaces.menu_principal import MenuPrincipal
            self.master.mostrar_pantalla(MenuPrincipal, id_usuario_actual=self.id_usuario_actual)
