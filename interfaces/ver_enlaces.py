import tkinter as tk
from tkinter import messagebox, Scrollbar, Canvas, Frame
from tkcalendar import DateEntry
import sqlite3
import os
import webbrowser
from PIL import Image, ImageTk
import fitz
from utils.crypto_utils import desencriptar_archivo
from db.conexion import conectar
import sys

class VerEnlaces(tk.Frame):
    def __init__(self, master, id_documento=None, id_usuario_actual=None, pantalla_anterior=None, filtro=None):
        super().__init__(master, bg="white")
        self.master = master
        self.id_documento = id_documento
        self.id_usuario_actual = id_usuario_actual
        self.pantalla_anterior = pantalla_anterior
        self.filtro = filtro
        self.doc_data = {}

        self.pack(fill="both", expand=True)
        self.master.geometry("900x500")

        self.encabezado()
        self.cargar_datos_documento()
        self.mostrar_enlace_y_edicion()
        self.vista_previa_documento_scroll()

    def encabezado(self):
        tk.Label(self, text="Enlace Documentos Oficiales", font=("Helvetica", 14, "bold"),
                 bg="#bdf8f8", fg="black").place(x=0, y=0, width=900, height=40)

        canvas_top = tk.Canvas(self, width=900, height=2, bg="white", highlightthickness=0)
        canvas_top.place(x=0, y=40)
        canvas_top.create_line(0, 1, 900, 1, fill="black", width=2)

        tk.Button(self, text="← REGRESAR", font=("Arial", 10), bg="#bdf8f8", fg="black", bd=0,
                  activebackground="#bdf8f8", activeforeground="black",
                  command=self.volver_menu).place(x=800, y=5)

    def cargar_datos_documento(self):
        if not self.id_documento:
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT d.nombre_documento, d.fecha_vencimiento, e.url, d.id_enlace,
                   d.ruta_archivo, d.correo_aviso, d.dias_aviso
            FROM Documentos d
            JOIN Enlaces_Oficiales e ON d.id_enlace = e.id_enlace
            WHERE d.id_documento = ?
        """, (self.id_documento,))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            self.doc_data["nombre"] = resultado[0]
            self.doc_data["fecha_vencimiento"] = resultado[1]
            self.doc_data["url"] = resultado[2]
            self.doc_data["id_enlace"] = resultado[3]
            self.doc_data["ruta"] = resultado[4]
            self.doc_data["correo_aviso"] = resultado[5] or ""
            self.doc_data["dias_aviso"] = resultado[6] if resultado[6] is not None else ""

    def mostrar_enlace_y_edicion(self):
        if not self.doc_data:
            tk.Label(self, text="No se encontraron datos del documento.",
                     font=("Arial", 12), bg="white", fg="red").place(x=100, y=100)
            return

        form = tk.Frame(self, bg="white")
        form.place(x=30, y=80)

        tk.Label(form, text="Nombre del documento:", bg="white").pack(anchor="w")
        self.entry_nombre = tk.Entry(form, width=40)
        self.entry_nombre.insert(0, self.doc_data["nombre"])
        self.entry_nombre.pack(pady=5)

        tk.Label(form, text="Fecha de vencimiento:", bg="white").pack(anchor="w")
        self.entry_fecha = DateEntry(form, width=20, date_pattern="yyyy-mm-dd")
        self.entry_fecha.set_date(self.doc_data["fecha_vencimiento"])
        self.entry_fecha.pack(pady=5)

        tk.Label(form, text="URL del trámite oficial:", bg="white").pack(anchor="w")
        self.entry_url = tk.Entry(form, width=50)
        self.entry_url.insert(0, self.doc_data["url"])
        self.entry_url.pack(pady=5)

        tk.Label(form, text="Correo de notificación:", bg="white").pack(anchor="w")
        self.entry_correo = tk.Entry(form, width=40)
        self.entry_correo.insert(0, self.doc_data["correo_aviso"])
        self.entry_correo.pack(pady=5)

        tk.Label(form, text="Días antes para avisar:", bg="white").pack(anchor="w")
        self.entry_dias = tk.Entry(form, width=10)
        self.entry_dias.insert(0, str(self.doc_data["dias_aviso"]))
        self.entry_dias.pack(pady=5)

        tk.Button(form, text="🔗 Abrir enlace", bg="#d9f2f9", font=("Arial", 9),
                  command=lambda: self.abrir_url(self.doc_data["url"])).pack(pady=10)

        tk.Button(form, text="💾 Guardar cambios", bg="#abe3f9", font=("Arial", 10, "bold"),
                  command=self.guardar_cambios).pack(pady=5)

    def vista_previa_documento_scroll(self):
        ruta = self.doc_data.get("ruta")
        if not ruta or not os.path.exists(ruta):
            tk.Label(self, text="No se puede cargar vista previa del documento.",
                     font=("Arial", 10), bg="white", fg="gray").place(x=400, y=100)
            return

        try:
            ruta_desencriptada = desencriptar_archivo(ruta)
            if not ruta_desencriptada or not os.path.exists(ruta_desencriptada):
                raise Exception("No se pudo desencriptar el archivo")

            frame_scroll = Frame(self, bg="white")
            frame_scroll.place(x=370, y=80, width=470, height=360)

            canvas = Canvas(frame_scroll, bg="white")
            scrollbar = Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
            canvas.configure(yscrollcommand=scrollbar.set)

            sub_frame = Frame(canvas, bg="white")
            canvas.create_window((0, 0), window=sub_frame, anchor="nw")

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            doc = fitz.open(ruta_desencriptada)
            for i in range(min(5, len(doc))):
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=fitz.Matrix(0.6, 0.6))
                img_path = os.path.join("temp", f"preview_{self.id_documento}_{i}.png")
                os.makedirs("temp", exist_ok=True)
                pix.save(img_path)

                img = Image.open(img_path)
                img_tk = ImageTk.PhotoImage(img)
                label = tk.Label(sub_frame, image=img_tk, bg="white")
                label.image = img_tk
                label.pack(pady=5)

            sub_frame.update_idletasks()
            canvas.config(scrollregion=canvas.bbox("all"))

        except Exception as e:
            print(f"❌ Error vista previa: {e}")
            tk.Label(self, text="Error al generar vista previa", fg="red", bg="white").place(x=400, y=100)

    def guardar_cambios(self):
        nuevo_nombre = self.entry_nombre.get().strip()
        nueva_fecha = self.entry_fecha.get_date()
        nueva_url = self.entry_url.get().strip()
        nuevo_correo = self.entry_correo.get().strip()
        nuevo_dias = self.entry_dias.get().strip()

        if not nuevo_nombre or not nueva_fecha or not nueva_url or not nuevo_correo:
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos.")
            return

        if nuevo_dias:
            if not nuevo_dias.isdigit():
                messagebox.showerror("Error", "El campo 'días de aviso' debe ser numérico.")
                return
            nuevo_dias = int(nuevo_dias)
        else:
            nuevo_dias = None

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("UPDATE Enlaces_Oficiales SET url = ? WHERE id_enlace = ?",
                           (nueva_url, self.doc_data["id_enlace"]))

            cursor.execute("""
                UPDATE Documentos
                SET nombre_documento = ?, fecha_vencimiento = ?, correo_aviso = ?, dias_aviso = ?
                WHERE id_documento = ?
            """, (nuevo_nombre, nueva_fecha, nuevo_correo, nuevo_dias, self.id_documento))

            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Datos actualizados correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def abrir_url(self, url):
        try:
            webbrowser.open_new_tab(url)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el enlace:\n{e}")

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
