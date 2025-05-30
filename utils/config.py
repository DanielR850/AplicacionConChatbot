import os

# ✅ Ruta absoluta a la base de datos
from utils.rutas import obtener_ruta_db
DB_PATH = obtener_ruta_db()

# ✅ Credenciales de correo para notificaciones
EMAIL_ORIGEN = "notificadordocumentos@gmail.com"
EMAIL_PASSWORD = "rjhynmcrkfauvkyl"  # contraseña de aplicación generada con 2FA

# ✅ Configuración general
NOTIFICACION_DIAS_DEFAULT = 3  # si no se especifica, cuántos días antes notificar

# ✅ Asunto/cuerpo por defecto (puedes sobreescribir desde quien lo llame)
ASUNTO_VENCE_HOY = "📢 El documento '{nombre}' vence HOY"
CUERPO_VENCE_HOY = """Hola,

Este es un recordatorio de que el documento:
'{nombre}' vence HOY ({fecha}).

Sistema de Documentos"""

ASUNTO_POR_VENCER = "⏰ El documento '{nombre}' vencerá en {dias} día(s)"
CUERPO_POR_VENCER = """Hola,

Este es un aviso anticipado de que el documento:
'{nombre}' vencerá el {fecha} (en {dias} días).

Sistema de Documentos"""
