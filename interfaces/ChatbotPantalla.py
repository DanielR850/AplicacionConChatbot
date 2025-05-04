import os
import tkinter as tk
from tkinter import messagebox, scrolledtext
import sqlite3
from llama_cpp import Llama

# Ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "tinyllama-1.1b-chat-v1.0.Q8_0.gguf")
DB_PATH = os.path.join(BASE_DIR, "gestion_documentos.db")

class ChatbotPantalla(tk.Frame):
    def __init__(self, master, id_usuario_actual=None):
        super().__init__(master, bg="white")
        self.master = master
        self.id_usuario_actual = id_usuario_actual
        self.pack(fill="both", expand=True)

        self.llm = Llama(
            model_path=MODEL_PATH,
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )

        self.configurar_gui()
        self.historico.insert(tk.END, "🤖 IA: Hola, ¿en qué puedo ayudarte?\n\n")

    def configurar_gui(self):
        tk.Label(self, text="Asistente SQL", font=("Helvetica", 14, "bold"), bg="#bdf8f8").pack(fill="x")

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

        sql = self.generar_sql_con_modelo(pregunta)

        if sql.lower().startswith("select"):
            self.ejecutar_sql(sql)
        else:
            self.historico.insert(tk.END, f"🤖 IA: No se pudo procesar la solicitud.\n\n")


    def generar_sql_con_modelo(self, pregunta):
        prompt = f"""
Eres un generador experto de consultas SQL para SQLite.

Aquí está la estructura de la base de datos:

Tabla: Usuarios
- id_usuario (INTEGER, PK)
- nombre_usuario (TEXT)
- correo (TEXT)
- contraseña (TEXT)

Tabla: Enlaces_Oficiales
- id_enlace (INTEGER, PK)
- nombre_tramite (TEXT)
- url (TEXT)

Tabla: Documentos
- id_documento (INTEGER, PK)
- id_usuario (INTEGER, FK a Usuarios)
- id_enlace (INTEGER, FK a Enlaces_Oficiales)
- nombre_documento (TEXT)
- ruta_archivo (TEXT)
- fecha_subida (TIMESTAMP)
- fecha_vencimiento (DATE)

Reglas importantes:
- Siempre incluye: WHERE id_usuario = {self.id_usuario_actual} si se habla del usuario actual.
- Nunca uses id_enlace para condiciones relacionadas con fechas, vencimientos o archivos.
- Nunca inventes condiciones si no están claramente mencionadas.
- Usa funciones como DATE('now'), DATE('now', '-2 day') o BETWEEN para fechas.
- No uses INTERVAL (no es compatible con SQLite).
- Devuelve solo UNA consulta SQL válida, en UNA sola línea, sin explicaciones ni comentarios.

Ejemplos:

Pregunta: ¿Qué documentos he subido?
Respuesta: SELECT * FROM Documentos WHERE id_usuario = {self.id_usuario_actual};

Pregunta: ¿Cuáles son mis documentos?
Respuesta: SELECT * FROM Documentos WHERE id_usuario = {self.id_usuario_actual};

Pregunta: Dame todos mis documentos registrados
Respuesta: SELECT * FROM Documentos WHERE id_usuario = {self.id_usuario_actual};

Pregunta: ¿Qué documentos vencen hoy?
Respuesta: SELECT * FROM Documentos WHERE fecha_vencimiento = DATE('now') AND id_usuario = {self.id_usuario_actual};

Pregunta: ¿Qué documentos vencen esta semana?
Respuesta: SELECT * FROM Documentos WHERE fecha_vencimiento BETWEEN DATE('now') AND DATE('now', '+7 days') AND id_usuario = {self.id_usuario_actual};

Pregunta: ¿Qué documentos subí el 3 de mayo de 2025?
Respuesta: SELECT * FROM Documentos WHERE fecha_subida LIKE '2025-05-03%' AND id_usuario = {self.id_usuario_actual};

Pregunta: ¿Qué documentos subí hace dos días?
Respuesta: SELECT * FROM Documentos WHERE fecha_subida >= DATE('now', '-2 day') AND fecha_subida < DATE('now', '-1 day') AND id_usuario = {self.id_usuario_actual};

Pregunta: ¿Hay un documento llamado 'acta de nacimiento'?
Respuesta: SELECT * FROM Documentos WHERE nombre_documento = 'acta de nacimiento' AND id_usuario = {self.id_usuario_actual};

Pregunta: {pregunta}
Respuesta:
""".strip()



        try:
            salida = self.llm(prompt=prompt, max_tokens=200)
            respuesta = salida["choices"][0]["text"].strip()

            # Registrar respuesta completa para depuración
            with open(os.path.join(BASE_DIR, "debug_llm_output.txt"), "a", encoding="utf-8") as f:
                f.write(f"\n[PREGUNTA] {pregunta}\n[RESPUESTA RAW]\n{respuesta}\n")

            if not respuesta:
                return "-- Error: El modelo no generó una respuesta."

            lineas = [l.strip() for l in respuesta.splitlines() if l.strip()]
            primera_linea = next((l for l in lineas if "select" in l.lower()), None)

            if not primera_linea or (";" in primera_linea and not primera_linea.strip().endswith(";")):
                return "-- Error: Consulta SQL incompleta o inválida."

            return primera_linea.replace(";", "").strip() + ";"
        except Exception as e:
            return f"-- Error generando SQL: {e}"

    def ejecutar_sql(self, sql):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(sql)
            resultados = cursor.fetchall()

            if resultados:
                self.historico.insert(tk.END, "🤖 IA: Estos son los documentos encontrados:\n")
                for fila in resultados:
                    try:
                        nombre = fila[3]
                        ruta = fila[4]
                        fecha_subida = fila[5]
                        fecha_vencimiento = fila[6]
                        self.historico.insert(
                            tk.END,
                            f"📄 {nombre}\n📁 Ruta: {ruta}\n📅 Subido: {fecha_subida} | Vence: {fecha_vencimiento}\n\n"
                        )
                    except IndexError:
                        self.historico.insert(tk.END, f"🔸 {fila}\n")
            else:
                self.historico.insert(tk.END, "🤖 IA: No se encontraron resultados.\n\n")

            conn.close()
        except Exception as e:
            self.historico.insert(tk.END, f"🤖 IA: Ocurrió un error al ejecutar la consulta.\n\n")


    def volver_menu(self):
        from interfaces.menu_principal import MenuPrincipal
        self.master.mostrar_pantalla(MenuPrincipal, id_usuario_actual=self.id_usuario_actual)
