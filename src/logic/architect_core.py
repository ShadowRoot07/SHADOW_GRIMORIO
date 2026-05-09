import os
import json
import re
from pathlib import Path
from loguru import logger

class ArchitectCore:
    def __init__(self):
        current_file = Path(__file__).resolve()
<<<<<<< HEAD
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
        
=======
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
>>>>>>> final-fix-branch
        if not json_puro:
            return {"status": "error", "message": "No se detectó estructura operativa JSON."}

        try:
<<<<<<< HEAD
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
=======
            # Limpieza profunda de comentarios y saltos de línea literales
            json_saneado = re.sub(r'//.*?\n|/\*.*?\*/', '', json_puro, flags=re.S)
            
            # Intentar parseo estándar
            try:
                data = json.loads(json_saneado)
            except json.JSONDecodeError:
                # Si falla por caracteres de escape, intentamos una limpieza manual de escapes
                # Esto ayuda con el error 'Expecting , delimiter'
                json_saneado = json_saneado.replace('\n', '\\n').replace('\r', '\\r')
                # Intentamos rescatar los componentes básicos si el JSON es demasiado complejo
                logger.warning("Sintaxis JSON compleja detectada. Iniciando modo rescate.")
                return self._intento_rescate_manual(json_puro)

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
>>>>>>> final-fix-branch

    def construir(self, plano: dict, target_path: Path):
        resumen = []
        try:
<<<<<<< HEAD
            # 1. Crear directorios
=======
>>>>>>> final-fix-branch
            for folder in plano.get("folders", []):
                path = target_path / folder.lstrip("/")
                path.mkdir(parents=True, exist_ok=True)
                resumen.append(f"📁 Dir: {folder}")

<<<<<<< HEAD
            # 2. Escribir archivos
            for file_info in plano.get("files", []):
                file_path = target_path / file_info["path"].lstrip("/")
                # Asegurar que el directorio padre existe
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
=======
            for file_info in plano.get("files", []):
                file_path = target_path / file_info["path"].lstrip("/")
                file_path.parent.mkdir(parents=True, exist_ok=True)
>>>>>>> final-fix-branch
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(file_info["content"])
                resumen.append(f"📄 File: {file_info['path']}")

            return {"status": "success", "details": resumen}
        except Exception as e:
            return {"status": "error", "message": f"Error de escritura: {e}"}

    def aplicar_parches(self, patches: list, target_path: Path):
        resumen = []
<<<<<<< HEAD
        try:
            for p in patches:
=======
        for p in patches:
            try:
>>>>>>> final-fix-branch
                file_path = target_path / p["path"].lstrip("/")
                if not file_path.exists():
                    resumen.append(f"❌ Inexistente: {p['path']}")
                    continue
<<<<<<< HEAD

                contenido = file_path.read_text(encoding="utf-8")
                
                # Búsqueda exacta para evitar parches accidentales
=======
                contenido = file_path.read_text(encoding="utf-8")
>>>>>>> final-fix-branch
                if p["search"] in contenido:
                    nuevo_contenido = contenido.replace(p["search"], p["replace"])
                    file_path.write_text(nuevo_contenido, encoding="utf-8")
                    resumen.append(f"🩹 Patched: {p['path']}")
                else:
                    resumen.append(f"⚠️ Search string no hallada en: {p['path']}")
<<<<<<< HEAD

            return {"status": "success", "details": resumen}
        except Exception as e:
            return {"status": "error", "message": f"Fallo en cirugía de parches: {e}"}
=======
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
>>>>>>> final-fix-branch

architect = ArchitectCore()

