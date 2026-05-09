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
        Extractor de alto rendimiento: Ignora explicaciones y limpia sintaxis común de LLMs.
        """
        if not texto:
            return ""

        # 1. Intentar capturar el bloque más grande que empiece con { y termine con }
        # Usamos una búsqueda no ambiciosa para encontrar el objeto principal
        try:
            # Buscamos desde el primer '{' hasta el último '}'
            match = re.search(r'(\{.*\})', texto, re.DOTALL | re.MULTILINE)
            if match:
                candidato = match.group(1).strip()
                
                # --- LIMPIEZA DE SINTAXIS LLM ---
                # Eliminar comas finales antes de llaves de cierre [1, 2,] -> [1, 2]
                candidato = re.sub(r',\s*([\]}])', r'\1', candidato)
                # Eliminar caracteres de control (saltos de línea raros, etc)
                candidato = "".join(char for char in candidato if ord(char) >= 32 or char in "\n\r\t")
                
                return candidato
        except Exception as e:
            logger.error(f"Fallo en extracción quirúrgica: {e}")

        return ""

    def procesar_instruccion(self, raw_response: str, cwd_usuario: str = None):
        """Intenta parsear el JSON y si falla, busca repararlo."""
        json_puro = self._extraer_json(raw_response)

        if not json_puro:
            return {"status": "error", "message": "No se detectó estructura operativa JSON."}

        try:
            # Eliminar comentarios de estilo JS (// o /* */) que Spica a veces incluye
            json_saneado = re.sub(r'//.*?\n|/\*.*?\*/', '', json_puro, flags=re.S)
            
            data = json.loads(json_saneado)
            target_path = Path(cwd_usuario) if cwd_usuario else self.project_root

            if "patches" in data:
                return self.aplicar_parches(data["patches"], target_path)

            if "folders" in data or "files" in data:
                return self.construir(data, target_path)

            return {"status": "error", "message": "JSON detectado pero sin instrucciones válidas."}

        except json.JSONDecodeError:
            # ÚLTIMO RECURSO: Intentar un parseo parcial o manual si el JSON está truncado
            logger.warning("⚠️ JSON Corrupto detectado. Intentando rescate de emergencia...")
            return self._intento_rescate_manual(json_puro)

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
            json_saneado = re.sub(r'^\s*//.*$', '', json_puro, flags=re.MULTILINE)  
            data = json.loads(json_saneado)
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

    def _intento_rescate_manual(self, json_roto: str):
        """Si el JSON está incompleto, intenta extraer al menos los archivos que estén íntegros."""
        resumen = []
        # Buscar patrones de contenido de archivos: "path": "...", "content": "..."
        files_raw = re.findall(r'\{\s*"path":\s*"(.*?)",\s*"content":\s*"(.*?)"\s*\}', json_roto, re.DOTALL)
        
        if not files_raw:
            return {"status": "error", "message": "Incapaz de rescatar datos del JSON corrupto."}
            
        for path_str, content_str in files_raw:
            try:
                # Decodificar escapes de strings (\n, \t, etc)
                content_clean = content_str.encode().decode('unicode_escape')
                file_path = self.project_root / path_str.lstrip("/")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content_clean, encoding="utf-8")
                resumen.append(f"📄 File (Rescatado): {path_str}")
            except:
                continue
                
        return {"status": "success", "details": resumen} if resumen else {"status": "error", "message": "Rescate fallido."}


architect = ArchitectCore()

