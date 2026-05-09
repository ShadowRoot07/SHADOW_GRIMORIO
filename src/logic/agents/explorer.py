import os
import json
import time
from pathlib import Path

class Explorer:
    def __init__(self):
        # Localizamos la raíz de forma dinámica
        self.raiz = Path(__file__).resolve().parents[3] 
        self.report_file = self.raiz / "logs" / "explorer_report.json"
        self.ignore_dirs = {'.git', '__pycache__', 'env', 'venv', 'node_modules', 'logs', 'core'}
        print(f"[EXPLORER]: Brújula orientada en {self.raiz}")

    def generar_arbol(self, ruta, prefijo=""):
        tree = []
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
        print("[EXPLORER]: Trazando nueva cartografía...")
        arbol = self.generar_arbol(self.raiz)

        report = {
            "status": "success",
            "message": "MAPA ESTRUCTURAL ACTUALIZADO",
            "tree": arbol,
            "timestamp": time.time(),
            "total_files": len([f for f in self.raiz.rglob('*') if f.is_file()])
        }

        try:
            self.report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.report_file, "w") as f:
                json.dump(report, f, indent=2)
            print(f"[EXPLORER]: Mapa sincronizado ({len(arbol)} nodos).")
        except Exception as e:
            print(f"[ERROR]: {e}")

    def run(self):
        while True:
            self.ejecutar_escaneo()
            time.sleep(60)

if __name__ == "__main__":
    Explorer().run()

