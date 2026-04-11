from src.logic.identity_matrix import sap
from src.database.manager import db
from src.database.models import Usuario
from loguru import logger

class LazaroProtocol:
    """Protocolo de recuperación y validación de integridad de sesión."""
    
    @staticmethod
    def validar_integridad_hardware():
        """Verifica si el Grimorio está corriendo en el dispositivo original (ZTE)."""
        session = db.get_session()
        user = session.query(Usuario).first()
        
        if not user:
            session.close()
            return False
            
        current_hw = sap.hw_fingerprint
        if user.hw_fingerprint != current_hw:
            logger.critical("🚨 VIOLACIÓN DE HARDWARE: Este Grimorio no pertenece a este dispositivo.")
            session.close()
            return False
            
        session.close()
        return True

    @staticmethod
    def despertar_agentes(manager):
        """Si la integridad es correcta, despierta a los agentes necesarios."""
        if LazaroProtocol.validar_integridad_hardware():
            logger.info("🕯️ Protocolo Lázaro: Integridad de hardware confirmada.")
            # Por defecto, solo despertamos al Watchdog y Bruma para seguridad
            manager.encender_agente("watchdog")
            manager.encender_agente("bruma_sync")
            return True
        return False

lazaro = LazaroProtocol()

