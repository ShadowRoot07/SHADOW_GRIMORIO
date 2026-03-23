import os
from pathlib import Path
from src.database.manager import db
from src.database.models import Usuario
from src.logic.identity_matrix import AGENT_IDENTITIES
from loguru import logger

class ContextInjector:
    """Motor de contexto optimizado para terminales móviles (ZTE-Blade-A54)."""

    @staticmethod
    def filtrar_privacidad(texto: str) -> str:
        ruta_termux = "/data/data/com.termux/files/home"
        return texto.replace(ruta_termux, "~")

    @staticmethod
    def obtener_ultimos_logs(n_lineas: int = 10) -> str:
        log_path = Path("logs/shadow_grimorio.log")
        if log_path.exists():
            try:
                with open(log_path, "r") as f:
                    lineas = f.readlines()
                    # Solo enviamos logs si no son demasiado masivos
                    resumen = "".join(lineas[-n_lineas:])
                    return resumen if len(resumen) < 1000 else resumen[:1000] + "... [LOG CORTADO]"
            except: pass
        return "No hay telemetría disponible."

    @staticmethod
    def obtener_contexto_completo(agente_id: str = None, query_usuario: str = "") -> str:
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            alias = user.alias if user else "ShadowRoot07"

            # 1. NÚCLEO DE PERSONALIDAD
            prompt = (
                "### SISTEMA OPERATIVO: SHADOW_GRIMORIO ###\n"
                "- IDIOMA: ESPAÑOL (ESTRICTO).\n"
                "- MODO: Cyberpunk, pragmático, sombra.\n\n"
            )

            # 2. IDENTIDAD DINÁMICA
            if agente_id and agente_id.upper() in AGENT_IDENTITIES:
                info = AGENT_IDENTITIES[agente_id.upper()]
                prompt += f"[AGENTE ACTIVO: {agente_id.upper()}]\n"
                prompt += f"ROL: {info.get('prompt', 'Asistente de ejecución.')}\n"
                prompt += f"RASGO: {info.get('trait', 'Eficiencia pura.')}\n\n"
            else:
                prompt += f"ERES EL NÚCLEO CENTRAL DEL ENJAMBRE DE {alias.upper()}.\n\n"

            # 3. GHOST_SHELL (LECTURA INTELIGENTE DE ARCHIVOS)
            # Solo leemos si el archivo es pequeño para evitar Error 400
            for palabra in query_usuario.split():
                if "/" in palabra or "." in palabra:
                    path_candidato = palabra.strip("., \"'`")
                    p = Path(path_candidato)
                    if p.exists() and p.is_file():
                        # Límite de seguridad: 2KB por archivo
                        if p.stat().st_size < 2048: 
                            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                                prompt += f"\n[FILE_READ: {p.name}]\n{f.read()}\n"
                        else:
                            prompt += f"\n[AVISO: Archivo {p.name} es demasiado grande para inyectar]\n"

            # 4. TELEMETRÍA (Reducida para ahorrar tokens)
            prompt += f"\n--- LOGS_SISTEMA ---\n{ContextInjector.obtener_ultimos_logs(5)}"

            return ContextInjector.filtrar_privacidad(prompt)

        except Exception as e:
            logger.error(f"Fallo crítico en Inyector: {e}")
            return "CONTEXTO_DAÑADO: Responde solo en español."
        finally:
            session.close()

