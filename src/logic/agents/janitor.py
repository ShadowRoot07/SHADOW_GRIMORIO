import os
import shutil
import sys
import time
import json
from pathlib import Path

# --- ANCLAJE AL NÚCLEO ---
def buscar_raiz():
    actual = Path(__file__).resolve()
    for padre in actual.parents:
        if (padre / "src").exists():
            return padre
    return actual.parents[3]

raiz = buscar_raiz()
sys.path.append(str(raiz))
report_file = raiz / "logs" / "janitor_report.json"

def notificar(mensaje):
    try:
        with open('/dev/tty', 'w', encoding="utf-8") as tty:
            tty.write(f"\n\x1b[1;35m[JANITOR]:\x1b[0m {mensaje}\n")
    except: pass

class JanitorAgent:
    def __init__(self):
        self.root = raiz
        self.objetivos = ["**/__pycache__", "**/*.pyc", "sabotaje.py", "test_error.py", "temp_file.pyc", "trigger.py"]

    def generar_reporte_tui(self, eliminados):
        if not eliminados: return
        # El timestamp asegura que la TUI detecte que es un reporte NUEVO
        report = {
            "last_purge": str(time.time()), 
            "count": len(eliminados),
            "files": sorted(eliminados) # Ordenados para que se vea mejor
        }
        try:
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
        except: pass

    def limpiar_basura(self):
        eliminados = []
        for patron in self.objetivos:
            for item in self.root.glob(patron):
                try:
                    nombre_relativo = item.relative_to(self.root)
                    if item.is_dir(): shutil.rmtree(item)
                    else: item.unlink()
                    eliminados.append(str(nombre_relativo))
                except: continue
        return eliminados

    def run(self):
        notificar("Conserje del Grimorio Online. Auditoría activa.")
        if report_file.exists(): report_file.unlink()

        while True:
            lista_purgados = self.limpiar_basura()
            if lista_purgados:
                notificar(f"Higienización: {len(lista_purgados)} elementos detectados.")
                self.generar_reporte_tui(lista_purgados)

            time.sleep(10) # Frecuencia de escaneo

if __name__ == "__main__":
    agent = JanitorAgent()
    try: agent.run()
    except KeyboardInterrupt: pass

