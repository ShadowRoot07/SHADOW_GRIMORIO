import subprocess
import time
import json
import os
from pathlib import Path

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
        report_file.parent.mkdir(parents=True, exist_ok=True)
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
    except Exception as e:
        print(f"[ERROR]: {e}")

def git_cmd(args):
    try:
        subprocess.run(["git"] + args, cwd=raiz, capture_output=True, check=True)
        return True
    except:
        return False

class BrumaSync:
    def __init__(self):
        # Al iniciar, limpiamos reportes viejos para empezar de cero
        if report_file.exists():
            report_file.unlink()

    def ejecutar_ciclo(self):
        status = subprocess.run(["git", "status", "--porcelain"],
                               cwd=raiz, capture_output=True, text=True).stdout

        if status.strip():
            print("[BRUMA]: Cambios detectados...")
            timestamp_legible = time.strftime("%H:%M:%S")

            notificar_tui("working", "PRESERVANDO ESTADO...", ["Iniciando Git Add..."])
            
            if git_cmd(["add", "."]):
                if git_cmd(["commit", "-m", f"[SHADOW_AUTO]: {timestamp_legible}"]):
                    print(f"[BRUMA]: Éxito {timestamp_legible}")
                    notificar_tui("success", "ESTADO PRESERVADO", [
                        f"Hora: {timestamp_legible}",
                        "Sincronización: Exitosa"
                    ])
                    # IMPORTANTE: No borramos el archivo aquí para que la TUI lo vea
        else:
            # Si el repo está limpio, podemos borrar el reporte viejo después de un rato
            # para que la TUI sepa que no hay nada pendiente.
            pass

    def run(self):
        print("[BRUMA]: Online.")
        while True:
            self.ejecutar_ciclo()
            time.sleep(300) # 5 minutos para cada commit 

if __name__ == "__main__":
    BrumaSync().run()

