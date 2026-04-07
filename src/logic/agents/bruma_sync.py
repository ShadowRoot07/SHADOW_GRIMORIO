import subprocess
import time
import json
import os
from pathlib import Path

# --- CONFIGURACIÓN DE RUTAS ---
def buscar_raiz():
    # Aseguramos la ruta absoluta de Termux
    return Path("/data/data/com.termux/files/home/BIG-Projects/SHADOW_GRIMORIO")

raiz = buscar_raiz()
report_file = raiz / "logs" / "bruma_report.json"

def notificar_tui(estado, mensaje, detalles=None):
    """Escribe el reporte con un timestamp fresco para forzar la reacción de la TUI."""
    report = {
        "status": estado,
        "message": mensaje,
        "details": detalles or [],
        "timestamp": time.time() # Timestamp de alta precisión
    }
    try:
        # Asegurar que el directorio de logs existe
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
    except Exception as e:
        print(f"[ERROR]: No se pudo escribir reporte de Bruma: {e}")

def git_cmd(args):
    try:
        subprocess.run(["git"] + args, cwd=raiz, capture_output=True, check=True)
        return True
    except Exception as e:
        print(f"[GIT ERROR]: {e}")
        return False

class BrumaSync:
    def __init__(self):
        print(f"[BRUMA]: Vigilando cambios en {raiz}")

    def ejecutar_ciclo(self):
        # 1. Verificar cambios reales (incluyendo archivos nuevos no rastreados)
        status = subprocess.run(["git", "status", "--porcelain"],
                               cwd=raiz, capture_output=True, text=True).stdout

        if status.strip():
            print("[BRUMA]: Cambios detectados. Iniciando preservación...")
            timestamp_legible = time.strftime("%H:%M:%S")

            # 2. Notificar inicio a la TUI
            notificar_tui("working", "PRESERVANDO ESTADO...", ["Sincronizando con Git..."])

            # 3. Operaciones Git
            # git add . es vital para que los archivos nuevos cuenten como cambios
            if git_cmd(["add", "."]):
                commit_msg = f"[SHADOW_AUTO]: {timestamp_legible} - Preservación de estado"
                if git_cmd(["commit", "-m", commit_msg]):
                    print(f"[BRUMA]: Commit exitoso a las {timestamp_legible}")
                    notificar_tui("success", "ESTADO PRESERVADO", [
                        f"Hora: {timestamp_legible}",
                        "Rama: dev",
                        "Cambios asegurados en Git"
                    ])
        else:
            # Si no hay cambios, el agente sigue vivo pero no bombardea la TUI
            # Mantenemos el reporte en "success" o lo dejamos como está
            pass

    def run(self):
        print("[BRUMA]: Bruma Online (Modo Vigilante).")
        while True:
            self.ejecutar_ciclo()
            # 3 segundos es genial para debug, pero 10s es más sano para Git
            time.sleep(3) 

if __name__ == "__main__":
    bruma = BrumaSync()
    bruma.run()

