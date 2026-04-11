import json
from pathlib import Path
from src.logic.config import config
from loguru import logger

class ShadowVault:
    """Caja fuerte para secretos persistentes en disco."""

    def __init__(self):
        self.vault_path = Path("data/shadow_vault.json")
        self.vault_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.vault_path.exists():
            self._write_vault({})

    def _read_vault(self) -> dict:
        try:
            with open(self.vault_path, "r") as f:
                return json.load(f)
        except: return {}

    def _write_vault(self, data: dict):
        with open(self.vault_path, "w") as f:
            json.dump(data, f, indent=4)

    def store_secret(self, key: str, value: str):
        """Cifra y guarda un secreto en la bóveda."""
        encrypted_val = config.encrypt_value(value)
        data = self._read_vault()
        data[key] = encrypted_val
        self._write_vault(data)
        logger.info(f"🔒 Secreto '{key}' sellado en la bóveda.")

    def get_secret(self, key: str) -> str:
        """Recupera y descifra un secreto de la bóveda."""
        data = self._read_vault()
        encrypted_val = data.get(key)
        if encrypted_val:
            return config.decrypt_value(encrypted_val)
        return ""

vault = ShadowVault()

