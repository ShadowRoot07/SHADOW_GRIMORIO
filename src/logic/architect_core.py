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
        """Extractor de alta resistencia para entornos móviles y Termux."""
        if not texto: return ""
        try:
            # Eliminamos posibles caracteres de control que rompen el buffer
            texto_limpio = "".join(char for char in texto if ord(char) >= 32 or char in "\n\r\t")

            # Buscamos el bloque JSON ignorando cualquier texto decorativo del TUI
            match = re.search(r'(\{.*\})', texto_limpio, re.DOTALL | re.MULTILINE)
            if match:
                candidato = match.group(1).strip()
                # Reparación de urgencia: comas finales antes de cerrar llaves/corchetes
                candidato = re.sub(r',\s*([\]}])', r'\1', candidato)
                return candidato
        except Exception as e:
            logger.error(f"Fallo crítico en extracción: {e}")
        return ""

    def procesar_instruccion(self, raw_response: str, cwd_usuario: str = None):
        """Procesa y valida la intención de construcción del Oráculo."""
        json_puro = self._extraer_json(raw_response)
        if not json_puro:
            return {"status": "error", "message": "No se detectó estructura operativa JSON."}

        try:
            # Limpieza profunda de comentarios y saltos de línea literales
            json_saneado = re.sub(r'//.*?\n|/\*.*?\*/', '', json_puro, flags=re.S)

            # Intentar parseo estándar
            try:
                data = json.loads(json_saneado)
            except json.JSONDecodeError:
                # Si falla por caracteres de escape, intentamos una limpieza manual de escapes
                json_saneado = json_saneado.replace('\n', '\\n').replace('\r', '\\r')
                logger.warning("Sintaxis JSON compleja detectada. Iniciando modo rescate.")
                return self._intento_rescate_manual(json_puro, cwd_usuario)

            target_path = Path(cwd_usuario) if cwd_usuario else self.project_root

            # 1. Soporte para parches (Edición de archivos existentes)
            if "patches" in data:
                return self.aplicar_parches(data["patches"], target_path)

            # 2. Soporte para protocolo de creación/actualización
            plano_final = {"files": [], "folders": data.get("folders", [])}

            if "actions" in data:
                for act in data["actions"]:
                    if act.get("action") in ["create", "update"]:
                        plano_final["files"].append({
                            "path": act["path"],
                            "content": act.get("code") or act.get("content", "")
                        })

            if "files" in data:
                plano_final["files"].extend(data["files"])

            if not plano_final["files"] and not plano_final["folders"]:
                return {"status": "error", "message": "JSON válido pero sin instrucciones de construcción."}

            return self.construir(plano_final, target_path)

        except Exception as e:
            logger.error(f"Fallo general en Architect: {e}")
            return {"status": "error", "message": f"Error en procesamiento: {str(e)}"}

    def construir(self, plano: dict, target_path: Path):
        resumen = []
        try:
            # Asegurar que target_path sea absoluto para evitar ambigüedades en Termux
            target_path = target_path.resolve()
            
            for folder in plano.get("folders", []):
                # .lstrip("/") es vital para que Path / "/ruta" no ignore el target_path
                path = (target_path / folder.lstrip("/")).resolve()
                
                # SEGURIDAD: No permitir escribir fuera del target_path
                if not str(path).startswith(str(target_path)):
                    continue
                    
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

    def _intento_rescate_manual(self, json_roto: str, cwd_usuario: str = None):
        resumen = []
        # Usar el CWD proporcionado o caer en la raíz como último recurso
        base_escritura = Path(cwd_usuario) if cwd_usuario else self.project_root
        
        files_raw = re.findall(r'"path":\s*"(.*?)".*?"(?:code|content)":\s*"(.*?)"', json_roto, re.DOTALL)
        for path_str, content_str in files_raw:
            try:
                # Sanitización: Evitar que la IA intente salir del directorio con ../
                safe_path = path_str.lstrip("/")
                file_path = base_escritura / safe_path
                
                file_path.parent.mkdir(parents=True, exist_ok=True)
                clean_content = content_str.replace("\\n", "\n").replace('\\"', '"')
                file_path.write_text(clean_content, encoding="utf-8")
                resumen.append(f"📄 File (Rescatado): {safe_path}")
            except Exception as e: 
                logger.error(f"Error en rescate de {path_str}: {e}")
                continue
        return {"status": "success", "details": resumen} if resumen else {"status": "error", "message": "Rescate fallido."}

architect = ArchitectCore()

