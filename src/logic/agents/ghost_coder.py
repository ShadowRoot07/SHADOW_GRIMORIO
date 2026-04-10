import os
import sys
import time
import json
import shutil
import traceback
import tempfile
from pathlib import Path

def buscar_raiz():
    termux_path = Path("/data/data/com.termux/files/home/BIG-Projects/SHADOW_GRIMORIO")
    return termux_path if termux_path.exists() else Path(__file__).resolve().parents[3]

raiz = buscar_raiz()
if str(raiz) not in sys.path:
    sys.path.append(str(raiz))

try:
    from src.logic.architect_core import architect
    from src.logic.agents.lexicon_indexer import indexar_proyecto
    print("[GHOST]: Núcleos vinculados (Groq-Engine + Lexicon).")
except Exception as e:
    print(f"[ERROR CRÍTICO]: Fallo en vinculación: {e}")
    sys.exit(1)

# --- CONFIGURACIÓN DE CANALES ---
LOGS_DIR = raiz / "logs"
BACKUP_DIR = raiz / "data" / "backups"
TASK_FILE = LOGS_DIR / "coding_task.json"
REPORT_FILE = LOGS_DIR / "ghost_report.json"

# Asegurar directorios
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

class GhostCoder:
    def __init__(self):
        self.running = True

    def crear_backup(self, file_path_str: str):
        """Crea una copia de seguridad antes de intervenir un archivo existente."""
        target = raiz / file_path_str
        if target.exists() and target.is_file():
            timestamp = int(time.time())
            backup_path = BACKUP_DIR / f"{target.name}.{timestamp}.bak"
            shutil.copy2(target, backup_path)
            return str(backup_path)
        return None

    def notificar_tui(self, estado, mensaje, detalles=None):
        """Envía el estado al Oráculo (TUI)."""
        report = {
            "status": estado,
            "message": mensaje,
            "details": detalles or [],
            "timestamp": time.time()
        }
        with tempfile.NamedTemporaryFile('w', dir=LOGS_DIR, delete=False) as tf:
            json.dump(report, tf, indent=2)
            temp_name = tf.name
        Path(temp_name).replace(REPORT_FILE)

    def procesar_cola(self):
        if not TASK_FILE.exists():
            return

        print("\n[GHOST]: Instrucción recibida. Iniciando posesión de archivos...")
        try:
            with open(TASK_FILE, "r") as f:
                task_data = json.load(f)

            # Extraer la respuesta de Groq que viene desde el Oráculo
            raw_response = task_data.get("raw_response")
            if not raw_response:
                TASK_FILE.unlink()
                return

            self.notificar_tui("working", "GHOST CODER ACTIVO", ["Analizando estructura...", "Preparando backups..."])

            # 1. El Arquitecto parsea la respuesta de Groq para saber QUÉ archivos tocar
            # Supongamos que ArchitectCore devuelve una lista de acciones
            plan = architect.planificar(raw_response) 
            
            for accion in plan:
                if accion.get("type") == "edit":
                    b_path = self.crear_backup(accion.get("file"))
                    print(f"[GHOST]: Backup creado en {b_path}")

            # 2. EJECUCIÓN: El Arquitecto aplica los cambios
            resultado = architect.procesar_instruccion(raw_response)

            if resultado["status"] == "success":
                # 3. REFRESCAR LEXICON: Para que el Oráculo sepa que el archivo cambió
                print("[GHOST]: Sincronizando Lexicon...")
                indexar_proyecto()
                
                self.notificar_tui("success", "MATERIALIZACIÓN COMPLETADA", 
                                  resultado.get("details", ["Archivos modificados con éxito."]))
            else:
                self.notificar_tui("error", "FALLO ARQUITECTÓNICO", [resultado.get("message")])

        except Exception as e:
            self.notificar_tui("error", "CRASH EN EL ÉTER", [str(e)])
            print(f"[CRASH]: {traceback.format_exc()}")
        finally:
            if TASK_FILE.exists():
                TASK_FILE.unlink()

    def run(self):
        print(f"\033[1;35m[GHOST_CODER]\033[0m: Fantasma en línea. Vigilando {TASK_FILE}")
        try:
            while self.running:
                self.procesar_cola()
                time.sleep(1.5)
        except KeyboardInterrupt:
            print("\n[GHOST]: Desmaterializando agente...")

if __name__ == "__main__":
    GhostCoder().run()

