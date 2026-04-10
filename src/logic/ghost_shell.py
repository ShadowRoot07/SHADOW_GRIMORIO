import os
import shutil
from pathlib import Path
from cryptography.fernet import Fernet
from loguru import logger

class GhostShell:
    def __init__(self, key: str = None):
        self.raiz = Path(__file__).resolve().parents[2]
        self.temp_dir = self.raiz / "logs" / "session_temp"
        self.cipher = None
        if key:
            self.setup_key(key)

    def setup_key(self, key: str):
        try:
            self.cipher = Fernet(key.encode())
        except Exception as e:
            logger.error(f"❌ GHOST_SHELL: Llave inválida: {e}")

    def obfuscate_data(self, plain_text: str) -> str:
        if not self.cipher: return plain_text
        return self.cipher.encrypt(plain_text.encode()).decode()

    def reveal_data(self, encrypted_text: str) -> str:
        if not self.cipher: return encrypted_text
        try:
            return self.cipher.decrypt(encrypted_text.encode()).decode()
        except Exception:
            return "ERROR_DE_DESCIFRADO"

    def burn_session(self):
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            logger.success("🧹 GHOST_SHELL: Sesión purgada.")

# Instancia única para todo el sistema
ghost = GhostShell()

