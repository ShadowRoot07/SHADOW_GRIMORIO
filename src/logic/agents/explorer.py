import os
import json
import time
from pathlib import Path

def buscar_raiz():
    return Path("/data/data/com.termux/files/home/BIG-Projects/SHADOW_GRIMORIO")

raiz = buscar_raiz()
report_file = raiz / "logs" / "explorer_report.json"

class Explorer:
    def __init__(self):
        self.ignore_dirs = {'.git', '__pycache__', 'env', 'venv', 'node_modules', 'logs'}
        print(f"[EXPLORER]: Brújula orientada en {raiz}")

    def generar_arbol(self, ruta, prefijo=""):
        """Genera una representación visual del árbol de directorios."""
        tree = []
        # Obtener items y filtrar ignorados
        try:
            items = sorted([i for i in os.listdir(ruta) if i not in self.ignore_dirs])
        except PermissionError:
            return tree

        for i, nombre in enumerate(items):
            ruta_completa = os.path.join(ruta, nombre)
            es_ultimo = (i == len(items) - 1)
            conector = "└── " if es_ultimo else "├── "
            
            tree.append(f"{prefijo}{conector}{nombre}")
            
            if os.path.isdir(ruta_completa):
                nuevo_prefijo = prefijo + ("    " if es_ultimo else "│   ")
                tree.extend(self.generar_arbol(ruta_completa, nuevo_prefijo))
        
        return tree

    def ejecutar_escaneo(self):
        print("[EXPLORER]: Escaneando estructura del Grimorio...")
        arbol = self.generar_arbol(raiz)
        
        report = {
            "status": "success",
            "message": "MAPA ESTRUCTURAL ACTUALIZADO",
            "tree": arbol,
            "timestamp": time.time(),
            "total_files": len([f for f in raiz.rglob('*') if f.is_file()])
        }

        try:
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
            print(f"[EXPLORER]: Mapa guardado. ({len(arbol)} elementos)")
        except Exception as e:
            print(f"[ERROR]: {e}")

    def run(self):
        print("[EXPLORER]: Online (Modo Cartógrafo).")
        while True:
            self.ejecutar_escaneo()
            # Escanea cada 60 segundos o cuando lo necesites manualmente
            time.sleep(60)

if __name__ == "__main__":
    Explorer().run()

