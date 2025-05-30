import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
import sys
import re
from datetime import datetime
from db.conexion import conectar

class ChatbotBasico(tk.Frame):
    def __init__(self, master, id_usuario_actual):
        super().__init__(master, bg="white")
        self.master = master
        self.id_usuario_actual = id_usuario_actual
        self.pack(fill="both", expand=True)

        self.configurar_gui()

        self.historico.insert(tk.END, "🤖 IA: Hola, ¿en qué puedo ayudarte?\n\n")

    def configurar_gui(self):
        tk.Label(self, text="Asistente Documental", font=("Helvetica", 14, "bold"), bg="#bdf8f8").pack(fill="x")

        self.historico = scrolledtext.ScrolledText(self, wrap="word", height=20, bg="white", font=("Arial", 10))
        self.historico.pack(padx=10, pady=10, fill="both", expand=True)

        self.entrada = tk.Entry(self, font=("Arial", 10))
        self.entrada.pack(padx=10, pady=5, fill="x")
        self.entrada.bind("<Return>", self.enviar)

        frame_botones = tk.Frame(self, bg="white")
        frame_botones.pack(fill="x", pady=(5, 10), padx=10)

        tk.Button(frame_botones, text="Enviar", bg="#abe3f9", font=("Arial", 10, "bold"),
                  command=self.enviar).pack(side="left")

        tk.Button(frame_botones, text="← Volver al menú principal", bg="white", font=("Arial", 10, "bold"),
                  command=self.volver_menu, cursor="hand2").pack(side="right")

    def enviar(self, event=None):
        pregunta = self.entrada.get().strip()
        if not pregunta:
            return

        self.historico.insert(tk.END, f"👤 Tú: {pregunta}\n\n")
        self.entrada.delete(0, tk.END)

        sql = self.detectar_pregunta(pregunta)

        if sql:
            self.ejecutar_sql(sql)
        else:
            self.historico.insert(tk.END, "🤖 IA: Lo siento, no entiendo tu pregunta.\n\n")

    def detectar_pregunta(self, pregunta):
        pregunta = pregunta.lower()

        if "documentos" in pregunta and "he subido" in pregunta:
            return f"SELECT * FROM Documentos WHERE id_usuario = {self.id_usuario_actual};"

        if "vencen hoy" in pregunta:
            return f"SELECT * FROM Documentos WHERE fecha_vencimiento = DATE('now') AND id_usuario = {self.id_usuario_actual};"

        if "vencidos" in pregunta:
            return f"SELECT * FROM Documentos WHERE fecha_vencimiento < DATE('now') AND id_usuario = {self.id_usuario_actual};"

        if "vencen" in pregunta and "semana" in pregunta:
            return f"SELECT * FROM Documentos WHERE fecha_vencimiento BETWEEN DATE('now') AND DATE('now', '+7 day') AND id_usuario = {self.id_usuario_actual};"

        fecha_match = re.search(r"\d{4}-\d{2}-\d{2}", pregunta)
        if "subí" in pregunta and fecha_match:
            fecha = fecha_match.group(0)
            return f"SELECT * FROM Documentos WHERE fecha_subida LIKE '{fecha}%' AND id_usuario = {self.id_usuario_actual};"

        if "vencen" in pregunta and "días" in pregunta:
            return f"SELECT * FROM Documentos WHERE fecha_vencimiento BETWEEN DATE('now') AND DATE('now', '+5 day') AND id_usuario = {self.id_usuario_actual};"

        return None

    def ejecutar_sql(self, sql):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute(sql)
            resultados = cursor.fetchall()
            conn.close()

            if resultados:
                self.historico.insert(tk.END, "🤖 IA: Documentos encontrados:\n\n")
                for fila in resultados:
                    try:
                        nombre = fila[3]
                        ruta = fila[4]
                        subida = fila[5]
                        vencimiento = fila[6]
                        self.historico.insert(
                            tk.END,
                            f"📄 {nombre}\n📁 Ruta: {ruta}\n📅 Subido: {subida} | Vence: {vencimiento}\n\n"
                        )
                    except IndexError:
                        self.historico.insert(tk.END, f"🔸 Resultado parcial: {fila}\n")
            else:
                self.historico.insert(tk.END, "🤖 IA: No se encontraron documentos.\n\n")
        except Exception as e:
            self.historico.insert(tk.END, f"❌ Error ejecutando SQL:\n{e}\n\n")

    def volver_menu(self):
        from interfaces.menu_principal import MenuPrincipal
        self.master.mostrar_pantalla(MenuPrincipal, id_usuario_actual=self.id_usuario_actual)
