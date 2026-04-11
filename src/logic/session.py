from src.logic.vault import vault
from src.logic.identity_matrix import sap
from loguru import logger

class SessionManager:
    """Controla el estado de autenticación en la sesión actual."""
    
    _authenticated = False

    @classmethod
    def login(cls, k2: str, k3: str) -> bool:
        """Intenta validar la sesión usando las llaves proporcionadas."""
        stored_super_key = vault.get_secret("SUPER_KEY_HASH")
        k1 = vault.get_secret("K1_HARDWARE")
        
        if not stored_super_key or not k1:
            logger.error("🚨 SESSION: No se encontró un perfil sellado.")
            return False
            
        # Generamos el hash con lo que el usuario acaba de meter
        current_hash = sap.generar_super_key(k1, k2, k3)
        
        if current_hash == stored_super_key:
            cls._authenticated = True
            logger.success("🔓 SESSION: Acceso concedido.")
            return True
        
        logger.warning("🔒 SESSION: Intento de acceso fallido.")
        return False

    @classmethod
    def is_active(cls) -> bool:
        return cls._authenticated

    @classmethod
    def logout(cls):
        cls._authenticated = False

