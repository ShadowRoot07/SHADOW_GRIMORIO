import subprocess
import time
import json
import os
from pathlib import Path

# --- CONFIGURACIÓN DE RUTAS ---
def buscar_raiz():
    return Path("/data/data/com.termux/files/home/BIG-Projects/SHADOW_GRIMORIO")

raiz = buscar_raiz()
report_file = raiz / "logs" / "bruma_report.json"

def notificar_tui(estado, mensaje, detalles=None):
    report = {
        "status": estado,
        "message": mensaje,
        "details": detalles or [],
        "timestamp": time.time()
    }
    try:
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
        # 1. Verificar cambios reales
        status = subprocess.run(["git", "status", "--porcelain"], 
                               cwd=raiz, capture_output=True, text=True).stdout
        
        if status.strip():
            print("[BRUMA]: Cambios detectados. Iniciando preservación...")
            timestamp = time.strftime("%H:%M:%S")
            
            # 2. Notificar inicio a la TUI
            notificar_tui("working", "PRESERVANDO ESTADO...", ["Sincronizando con Git..."])
            
            # 3. Operaciones Git
            if git_cmd(["add", "."]):
                commit_msg = f"[SHADOW_AUTO]: {timestamp} - Preservación de estado"
                if git_cmd(["commit", "-m", commit_msg]):
                    print(f"[BRUMA]: Commit exitoso a las {timestamp}")
                    notificar_tui("success", "ESTADO PRESERVADO", [
                        f"Hora: {timestamp}",
                        "Rama: dev",
                        "Cambios asegurados en Git"
                    ])
        else:
            # Opcional: limpiar reporte anterior si no hay cambios
            if report_file.exists():
                pass 

    def run(self):
        print("[BRUMA]: Bruma Online (Modo Vigilante).")
        while True:
            self.ejecutar_ciclo()
            time.sleep(3) # Sincroniza cada 5 minutos

if __name__ == "__main__":
    bruma = BrumaSync()
    bruma.run()

