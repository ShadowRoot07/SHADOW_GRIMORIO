import os
import json
from loguru import logger

class ArchitectCore:
    """El ejecutor material de las estructuras de archivos."""

    def __init__(self, base_path=None):
        # Por seguridad, operamos relativo a la raíz del proyecto o una carpeta 'workspace'
        self.base_path = base_path or os.getcwd()

    def procesar_instruccion(self, raw_response: str):
        """
        Parsea la respuesta del Oráculo. 
        Busca un bloque JSON para extraer la estructura de archivos.
        """
        try:
            # Intentamos extraer el JSON si la IA puso texto alrededor
            inicio = raw_response.find("{")
            fin = raw_response.rfind("}") + 1
            if inicio == -1 or fin == 0:
                return {"status": "error", "message": "No se detectó estructura de construcción."}
            
            data = json.loads(raw_response[inicio:fin])
            return self.construir(data)
        except Exception as e:
            logger.error(f"Error al parsear plano del Arquitecto: {e}")
            return {"status": "error", "message": str(e)}

    def construir(self, plano: dict):
        """Crea las carpetas y archivos definidos en el plano."""
        resumen = []
        try:
            # 1. Crear directorios
            for folder in plano.get("folders", []):
                path = os.path.join(self.base_path, folder)
                os.makedirs(path, exist_ok=True)
                resumen.append(f"📁 Dir: {folder}")

            # 2. Crear archivos
            for file_info in plano.get("files", []):
                file_path = os.path.join(self.base_path, file_info["path"])
                
                # Asegurar que el directorio padre exista
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(file_info["content"])
                resumen.append(f"📄 File: {file_info['path']}")

            return {
                "status": "success", 
                "details": resumen, 
                "description": plano.get("description", "Construcción finalizada.")
            }
        except Exception as e:
            logger.error(f"Fallo en la construcción: {e}")
            return {"status": "error", "message": str(e)}

# Instancia global
architect = ArchitectCore()

