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
    def obtener_conocimiento_personal() -> str:
        """Recupera hechos guardados sobre el usuario."""
        from src.database.models import Conocimiento
        session = db.get_session(force_local=True)
        try:
            hechos = session.query(Conocimiento).all()
            if not hechos:
                return "No hay registros de conocimiento personal."
            
            resumen = ["[NÚCLEO_DE_CONOCIMIENTO]"]
            for h in hechos:
                resumen.append(f"• {h.categoria}[{h.llave}]: {h.valor}")
            return "\n".join(resumen)
        except Exception as e:
            return f"Error en Bóveda de Conocimiento: {e}"
        finally:
            session.close()

    @staticmethod
    def obtener_memoria_proyectos(n: int = 5) -> str:
        from src.database.models import HitoHistorial
        session = db.get_session(force_local=True)
        try:
            hitos = session.query(HitoHistorial).order_by(HitoHistorial.fecha.desc()).limit(n).all()
            if not hitos:
                return "No hay hitos registrados."

            memoria = ["[HISTORIAL_RECIENTE]"]
            for h in reversed(hitos): # Invertimos para que el más reciente sea el último que lea
                memoria.append(f"USR: {h.prompt_usuario}") # <--- Quitamos el recorte
                memoria.append(f"IA: {h.respuesta_ia}")   # <--- Quitamos el recorte
            return "\n".join(memoria)
        except Exception as e:
            return "Error al acceder a la memoria."
        finally:
            session.close()

    @staticmethod
    def obtener_contexto_completo(agente_id: str = None, query_usuario: str = "") -> str:
        session = db.get_session(force_local=True) 

        # Inicialización de seguridad para evitar NameError
        alias = "ShadowRoot07"
        rango_nombre = "Iniciado"

        try:
            user = session.query(Usuario).first()
            if user:
                alias = user.alias
                # Extraemos el nombre del rango desde la relación
                if user.rango_rel:
                    rango_nombre = user.rango_rel.nombre

            prompt = "### NÚCLEO_SPICA_V3 ###\n"
            prompt += "PERSONALIDAD: Fría, técnica, eficiente. Estilo Cyberpunk.\n"
            prompt += "IDENTIDAD_SISTEMA: Oráculo del Shadow_Grimorio.\n"
            prompt += f"OPERADOR: {alias.upper()} | RANGO: {rango_nombre.upper()}\n\n"

            # MEMORIA: Usamos la función que ya tiene force_local=True
            prompt += f"{ContextInjector.obtener_memoria_proyectos(5)}\n\n"

            # 2. CONOCIMIENTO LOCAL (Archivos y Lexicon)
            prompt += f"### MAPA_LÉXICO ###\n{ContextInjector.obtener_mapa_lexico()}\n\n"
            prompt += "- IDIOMA: ESPAÑOL (ESTRICTO)\n"
            prompt += f"{ContextInjector.obtener_conocimiento_personal()}\n\n"
        
            # INYECCIÓN DE HISTORIAL
            prompt += f"{ContextInjector.obtener_memoria_proyectos(5)}\n\n"

            # 3. MODO DE OPERACIÓN
            if agente_id and agente_id.upper() in AGENT_IDENTITIES:
                info = AGENT_IDENTITIES[agente_id.upper()]
                prompt += f"[MODO_AGENTE: {agente_id.upper()}]\n"
                prompt += f"OBJETIVO: {info.get('prompt', 'Asistente técnico.')}\n"

                                # --- INYECCIÓN CRÍTICA PARA SPICA ---
                if agente_id.upper() == "SPICA":
                    prompt += "\n[PROTOCOLO_ARCHITECT_ACTIVO]\n"
                    prompt += "Si el usuario pide crear/editar código, genera un bloque JSON puro al final de tu respuesta:\n"
                    prompt += 'CREAR: {"folders": ["path/"], "files": [{"path": "file.py", "content": "..."}]}\n'
                    prompt += 'EDITAR: {"patches": [{"path": "file.py", "search": "old", "replace": "new"}]}\n'
            else:
                # Fallback para el oráculo general
                prompt += "MODO: ORÁCULO CENTRAL.\n"
                prompt += "REGLA: Si el usuario pide construir, usa el formato JSON del ARCHITECT.\n"
                prompt += "REGLA: Responde con precisión quirúrgica. Si el usuario pide crear o construir, "
                prompt += "puedes sugerir estructuras JSON para el ARCHITECT.\n"

            # 4. GHOST_SHELL (Lectura de archivos mencionados en el chat)
            for palabra in query_usuario.split():
                if "/" in palabra or "." in palabra:
                    path_candidato = palabra.strip("., \"'`")
                    p = Path(path_candidato)
                    if p.exists() and p.is_file():
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
