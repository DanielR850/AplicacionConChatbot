import tkinter as tk
from tkinter import messagebox
import os
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.worksheet.table import Table as ExcelTable, TableStyleInfo
import sys

from db.conexion import conectar

class ExportarReportes(tk.Frame):
    def __init__(self, master, id_usuario_actual=None):
        super().__init__(master, bg="#f7fafd")
        self.master = master
        self.id_usuario_actual = id_usuario_actual
        self.pack(fill="both", expand=True)
        self.configurar_gui()

    def obtener_nombre_usuario(self):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT correo FROM Usuarios WHERE id_usuario = ?", (self.id_usuario_actual,))
            resultado = cursor.fetchone()
            conn.close()
            return resultado[0].replace(" ", "_") if resultado else f"usuario_{self.id_usuario_actual}"
        except:
            return f"usuario_{self.id_usuario_actual}"

    def configurar_gui(self):
        tk.Label(self, text="📋 Exportación de Reportes",
                 font=("Helvetica", 18, "bold"), bg="#f7fafd", fg="#333").pack(pady=(20, 5))

        tk.Label(self, text="Exporta tus documentos a PDF o Excel para guardarlos, imprimirlos o compartirlos.",
                 font=("Helvetica", 11), bg="#f7fafd", fg="#666").pack(pady=(0, 20))

        btn_pdf = tk.Button(self, text="Exportar como PDF", bg="#d1e7dd", fg="#000",
                            font=("Arial", 12, "bold"), width=25, height=2,
                            command=self.exportar_pdf, cursor="hand2")
        btn_pdf.pack(pady=10)

        btn_excel = tk.Button(self, text="Exportar como Excel", bg="#ffeeba", fg="#000",
                              font=("Arial", 12, "bold"), width=25, height=2,
                              command=self.exportar_excel, cursor="hand2")
        btn_excel.pack(pady=10)

        tk.Button(self, text="← Volver al menú", font=("Arial", 10, "bold"),
                  command=self.volver_menu, bg="white", fg="blue", relief="flat", cursor="hand2").pack(pady=(30, 10))

        self.lbl_estado = tk.Label(self, text="", font=("Arial", 10), bg="#f7fafd", fg="#007700")
        self.lbl_estado.pack()

    def obtener_documentos(self):
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT nombre_documento, fecha_subida, fecha_vencimiento
                FROM Documentos
                WHERE id_usuario = ?
            """, (self.id_usuario_actual,))
            resultados = cursor.fetchall()
            conn.close()
            return resultados
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron obtener los datos: {e}")
            return []

    def exportar_pdf(self):
        documentos = self.obtener_documentos()
        if not documentos:
            messagebox.showinfo("Sin datos", "No hay documentos para exportar.")
            return

        nombre_usuario = self.obtener_nombre_usuario()
        nombre_archivo = f"Reporte_Documentos_{nombre_usuario}.pdf"
        doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)

        styles = getSampleStyleSheet()
        elementos = []

        titulo = Paragraph(f"<b>📄 Reporte de Documentos de {nombre_usuario.replace('_', ' ')}</b>", styles["Title"])
        elementos.append(titulo)
        elementos.append(Spacer(1, 12))

        data = [["Nombre del Documento", "Fecha de Subida", "Fecha de Vencimiento", "Estado"]]
        for nombre, subida, vencimiento in documentos:
            estado = "VENCIDO" if vencimiento < subida else "VIGENTE"
            data.append([nombre, subida, vencimiento, estado])

        tabla = Table(data, colWidths=[150, 100, 120, 80])
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#007acc")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 11),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        elementos.append(tabla)
        doc.build(elementos)
        self.lbl_estado.config(text=f"✅ PDF generado: {nombre_archivo}")

    def exportar_excel(self):
        documentos = self.obtener_documentos()
        if not documentos:
            messagebox.showinfo("Sin datos", "No hay documentos para exportar.")
            return

        nombre_usuario = self.obtener_nombre_usuario()
        nombre_archivo = f"Reporte_Documentos_{nombre_usuario}.xlsx"

        wb = Workbook()
        ws = wb.active
        ws.title = "Documentos"

        encabezados = ["Nombre del Documento", "Fecha de Subida", "Fecha de Vencimiento", "Estado"]
        ws.append(encabezados)

        for nombre, subida, vencimiento in documentos:
            estado = "VENCIDO" if vencimiento < subida else "VIGENTE"
            ws.append([nombre, subida, vencimiento, estado])

        total_filas = len(documentos) + 1
        total_columnas = len(encabezados)
        rango_tabla = f"A1:{chr(64 + total_columnas)}{total_filas}"

        tabla = ExcelTable(displayName="TablaDocumentos", ref=rango_tabla)
        estilo_tabla = TableStyleInfo(
            name="TableStyleMedium9",
            showFirstColumn=False,
            showLastColumn=False,
            showRowStripes=True,
            showColumnStripes=False
        )
        tabla.tableStyleInfo = estilo_tabla
        ws.add_table(tabla)

        for column_cells in ws.columns:
            length = max(len(str(cell.value)) if cell.value else 0 for cell in column_cells)
            ws.column_dimensions[column_cells[0].column_letter].width = length + 5

        wb.save(nombre_archivo)
        self.lbl_estado.config(text=f"✅ Excel generado: {nombre_archivo}")

    def volver_menu(self):
        from interfaces.menu_principal import MenuPrincipal
        self.master.mostrar_pantalla(MenuPrincipal, id_usuario_actual=self.id_usuario_actual)
