import time
from src.database.manager import db
from src.database.models import Usuario
from src.logic.utils import limpiar_secuencias_ansi # Importamos el filtro

class PhaseOneManager:
    """Juez mecánico para la Fase 1: Caracteres, Tiempo y Paciencia."""

    def __init__(self):
        self.start_time = 0
        self.challenges = [
            {"id": 1, "task": "Crea un Hello World en Python.", "max_chars": 30, "min_chars": 10},
            {"id": 2, "task": "Crea una calculadora básica (suma) en Python.", "max_chars": 60, "min_chars": 15},
            {"id": 3, "task": "Crea un formulario con input() en Python.", "max_chars": 80, "min_chars": 20},
            {"id": 4, "task": "Pregunta Web: ¿Qué es un Protocolo? (Respuesta Humana)", "max_chars": 120, "min_chars": 15}
        ]

    def registrar_inicio(self):
        self.start_time = time.time()

    def es_humano(self, texto: str) -> bool:
        """Evita copy-paste masivo evaluando caracteres por segundo."""
        duracion = time.time() - self.start_time
        # Tolerancia ajustada para TextArea: menos de 0.3s para > 10 chars es bot.
        if duracion < 0.3 and len(texto.strip()) > 10: return False
        return True

    def validar_respuesta(self, texto: str, step: int) -> bool:
        """Valida longitud de caracteres tras limpiar basura de la terminal."""
        # APLICAMOS EL FILTRO AQUÍ:
        texto_puro = limpiar_secuencias_ansi(texto)
        texto_limpio = texto_puro.strip()
        
        ch = next((c for c in self.challenges if c['id'] == step), None)
        if not ch: return False

        # El conteo ahora es real, sin bytes fantasma de Termux
        longitud_ok = ch['min_chars'] <= len(texto_limpio) <= ch['max_chars']
        humano_ok = self.es_humano(texto_limpio)

        return longitud_ok and humano_ok

    def guardar_progreso_db(self, step: int, paciencia: int = 0):
        session = db.get_session()
        user = session.query(Usuario).first()
        if user:
            # USAMOS EL CAMPO CORRECTO
            user.progreso_trials = f"F1_S{step}_P{paciencia}"
            session.commit()
        session.close()

    def obtener_progreso_db(self):
        session = db.get_session()
        user = session.query(Usuario).first()
        status = {"step": 1, "paciencia": 0}
        
        # LEEMOS DEL CAMPO CORRECTO
        if user and user.progreso_trials and user.progreso_trials.startswith("F1_"):
            try:
                parts = user.progreso_trials.split("_")
                status["step"] = int(parts[1][1:])
                status["paciencia"] = int(parts[2][1:])
            except: 
                logger.error("Error parseando progreso_trials")
        session.close()
        return status

    def finalizar_fase_uno(self):
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            if user:
                # Marcamos el hito en el string de progreso
                user.progreso_trials = "F1_COMPLETADA"
                # IMPORTANTE: NO pongas pruebas_completadas = True aquí 
                # a menos que quieras saltarte la Fase 2 y 3.
                session.commit()
                logger.success("Fase 1 sellada.")
        finally:
            session.close()


trials_logic = PhaseOneManager()

