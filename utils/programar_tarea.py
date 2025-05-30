import os
import sys
import subprocess

def programar_tarea_verificacion():
    nombre_tarea = "VerificarVencimientosDocumentos"

    # Verifica si la tarea ya existe
    resultado = subprocess.run(
        f'schtasks /Query /TN "{nombre_tarea}"',
        shell=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    if resultado.returncode == 0:
        return  # Ya existe la tarea programada

    # Usa el mismo ejecutable que esté corriendo el programa
    ruta_python = sys.executable

    # Ruta al script de verificación
    ruta_script = os.path.abspath(os.path.join("utils", "verificar_vencimiento.py"))

    # Comando para crear la tarea programada
    comando = (
        f'schtasks /Create /SC DAILY /TN "{nombre_tarea}" '
        f'/TR "\\"{ruta_python}\\" \\"{ruta_script}\\"" /ST 23:24 /F'
    )

    try:
        subprocess.run(comando, shell=True, check=True)
        print("✅ Tarea programada con éxito.")
    except Exception as e:
        print(f"❌ No se pudo programar la tarea: {e}")
