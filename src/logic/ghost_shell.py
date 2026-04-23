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
        # Asegurar que el directorio existe para evitar errores de ruta
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.cipher = None
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
        """Elimina rastros temporales y limpia logs sensibles de forma segura."""
        if not self.temp_dir.exists():
            return

        logger.warning(f"🔥 GHOST_SHELL: Purgando {self.temp_dir}...")
        try:
            for item in self.temp_dir.iterdir():
                try:
                    if item.is_file():
                        # Verificación de existencia inmediata antes de borrar
                        if item.exists():
                            item.unlink(missing_ok=True)
                    elif item.is_dir():
                        if item.exists():
                            shutil.rmtree(item, ignore_errors=True)
                except (PermissionError, OSError) as e:
                    # Capturamos el warning de IO sin romper el flujo
                    logger.debug(f"⏳ GHOST_SHELL: Archivo {item.name} ocupado, saltando...")
            
            logger.success("🧹 GHOST_SHELL: Rastros de sesión eliminados.")
        except Exception as e:
            logger.error(f"⚠️ GHOST_SHELL: Error crítico durante la purga: {e}")

# --- INSTANCIA GLOBAL ---
ghost = GhostShell()

def init_ghost(key: str):
    global ghost
    ghost.setup_key(key)
    ghost.burn_session()

