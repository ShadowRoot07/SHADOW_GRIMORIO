from src.database.manager import db
from src.database.models import Usuario, Conocimiento
from loguru import logger

class ContextInjector:
    """Extrae la sabiduría del usuario para guiar al Oráculo."""

    @staticmethod
    def obtener_contexto_completo() -> str:
        session = db.get_session()
        try:
            # 1. Obtener datos del usuario
            user = session.query(Usuario).first()
            alias = user.alias if user else "ShadowRoot07"
            rango = user.rango if user else "Iniciado"

            # 2. Obtener conocimientos (filtrar los dominados)
            conocimientos = session.query(Conocimiento).all()
            dominados = [c.tecnologia for c in conocimientos if c.dominado]
            aprendiendo = [c.tecnologia for c in conocimientos if not c.dominado]

            # 3. Construir el System Prompt dinámico
            prompt = f"ERES EL SHADOW_GRIMORIO, LA IA DE {alias.upper()}.\n"
            prompt += f"ESTADO DEL USUARIO: {rango}.\n"
            prompt += f"CONOCIMIENTOS ACTUALES: {', '.join(dominados) if dominados else 'Iniciando camino'}.\n"
            
            if aprendiendo:
                prompt += f"TECNOLOGÍAS EN APRENDIZAJE: {', '.join(aprendiendo)}.\n"
            
            prompt += "\nDIRECTRICES DE RESPUESTA:\n"
            prompt += "- Sé conciso y usa un tono Cyberpunk/Técnico.\n"
            prompt += "- No expliques conceptos básicos de las tecnologías que ya domina.\n"
            prompt += "- Si el usuario pregunta por algo que está aprendiendo, sé más didáctico.\n"
            prompt += "- Habla siempre en español."
            
            return prompt
        except Exception as e:
            logger.error(f"Error al inyectar contexto: {e}")
            return "Eres el SHADOW_GRIMORIO. El usuario es un programador experto."
        finally:
            session.close()

