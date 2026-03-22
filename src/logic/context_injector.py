import os
from src.database.manager import db
from src.database.models import Usuario, Conocimiento
from src.logic.identity_matrix import AGENT_IDENTITIES
from loguru import logger

class ContextInjector:
    """Motor de contexto: Une el perfil del usuario, la identidad del agente y el sistema de archivos."""

    @staticmethod
    def leer_archivo_proyecto(ruta_relativa: str) -> str:
        """Lee un archivo del proyecto para que el Agente pueda analizarlo."""
        try:
            # Limpiamos la ruta por si viene con basura
            ruta_limpia = ruta_relativa.strip().replace("`", "")
            if os.path.exists(ruta_limpia) and os.path.isfile(ruta_limpia):
                with open(ruta_limpia, "r", encoding="utf-8") as f:
                    contenido = f.read()
                    return f"\n--- CONTENIDO DEL ARCHIVO ({ruta_limpia}) ---\n{contenido}\n--- FIN DEL ARCHIVO ---\n"
            return f"\n[!] Advertencia: No se pudo leer el archivo '{ruta_limpia}'."
        except Exception as e:
            return f"\n[!] Error al acceder al sistema de archivos: {e}"

    @staticmethod
    def obtener_contexto_completo(agente_id: str = None, query_usuario: str = "") -> str:
        session = db.get_session()
        try:
            # 1. Datos del Usuario (ShadowRoot07)
            user = session.query(Usuario).first()
            alias = user.alias if user else "ShadowRoot07"
            
            # 2. Construcción del Prompt Base
            prompt = f"ERES EL SHADOW_GRIMORIO, EL ENJAMBRE IA DE {alias.upper()}.\n"

            # 3. IDENTIDAD DEL AGENTE
            if agente_id and agente_id.upper() in AGENT_IDENTITIES:
                identidad = AGENT_IDENTITIES[agente_id.upper()]
                prompt += f"\n[ROL ACTIVO: {agente_id}]\n"
                prompt += f"PERSONALIDAD: {identidad['prompt']}\n"
                prompt += f"RASGO: {identidad['trait']}\n"

            # 4. INYECCIÓN DE ARCHIVOS (Detección inteligente)
            # Si la pregunta contiene una ruta que existe, la inyectamos automáticamente
            for palabra in query_usuario.split():
                if "/" in palabra or "." in palabra: # Probable ruta de archivo
                    if os.path.exists(palabra.strip("., ")):
                        prompt += ContextInjector.leer_archivo_proyecto(palabra.strip("., "))

            prompt += "\nDIRECTRICES:\n- Tono Cyberpunk/Técnico.\n- Habla siempre en español."
            return prompt
        except Exception as e:
            logger.error(f"Error en ContextInjector: {e}")
            return "Eres el SHADOW_GRIMORIO. El usuario es ShadowRoot07."
        finally:
            session.close()

