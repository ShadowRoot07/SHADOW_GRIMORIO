import os
import sys
import time
import json
import traceback
from pathlib import Path

# --- ANCLAJE CRÍTICO ---
def buscar_raiz():
    # En Termux, a veces Path.cwd() es traicionero
    return Path("/data/data/com.termux/files/home/BIG-Projects/SHADOW_GRIMORIO")

raiz = buscar_raiz()
sys.path.append(str(raiz))

# Importación tardía para evitar bloqueos en el arranque
try:
    from src.logic.architect_core import architect
    print("[GHOST]: Núcleo del Arquitecto enlazado.")
except Exception as e:
    print(f"[ERROR CRÍTICO]: No se pudo cargar el Arquitecto: {e}")
    sys.exit(1)

task_file = raiz / "logs" / "coding_task.json"
report_file = raiz / "logs" / "ghost_report.json"

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
        # Notificación por terminal para debug manual
        print(f"[GHOST-DB]: Reporte escrito: {estado} - {mensaje}")
    except Exception as e:
        print(f"[ERROR]: No se pudo escribir reporte JSON: {e}")

class GhostCoder:
    def __init__(self):
        print(f"[GHOST]: Vigilando {task_file}")

    def procesar_cola(self):
        if not task_file.exists():
            return

        print("[GHOST]: ¡Tarea detectada! Procesando...")
        try:
            with open(task_file, "r") as f:
                contenido = f.read().strip()
                if not contenido: return
                task_data = json.loads(contenido)
            
            raw_response = task_data.get("raw_response")
            notificar_tui("working", "TRABAJANDO...", ["Iniciando materialización..."])
            
            # EJECUCIÓN
            resultado = architect.procesar_instruccion(raw_response)
            
            if resultado["status"] == "success":
                print("[GHOST]: Escritura exitosa.")
                notificar_tui("success", "MATERIALIZACIÓN COMPLETADA", resultado["details"])
            else:
                print(f"[GHOST]: Fallo del Arquitecto: {resultado['message']}")
                notificar_tui("error", "ERROR DE ARQUITECTURA", [resultado["message"]])
            
            # Limpieza
            task_file.unlink()
            print("[GHOST]: Tarea finalizada y buzón limpio.")
            
        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"[CRASH]: {error_trace}")
            notificar_tui("error", "CRASH DEL AGENTE", [str(e)])
            if task_file.exists(): task_file.unlink()

    def run(self):
        print("[GHOST]: Fantasma Online (Termux Mode).")
        while True:
            self.procesar_cola()
            time.sleep(1)

if __name__ == "__main__":
    ghost = GhostCoder()
    ghost.run()

