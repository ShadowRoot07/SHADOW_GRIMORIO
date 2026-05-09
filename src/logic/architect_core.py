import os
import json
import re
from pathlib import Path
from loguru import logger

class ArchitectCore:
    def __init__(self):
        current_file = Path(__file__).resolve()
        self.project_root = current_file.parents[2]
        logger.info(f"🏗️ Base del Grimorio: {self.project_root}")

    def _extraer_json(self, texto: str) -> str:
        """Extrae el bloque JSON ignorando basura visual del TUI."""
        if not texto: return ""
        try:
            # Busca desde el primer '{' hasta el último '}'
            match = re.search(r'(\{.*\})', texto, re.DOTALL | re.MULTILINE)
            if match:
                candidato = match.group(1).strip()
                # Limpieza de comas finales y caracteres de control
                candidato = re.sub(r',\s*([\]}])', r'\1', candidato)
                return "".join(char for char in candidato if ord(char) >= 32 or char in "\n\r\t")
        except Exception as e:
            logger.error(f"Fallo en extracción: {e}")
        return ""

    def procesar_instruccion(self, raw_response: str, cwd_usuario: str = None):
        """Punto de entrada único para la construcción."""
        json_puro = self._extraer_json(raw_response)
        if not json_puro:
            return {"status": "error", "message": "No se detectó estructura operativa JSON."}

        try:
            # Limpiar comentarios y parsear
            json_saneado = re.sub(r'//.*?\n|/\*.*?\*/', '', json_puro, flags=re.S)
            data = json.loads(json_saneado)
            target_path = Path(cwd_usuario) if cwd_usuario else self.project_root

            # --- LÓGICA DE COMPATIBILIDAD ---
            # 1. Soporte para parches
            if "patches" in data:
                return self.aplicar_parches(data["patches"], target_path)

            # 2. Soporte para el protocolo "actions" (Spica)
            if "actions" in data:
                # Mapeamos "actions" al formato interno "files"
                plano_mapeado = {"files": []}
                for act in data["actions"]:
                    if act.get("action") in ["create", "update"]:
                        plano_mapeado["files"].append({
                            "path": act["path"],
                            "content": act.get("code") or act.get("content")
                        })
                return self.construir(plano_mapeado, target_path)

            # 3. Soporte para formato nativo "files" / "folders"
            if "folders" in data or "files" in data:
                return self.construir(data, target_path)

            return {"status": "error", "message": "🚨 JSON detectado pero sin instrucciones válidas (Faltan actions/files)."}

        except json.JSONDecodeError as e:
            logger.warning("⚠️ JSON Corrupto. Intentando rescate de emergencia...")
            return self._intento_rescate_manual(json_puro)
        except Exception as e:
            logger.error(f"Fallo general en Architect: {e}")
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
        for p in patches:
            try:
                file_path = target_path / p["path"].lstrip("/")
                if not file_path.exists():
                    resumen.append(f"❌ Inexistente: {p['path']}")
                    continue
                contenido = file_path.read_text(encoding="utf-8")
                if p["search"] in contenido:
                    nuevo_contenido = contenido.replace(p["search"], p["replace"])
                    file_path.write_text(nuevo_contenido, encoding="utf-8")
                    resumen.append(f"🩹 Patched: {p['path']}")
                else:
                    resumen.append(f"⚠️ Search string no hallada en: {p['path']}")
            except Exception as e:
                resumen.append(f"🔥 Error en {p['path']}: {e}")
        return {"status": "success", "details": resumen}

    def _intento_rescate_manual(self, json_roto: str):
        resumen = []
        # Regex flexible para capturar path y contenido incluso en JSON mal formado
        files_raw = re.findall(r'"path":\s*"(.*?)".*?"(?:code|content)":\s*"(.*?)"', json_roto, re.DOTALL)
        for path_str, content_str in files_raw:
            try:
                file_path = self.project_root / path_str.lstrip("/")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                # Intentar limpiar escapes de texto
                clean_content = content_str.replace("\\n", "\n").replace('\\"', '"')
                file_path.write_text(clean_content, encoding="utf-8")
                resumen.append(f"📄 File (Rescatado): {path_str}")
            except: continue
        return {"status": "success", "details": resumen} if resumen else {"status": "error", "message": "Rescate fallido."}

architect = ArchitectCore()

