import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
import sqlite3
import datetime

class Calendario(tk.Frame):
    def __init__(self, master, id_usuario_actual=None):
        super().__init__(master, bg="white")
        self.master = master
        self.master.geometry("900x500")
        self.pack(fill="both", expand=True)

        self.id_usuario_actual = id_usuario_actual

        self.dibujar_encabezado()
        self.dibujar_calendario()
        self.cargar_documentos()

    def dibujar_encabezado(self):
        tk.Label(self, text="Documentos vencidos", font=("Helvetica", 12, "bold"),
                 bg="#bdf8f8", fg="black").place(x=0, y=0, width=220, height=40)

        tk.Label(self, text="Calendario", font=("Helvetica", 16, "bold"),
                 bg="white", fg="black").place(x=250, y=5)

        tk.Button(self, text="← SALIR", font=("Arial", 10), bg="white", bd=0,
                  command=self.volver_menu).place(x=800, y=15)

        canvas_top = tk.Canvas(self, width=900, height=2, bg="white", highlightthickness=0)
        canvas_top.place(x=0, y=40)
        canvas_top.create_line(0, 1, 900, 1, fill="black", width=2)

        canvas_div = tk.Canvas(self, width=2, height=460, bg="white", highlightthickness=0)
        canvas_div.place(x=220, y=40)
        canvas_div.create_line(1, 0, 1, 460, fill="black", width=1)

    def dibujar_calendario(self):
        self.calendario = Calendar(
            self,
            selectmode="day",
            date_pattern="yyyy-mm-dd",
            font=("Arial", 16),
            headersbackground="#bdf8f8",
            normalbackground="white",
            weekendbackground="#f2f2f2",
            selectbackground="#abe3f9",
            disabledbackground="gray90",
            borderwidth=2,
            rowheight=40,
            background="white",
            foreground="black"
        )
        self.calendario.place(x=250, y=70, width=600, height=350)
        self.calendario.bind("<<CalendarSelected>>", self.fecha_seleccionada)

    def cargar_documentos(self):
        conn = sqlite3.connect("gestion_documentos.db")
        cursor = conn.cursor()

        hoy = datetime.date.today()
        proxima_semana = hoy + datetime.timedelta(days=7)

        cursor.execute("""
            SELECT nombre_documento, fecha_vencimiento
            FROM Documentos
            WHERE id_usuario = ?
            ORDER BY fecha_vencimiento ASC
        """, (self.id_usuario_actual,))
        documentos = cursor.fetchall()
        conn.close()

        y_actual = 60
        for nombre, fecha_str in documentos:
            try:
                fecha = datetime.datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except:
                continue

            # Mostrar en el panel izquierdo solo los vencidos
            if fecha < hoy:
                texto = f"{nombre}\n{fecha_str}"
                tk.Label(self, text=texto, bg="#f5c6cb", wraplength=180,
                         font=("Arial", 9), justify="center").place(x=20, y=y_actual, width=180, height=50)
                y_actual += 60
                self.calendario.calevent_create(fecha, "Vencido", "vencido")

            elif hoy <= fecha <= proxima_semana:
                self.calendario.calevent_create(fecha, "Próximo", "proximo")

        self.calendario.tag_config("proximo", background="red", foreground="white")
        self.calendario.tag_config("vencido", background="gray", foreground="white")

    def fecha_seleccionada(self, event):
        fecha = self.calendario.get_date()
        messagebox.showinfo("Fecha seleccionada", f"Seleccionaste: {fecha}")

    def volver_menu(self):
        from interfaces.menu_principal import MenuPrincipal
        self.master.mostrar_pantalla(MenuPrincipal, id_usuario_actual=self.id_usuario_actual)
