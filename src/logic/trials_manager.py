import hashlib
import time
from src.database.manager import db
from src.database.models import Usuario
from src.utils.hardware import generar_huella_hardware

class TrialsManager:
    """Orquestador de las Pruebas de Iniciación (Protocolo SAP)."""

    def __init__(self):
        self.start_time = 0

    def registrar_inicio_input(self):
        self.start_time = time.time()

    def es_humano(self, texto: str) -> bool:
        """Detecta si el input fue pegado (IA/Copy-Paste) por velocidad."""
        duracion = time.time() - self.start_time
        palabras = len(texto.split())
        # Si escribe más de 150 palabras por minuto, es sospechoso
        wpm = (palabras / duracion) * 60 if duracion > 0 else 999
        return wpm < 150

    def guardar_progreso(self, fase: int, repeticion: int = 0, respuestas_hash: str = ""):
        session = db.get_session()
        user = session.query(Usuario).first()
        if user:
            user.rango = f"Prueba Fase {fase} (Rep: {repeticion})"
            # Usaremos un campo temporal o el alias para guardar el estado del bucle
            # Por ahora, actualizamos el rango para reflejar el progreso
            session.commit()
        session.close()

    def finalizar_pruebas(self, k1: str, k2: str, k3: str):
        """Genera la Super Key y sella el perfil."""
        from src.logic.identity_matrix import sap
        super_k = sap.generar_super_key(k1, k2, k3)
        
        session = db.get_session()
        user = session.query(Usuario).first()
        if user:
            user.pruebas_completadas = True
            user.rango = "Arquitecto Maestro"
            user.key_hash_1 = k1
            user.key_hash_2 = k2
            user.key_hash_3 = k3
            user.super_key_hash = super_k
            user.hw_fingerprint = generar_huella_hardware()
            session.commit()
        session.close()

trials = TrialsManager()

