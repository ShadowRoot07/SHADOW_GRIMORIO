import json
import time
from pathlib import Path

current_path = Path(__file__).resolve()
base_path = current_path.parents[3]
index_file = base_path / "logs" / "lexicon_index.json"
report_file = base_path / "logs" / "void_hunter_report.json"

class VoidHunter:
    def __init__(self):
        self.findings = []

    def analizar_vacio(self):
        self.findings = []
        if not index_file.exists():
            return {"status": "waiting", "message": "Esperando índice..."}

        try:
            with open(index_file, "r") as f:
                index = json.load(f)

            for ruta, items in index.items():
                # CASO 1: Archivo totalmente vacío
                if len(items) == 0:
                    self.findings.append({
                        "file": ruta,
                        "issue": "Archivo sin lógica (vacío).",
                        "fix": "Añadir código o eliminar si es residual."
                    })

                # CASO 2: Lógica de test fuera de /tests/
                for item in items:
                    if "Func: test" in item and "tests/" not in ruta:
                        self.findings.append({
                            "file": ruta,
                            "issue": f"Test expuesto en producción: {item}",
                            "fix": "Mover a la carpeta /tests/ o renombrar."
                        })
                
                # CASO 3: Archivos corruptos detectados por Lexicon
                if any("ERROR" in str(i) for i in items):
                    self.findings.append({
                        "file": ruta,
                        "issue": "Error de sintaxis crítica.",
                        "fix": "Revisar indentación o símbolos faltantes."
                    })

            return {
                "status": "success",
                "findings": self.findings,
                "timestamp": time.time(),
                "indexed_files": len(index)
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def run(self):
        print("\033[94m[VOID_HUNTER]\033[0m: Analizador semántico activo.")
        while True:
            report = self.analizar_vacio()
            if report.get("status") == "success":
                with open(report_file, "w") as f:
                    json.dump(report, f, indent=2)
                print(f"[VOID_HUNTER]: Escaneo listo. Hallazgos: {len(self.findings)}")
            time.sleep(60)

if __name__ == "__main__":
    VoidHunter().run()

