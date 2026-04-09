import os
import sys
import time
import json
import traceback
import tempfile
from pathlib import Path

# --- ANCLAJE DE RUTA ---
def buscar_raiz():
    # Prioridad absoluta a la ruta de desarrollo en Termux
    termux_path = Path("/data/data/com.termux/files/home/BIG-Projects/SHADOW_GRIMORIO")
    if termux_path.exists():
        return termux_path
    # Fallback dinámico por si cambias de dispositivo
    return Path(__file__).resolve().parents[3]

raiz = buscar_raiz()
if str(raiz) not in sys.path:
    sys.path.append(str(raiz))

# Importación del Arquitecto (El que realmente edita los archivos)
try:
    from src.logic.architect_core import architect
    # También importamos el indexer para refrescar tras escribir
    from src.logic.agents.lexicon_indexer import indexar_proyecto
    print("[GHOST]: Conexión con el Arquitecto y Lexicon establecida.")
except Exception as e:
    print(f"[ERROR CRÍTICO]: Fallo en vinculación de núcleos: {e}")
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
        # Escritura atómica para evitar que la TUI lea un JSON incompleto
        with tempfile.NamedTemporaryFile('w', dir=report_file.parent, delete=False) as tf:
            json.dump(report, tf, indent=2)
            temp_name = tf.name
        Path(temp_name).replace(report_file)
    except Exception as e:
        print(f"[ERROR]: No se pudo escribir reporte: {e}")

class GhostCoder:
    def __init__(self):
        print(f"[GHOST]: Vigilando canal de tareas en {task_file}")

    def procesar_cola(self):
        if not task_file.exists():
            return

        print("[GHOST]: ¡Pulso detectado! Materializando código...")
        try:
            # Leer tarea
            with open(task_file, "r") as f:
                task_data = json.load(f)

            raw_response = task_data.get("raw_response")
            if not raw_response:
                task_file.unlink()
                return

            notificar_tui("working", "MATERIALIZANDO...", ["El Fantasma está poseyendo los archivos..."])

            # EJECUCIÓN: El Arquitecto hace la magia
            resultado = architect.procesar_instruccion(raw_response)

            if resultado["status"] == "success":
                print("[GHOST]: Escritura completada exitosamente.")
                
                # REFRESCAR EL CEREBRO: Forzamos al Lexicon a ver el nuevo código
                print("[GHOST]: Sincronizando Lexicon...")
                indexar_proyecto()
                
                notificar_tui("success", "MATERIALIZACIÓN COMPLETADA", resultado.get("details", []))
            else:
                print(f"[GHOST]: Error de Arquitectura: {resultado.get('message')}")
                notificar_tui("error", "FALLO EN LA ESTRUCTURA", [resultado.get("message")])

            # Limpiar buzón
            if task_file.exists():
                task_file.unlink()

        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"[CRASH]: {error_trace}")
            notificar_tui("error", "CRASH EN EL ÉTER", [str(e)])
            if task_file.exists(): 
                task_file.unlink()

    def run(self):
        print("\033[1;35m[GHOST_CODER]\033[0m: Fantasma Online (Esperando tareas...)")
        while True:
            self.procesar_cola()
            # Un segundo es perfecto para no fundir la batería del ZTE
            time.sleep(1)

if __name__ == "__main__":
    ghost = GhostCoder()
    ghost.run()

