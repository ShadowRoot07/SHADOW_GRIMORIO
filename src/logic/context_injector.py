import os
from pathlib import Path
from src.database.manager import db
from src.database.models import Usuario
from src.logic.identity_matrix import AGENT_IDENTITIES
from loguru import logger

class ContextInjector:
    """Motor de contexto con GHOST_SHELL (Privacidad) y Control de Idioma Estricto."""

    @staticmethod
    def filtrar_privacidad(texto: str) -> str:
        """Oculta rutas reales de Termux/Android."""
        ruta_termux = "/data/data/com.termux/files/home"
        return texto.replace(ruta_termux, "~")

    @staticmethod
    def obtener_ultimos_logs(n_lineas: int = 15) -> str:
        log_path = Path("logs/shadow_grimorio.log")
        if log_path.exists():
            with open(log_path, "r") as f:
                lineas = f.readlines()
                return "".join(lineas[-n_lineas:])
        return "No hay logs de ejecuciones previas."

    @staticmethod
    def obtener_contexto_completo(agente_id: str = None, query_usuario: str = "") -> str:
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            alias = user.alias if user else "ShadowRoot07"

            # 1. REGLAS PRIORITARIAS (IDIOMA Y FORMATO)
            prompt = (
                "### REGLAS DE ORO (ESTRICTAS) ###\n"
                "- IDIOMA: Responde ÚNICAMENTE en ESPAÑOL.\n"
                "- TONO: Cyberpunk, técnico, directo y cínico.\n"
                "- FORMATO: Usa Markdown para el código y negritas para énfasis.\n\n"
            )

            # 2. IDENTIDAD DEL AGENTE
            prompt += f"ERES EL SHADOW_GRIMORIO, EL ENJAMBRE IA DE {alias.upper()}.\n"

            if agente_id and agente_id.upper() in AGENT_IDENTITIES:
                agente = AGENT_IDENTITIES[agente_id.upper()]
                prompt += f"[IDENTIDAD ACTIVA: {agente_id}]\n"
                prompt += f"DIRECTRIZ: {agente['prompt']}\n"
                prompt += f"RASGO: {agente['trait']}\n"

            # 3. GHOST_SHELL (ARCHIVOS)
            for palabra in query_usuario.split():
                if "/" in palabra or "." in palabra:
                    path_candidato = palabra.strip("., \"'`")
                    if os.path.exists(path_candidato) and os.path.isfile(path_candidato):
                        with open(path_candidato, "r", encoding="utf-8") as f:
                            contenido = f.read()
                            prompt += f"\n--- DATA_DUMP: {path_candidato} ---\n{contenido}\n"

            # 4. MEMORIA (LOGS)
            prompt += f"\n--- TELEMETRÍA RECIENTE ---\n{ContextInjector.obtener_ultimos_logs()}"
            
            prompt += "\n\n[SISTEMA LISTO. RESPONDE EN ESPAÑOL AHORA.]\n"

            return ContextInjector.filtrar_privacidad(prompt)

        except Exception as e:
            logger.error(f"Error en ContextInjector: {e}")
            return "ERROR DE CONTEXTO. MODO SEGURO: ESPAÑOL ACTIVO."
        finally:
            session.close()

