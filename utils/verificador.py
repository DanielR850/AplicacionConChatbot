import sqlite3
import smtplib
from email.message import EmailMessage
from datetime import datetime
from utils.config import (
    EMAIL_ORIGEN, EMAIL_PASSWORD,
    ASUNTO_VENCE_HOY, CUERPO_VENCE_HOY,
    ASUNTO_POR_VENCER, CUERPO_POR_VENCER
)
from db.conexion import conectar  # ✅ conexión centralizada

def enviar_correo(destinatario, asunto, cuerpo):
    msg = EmailMessage()
    msg["Subject"] = asunto
    msg["From"] = EMAIL_ORIGEN
    msg["To"] = destinatario
    msg.set_content(cuerpo)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ORIGEN, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"✅ Correo enviado a {destinatario}")
    except Exception as e:
        print(f"❌ Error al enviar correo a {destinatario}: {e}")

def verificar_vencimientos():
    try:
        conn = conectar()
        cursor = conn.cursor()
        hoy = datetime.now().date()

        cursor.execute("""
            SELECT nombre_documento, fecha_vencimiento, dias_aviso, correo_aviso
            FROM Documentos
            WHERE correo_aviso IS NOT NULL AND fecha_vencimiento IS NOT NULL
        """)

        documentos = cursor.fetchall()

        for nombre, fecha_venc, dias_aviso, correo in documentos:
            try:
                if not correo or not correo.strip():
                    continue

                fecha_venc = datetime.strptime(fecha_venc, "%Y-%m-%d").date()
                dias_restantes = (fecha_venc - hoy).days

                try:
                    dias_aviso = int(dias_aviso)
                except (TypeError, ValueError):
                    dias_aviso = None

                if dias_restantes == 0:
                    asunto = ASUNTO_VENCE_HOY.format(nombre=nombre)
                    cuerpo = CUERPO_VENCE_HOY.format(nombre=nombre, fecha=fecha_venc)
                    enviar_correo(correo, asunto, cuerpo)

                elif dias_aviso is not None and 0 < dias_restantes <= dias_aviso:
                    asunto = ASUNTO_POR_VENCER.format(nombre=nombre, dias=dias_restantes)
                    cuerpo = CUERPO_POR_VENCER.format(nombre=nombre, fecha=fecha_venc, dias=dias_restantes)
                    enviar_correo(correo, asunto, cuerpo)

            except Exception as e:
                print(f"⚠️ Error procesando '{nombre}': {e}")

    except Exception as db_error:
        print(f"❌ Error verificando vencimientos: {db_error}")
    finally:
        try:
            conn.close()
        except:
            pass
