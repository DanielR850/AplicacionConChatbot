import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys
from db.conexion import conectar

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class CrearUsuario(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.master = master
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Crear Cuenta Nueva", font=("Helvetica", 14, "bold"), bg="white").pack(pady=10)

        canvas_h = tk.Canvas(self, width=800, height=2, bg="white", highlightthickness=0)
        canvas_h.place(x=0, y=35)
        canvas_h.create_line(0, 1, 800, 1, fill="black", width=2)

        frame_form = tk.Frame(self, bg="white", width=280, height=250)
        frame_form.place(x=80, y=60)

        tk.Label(frame_form, text="Correo electrónico", font=("Arial", 10), bg="white").pack(pady=5)
        self.entry_correo = tk.Entry(frame_form, width=25)
        self.entry_correo.pack()

        tk.Label(frame_form, text="Contraseña", font=("Arial", 10), bg="white").pack(pady=5)
        self.entry_contra = tk.Entry(frame_form, width=25, show="*")
        self.entry_contra.pack()

        tk.Button(frame_form, text="Crear cuenta", bg="#abe3f9", font=("Arial", 10, "bold"),
                  width=17, command=self.crear_usuario).pack(pady=10)

        tk.Button(frame_form, text="← Volver", bg="white", font=("Arial", 10, "bold"),
                  width=17, command=self.volver_login).pack()

        canvas = tk.Canvas(self, width=2, height=800, bg="white", highlightthickness=0)
        canvas.place(x=300, y=35)
        canvas.create_line(1, 0, 1, 800, fill="black", width=1)

        frame_img = tk.Frame(self, bg="white")
        frame_img.place(relx=0.55, rely=0.2)

        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")

        ruta_imagen = os.path.join(base_path, "assets", "iccons", "image.png")

        if os.path.exists(ruta_imagen):
            imagen = Image.open(ruta_imagen)
            imagen = imagen.resize((150, 150))
            self.img_tk = ImageTk.PhotoImage(imagen)
            tk.Label(frame_img, image=self.img_tk, bg="white").pack(pady=5)

        tk.Label(frame_img, text="Organiza tus Documentos\nPersonales", font=("Arial", 10, "italic"), bg="white").pack()

        canvas_h = tk.Canvas(self, width=800, height=2, bg="white", highlightthickness=0)
        canvas_h.place(x=0, y=300)
        canvas_h.create_line(0, 1, 800, 1, fill="black", width=2)

    def crear_usuario(self):
        correo = self.entry_correo.get().strip()
        contra = self.entry_contra.get()

        if not correo or not contra:
            messagebox.showwarning("Campos vacíos", "Por favor completa todos los campos.")
            return

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Usuarios (correo, contraseña) VALUES (?, ?)", (correo, contra))
            conn.commit()
            conn.close()
            messagebox.showinfo("Éxito", "Cuenta creada correctamente.")
            self.volver_login()

        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Ese correo ya está registrado.")
        except Exception as e:
            messagebox.showerror("Error inesperado", f"Ocurrió un error:\n{e}")

    def volver_login(self):
        from interfaces.login import Login
        self.master.mostrar_pantalla(Login)
