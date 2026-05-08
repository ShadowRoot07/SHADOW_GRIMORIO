import os
import json
import re
from pathlib import Path
from loguru import logger

class ArchitectCore:
    def __init__(self):
        current_file = Path(__file__).resolve()
        # Estructura: src/logic/architect_core.py -> src/logic/ -> src/ -> SHADOW_GRIMORIO/
        self.project_root = current_file.parents[2]
        logger.info(f"🏗️ Base del Grimorio: {self.project_root}")

    def _extraer_json(self, texto: str) -> str:
        """
        Limpia el ruido del Oráculo y extrae solo la estructura JSON.
        Soporta bloques de código markdown y texto plano.
        """
        # 1. Intentar capturar contenido dentro de bloques ```json ... ```
        match_markdown = re.search(r"```json\s*(\{.*?\})\s*```", texto, re.DOTALL)
        if match_markdown:
            return match_markdown.group(1).strip()

        # 2. Fallback: Buscar el primer '{' y el último '}'
        inicio = texto.find("{")
        fin = texto.rfind("}") + 1
        if inicio != -1 and fin > 0:
            return texto[inicio:fin].strip()
        
        return ""

    def planificar(self, raw_response: str):
        """Pre-visualización de cambios para el GhostCoder."""
        plan = []
        json_limpio = self._extraer_json(raw_response)
        if not json_limpio:
            return plan

        try:
            data = json.loads(json_limpio)
            if "patches" in data:
                for p in data["patches"]:
                    plan.append({"type": "edit", "file": p["path"]})
            if "files" in data:
                for f in data["files"]:
                    plan.append({"type": "create", "file": f["path"]})
            return plan
        except:
            return plan

    def procesar_instruccion(self, raw_response: str, cwd_usuario: str = None):
        """Punto de entrada principal para la construcción."""
        json_puro = self._extraer_json(raw_response)
        
        if not json_puro:
            return {"status": "error", "message": "No se detectó estructura operativa JSON."}

        try:
            # Reemplazar posibles comillas inteligentes o errores comunes de LLMs
            # Algunos modelos usan comillas simples por error en las llaves
            # json_puro = json_puro.replace("'", '"') # Opcional: Solo si Spica falla mucho

            data = json.loads(json_puro)
            target_path = Path(cwd_usuario) if cwd_usuario else self.project_root

            if "patches" in data:
                return self.aplicar_parches(data["patches"], target_path)
            
            if "folders" in data or "files" in data:
                return self.construir(data, target_path)
            
            return {"status": "error", "message": "JSON detectado pero vacío de instrucciones."}

        except json.JSONDecodeError as e:
            logger.error(f"Error de sintaxis JSON: {e}")
            return {"status": "error", "message": f"Estructura JSON corrupta: {str(e)}"}
        except Exception as e:
            logger.error(f"Fallo general en Architect: {e}")
            return {"status": "error", "message": str(e)}

    def construir(self, plano: dict, target_path: Path):
        resumen = []
        try:
            # 1. Crear directorios
            for folder in plano.get("folders", []):
                path = target_path / folder.lstrip("/")
                path.mkdir(parents=True, exist_ok=True)
                resumen.append(f"📁 Dir: {folder}")

            # 2. Escribir archivos
            for file_info in plano.get("files", []):
                file_path = target_path / file_info["path"].lstrip("/")
                # Asegurar que el directorio padre existe
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
                    resumen.append(f"❌ Inexistente: {p['path']}")
                    continue

                contenido = file_path.read_text(encoding="utf-8")
                
                # Búsqueda exacta para evitar parches accidentales
                if p["search"] in contenido:
                    nuevo_contenido = contenido.replace(p["search"], p["replace"])
                    file_path.write_text(nuevo_contenido, encoding="utf-8")
                    resumen.append(f"🩹 Patched: {p['path']}")
                else:
                    resumen.append(f"⚠️ Search string no hallada en: {p['path']}")

            return {"status": "success", "details": resumen}
        except Exception as e:
            return {"status": "error", "message": f"Fallo en cirugía de parches: {e}"}

architect = ArchitectCore()

