import os
import json
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
    def obtener_mapa_lexico() -> str:
        """Lee el índice de funciones y clases generado por el agente LEXICON."""
        index_path = Path("logs/lexicon_index.json")
        if index_path.exists():
            try:
                with open(index_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Resumimos para no saturar tokens (solo nombres de archivos y lo que contienen)
                    resumen = []
                    for file, items in data.items():
                        resumen.append(f"{file}: {', '.join(items)}")
                    return "\n".join(resumen)[:1000] # Límite de 1k caracteres
            except: pass
        return "No hay mapa léxico disponible aún."

    @staticmethod
    def obtener_contexto_completo(agente_id: str = None, query_usuario: str = "") -> str:
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            alias = user.alias if user else "ShadowRoot07"

            # 1. MAPA LÉXICO (Máxima prioridad: Al inicio del todo)
            # Esto le dice a la IA qué archivos existen antes de definir su personalidad.
            prompt = f"### [MEMORIA_LOCAL_DE_ARCHIVOS] ###\n{ContextInjector.obtener_mapa_lexico()}\n\n"

            # 2. NÚCLEO DE PERSONALIDAD
            prompt += (
                "### SISTEMA OPERATIVO: SHADOW_GRIMORIO ###\n"
                "- IDIOMA: ESPAÑOL (ESTRICTO).\n"
                "- MODO: Cyberpunk, pragmático, sombra.\n"
                "- ACCESO: Tienes permiso para leer la estructura de archivos mencionada arriba.\n\n"
            )

            # 3. IDENTIDAD DINÁMICA
            if agente_id and agente_id.upper() in AGENT_IDENTITIES:
                info = AGENT_IDENTITIES[agente_id.upper()]
                prompt += f"[AGENTE ACTIVO: {agente_id.upper()}]\n"
                prompt += f"ROL: {info.get('prompt', 'Asistente de ejecución.')}\n"
                prompt += f"RASGO: {info.get('trait', 'Eficiencia pura.')}\n\n"
            else:
                prompt += f"ERES EL NÚCLEO CENTRAL DEL ENJAMBRE DE {alias.upper()}.\n\n"

            # 4. GHOST_SHELL (LECTURA DINÁMICA)
            # Mantenemos tu lógica de split() que es muy eficiente en móvil
            for palabra in query_usuario.split():
                if "/" in palabra or "." in palabra:
                    path_candidato = palabra.strip("., \"'`")
                    p = Path(path_candidato)
                    if p.exists() and p.is_file():
                        if p.stat().st_size < 2048:
                            with open(p, "r", encoding="utf-8", errors="ignore") as f:
                                prompt += f"\n[CONTENIDO_DE_ARCHIVO: {p.name}]\n{f.read()}\n"
                        else:
                            prompt += f"\n[AVISO: {p.name} excedió los 2KB y no fue inyectado]\n"

            # 5. TELEMETRÍA (Final del prompt para contexto reciente)
            prompt += f"\n--- ÚLTIMOS_EVENTOS_DEL_SISTEMA ---\n{ContextInjector.obtener_ultimos_logs(5)}"

            return ContextInjector.filtrar_privacidad(prompt)

        except Exception as e:
            logger.error(f"Fallo crítico en Inyector: {e}")
            return "CONTEXTO_DAÑADO: Responde solo en español."
        finally:
            session.close()

