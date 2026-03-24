import os
import json
from pathlib import Path
from loguru import logger

class ArchitectCore:
    def __init__(self):
        current_file = Path(__file__).resolve()
        # src/logic/architect_core.py -> src/logic/ -> src/ -> SHADOW_GRIMORIO/
        self.project_root = current_file.parents[2]
        logger.info(f"🏗️ Base del Grimorio: {self.project_root}")

    def procesar_instruccion(self, raw_response: str, cwd_usuario: str = None):
        try:
            inicio = raw_response.find("{")
            fin = raw_response.rfind("}") + 1
            if inicio == -1 or fin == 0:
                return {"status": "error", "message": "No se detectó estructura JSON."}

            data = json.loads(raw_response[inicio:fin])
            target_path = Path(cwd_usuario) if cwd_usuario else self.project_root

            if "patches" in data:
                return self.aplicar_parches(data["patches"], target_path)
            return self.construir(data, target_path)

        except Exception as e:
            logger.error(f"Error en ArchitectCore: {e}")
            return {"status": "error", "message": str(e)}

    def construir(self, plano: dict, target_path: Path):
        resumen = []
        try:
            for folder in plano.get("folders", []):
                path = target_path / folder.lstrip("/")
                path.mkdir(parents=True, exist_ok=True)
                resumen.append(f"📁 Dir: {folder}")

            for file_info in plano.get("files", []):
                file_path = target_path / file_info["path"].lstrip("/")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(file_info["content"])
                resumen.append(f"📄 File: {file_info['path']}")

            return {"status": "success", "details": resumen}
        except Exception as e:
            return {"status": "error", "message": f"Error de escritura: {e}"}

    def aplicar_parches(self, patches: list, target_path: Path):
        resumen = []
        try:
            for p in patches:
                file_path = target_path / p["path"].lstrip("/")
                if not file_path.exists():
                    resumen.append(f"❌ No existe: {p['path']}")
                    continue

                contenido = file_path.read_text(encoding="utf-8")
                if p["search"] in contenido:
                    nuevo_contenido = contenido.replace(p["search"], p["replace"])
                    file_path.write_text(nuevo_contenido, encoding="utf-8")
                    resumen.append(f"🩹 Patched: {p['path']}")
                else:
                    resumen.append(f"⚠️ No hallado: {p['path']}")

            return {"status": "success", "details": resumen}
        except Exception as e:
            return {"status": "error", "message": f"Fallo en parche: {e}"}

# --- ESTA LÍNEA ES LA QUE EVITA EL ERROR DE IMPORTACIÓN ---
architect = ArchitectCore()

