import os
import shutil
from pathlib import Path
from cryptography.fernet import Fernet
from loguru import logger

class GhostShell:
    """Protocolo de Invisibilidad y Seguridad de Datos."""

    def __init__(self, key: str = None):
        self.raiz = Path(__file__).resolve().parents[2]
        self.temp_dir = self.raiz / "logs" / "session_temp"
        self.cipher = None
        
        # Si se pasa una llave al instanciar, configurar el cifrado
        if key:
            self.setup_key(key)

    def setup_key(self, key: str):
        """Configura o actualiza la llave Maestra de Fernet."""
        try:
            if not key:
                logger.warning("⚠️ GHOST_SHELL: Se intentó configurar una llave vacía.")
                return
            self.cipher = Fernet(key.encode())
            logger.debug("🔐 GHOST_SHELL: Llave configurada correctamente.")
        except Exception as e:
            self.cipher = None
            logger.error(f"❌ GHOST_SHELL: Llave maestra inválida o corrupta: {e}")

    def obfuscate_data(self, plain_text: str) -> str:
        """Cifra un dato para almacenamiento persistente."""
        if not self.cipher: 
            return plain_text
        return self.cipher.encrypt(plain_text.encode()).decode()

    def reveal_data(self, encrypted_text: str) -> str:
        """Descifra un dato solo cuando es necesario."""
        if not self.cipher: 
            return encrypted_text
        try:
            return self.cipher.decrypt(encrypted_text.encode()).decode()
        except Exception:
            logger.error("❌ GHOST_SHELL: Error al descifrar. ¿Llave incorrecta?")
            return "ERROR_DE_DESCIFRADO"

    def burn_session(self):
        """Elimina rastros temporales y limpia logs sensibles."""
        if not self.temp_dir.exists():
            return

        logger.warning(f"🔥 GHOST_SHELL: Purgando {self.temp_dir}...")
        try:
            # Borrar contenido del directorio temporal
            for item in self.temp_dir.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)
            logger.success("🧹 GHOST_SHELL: Rastros de sesión eliminados.")
        except Exception as e:
            logger.error(f"⚠️ GHOST_SHELL: Error durante la purga: {e}")

# --- INSTANCIA GLOBAL Y FUNCIONES DE APOYO ---

# Creamos una instancia inicial 'vacía'
ghost = GhostShell()

def init_ghost(key: str):
    """
    Función de compatibilidad para inicializar el fantasma global.
    Utilizada por main.py y scripts de migración.
    """
    global ghost
    ghost.setup_key(key)
    # Limpieza preventiva al iniciar
    ghost.burn_session()

