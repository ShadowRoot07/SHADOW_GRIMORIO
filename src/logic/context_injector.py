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
        # Usamos ruta absoluta para evitar fallos desde diferentes pantallas
        base_path = Path(__file__).resolve().parents[2]
        index_path = base_path / "logs" / "lexicon_index.json"
        
        if index_path.exists():
            try:
                with open(index_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                resumen = ["[ESTRUCTURA_PROYECTO_ACTUAL]"]
                for file, items in data.items():
                    resumen.append(f"- {file}: {', '.join(items)}")
                
                # Límite de 1500 caracteres es el 'sweet spot' para Llama 3 8B en móvil
                return "\n".join(resumen)[:1500] 
            except Exception as e:
                logger.warning(f"Error leyendo Lexicon: {e}")
        return "No hay mapa léxico disponible aún. Ejecuta el agente LEXICON_INDEXER."

    @staticmethod
    def obtener_ultimos_logs(n: int = 5) -> str:
        """Extrae las últimas líneas de actividad para contexto situacional."""
        log_path = Path("logs/daemon_survival.log")
        if log_path.exists():
            try:
                with open(log_path, "r") as f:
                    lines = f.readlines()
                    return "".join(lines[-n:])
            except: pass
        return "Sin eventos recientes."

    @staticmethod
    def obtener_contexto_completo(agente_id: str = None, query_usuario: str = "") -> str:
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            alias = user.alias if user else "ShadowRoot07"

            # 1. CONOCIMIENTO LOCAL (Lexicon)
            prompt = f"### CONOCIMIENTO_LOCAL ###\n{ContextInjector.obtener_mapa_lexico()}\n\n"

            # 2. PERSONALIDAD Y ENTORNO
            prompt += (
                "### SISTEMA OPERATIVO: SHADOW_GRIMORIO ###\n"
                f"- USUARIO: {alias.upper()}\n"
                "- IDIOMA: ESPAÑOL (ESTRICTO)\n"
                "- HARDWARE: ZTE Blade A54 (Termux)\n\n"
            )

            # 3. IDENTIDAD DINÁMICA
            if agente_id and agente_id.upper() in AGENT_IDENTITIES:
                info = AGENT_IDENTITIES[agente_id.upper()]
                prompt += f"[MODO_AGENTE: {agente_id.upper()}]\n"
                prompt += f"OBJETIVO: {info.get('prompt', 'Asistente técnico.')}\n\n"
            else:
                prompt += "ERES EL NÚCLEO CENTRAL. Gestiona el enjambre de agentes con precisión.\n\n"

            # 4. GHOST_SHELL (Lectura de archivos mencionados en el chat)
            for palabra in query_usuario.split():
                if "/" in palabra or "." in palabra:
                    path_candidato = palabra.strip("., \"'`")
                    p = Path(path_candidato)
                    if p.exists() and p.is_file():
                        # Límite de seguridad para no explotar la memoria del ZTE
                        if p.stat().st_size < 4096:
                            try:
                                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                                    prompt += f"\n[CONTENIDO_ARCHIVO: {p.name}]\n{f.read()}\n"
                            except: pass

            # 5. ESTADO DEL HARDWARE (Vía Logs de Survival)
            prompt += f"\n### ESTADO_SISTEMA ###\n{ContextInjector.obtener_ultimos_logs(3)}"

            return ContextInjector.filtrar_privacidad(prompt)

        except Exception as e:
            logger.error(f"Fallo en Inyector: {e}")
            return "ERROR_CONTEXTO: Responde como núcleo Shadow Grimorio."
        finally:
            session.close()

