import os
import yaml
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.fernet import Fernet
from loguru import logger

class Settings(BaseSettings):
    # --- Datos Públicos (Pueden ir en config.yaml) ---
    shadow_alias: str = "ShadowRoot07"
    shadow_env: str = "development"
    shadow_theme: str = "CYBERPUNK"
    database_url: str = "sqlite:///./data/shadow_local.db"
    sounds_path: str = "./assets/sounds"
    lexicon_path: Path = Path("./logs/lexicon_index.json")
    github_username: str = "ShadowRoot07"
    groq_model: str = "llama-3.3-70b-versatile"
    groq_timeout: int = 30
    groq_cooldown: int = 2
    groq_retry_limit: int = 3

    # --- Datos Sensibles (SÓLO en .env o Vault) ---
    # Usamos alias para mapear directamente desde el archivo .env
    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    encryption_key: str = Field(default="", alias="ENCRYPTION_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True # Permite usar el nombre del atributo o el alias
    )

    def save_to_yaml(self):
        """Guarda solo la configuración NO SENSIBLE en config.yaml."""
        # Campos a excluir para evitar fugas en GitHub
        exclude_fields = {
            'groq_api_key', 
            'github_token', 
            'encryption_key', 
            'database_url'
        }
        
        data = self.model_dump(exclude=exclude_fields)
        
        # Sanitizar Path para YAML limpio
        if 'lexicon_path' in data:
            data['lexicon_path'] = str(data['lexicon_path'])

        try:
            with open("config.yaml", "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            logger.success("✅ [SECURITY]: config.yaml actualizado sin secretos.")
        except Exception as e:
            logger.error(f"Error al guardar config.yaml: {e}")

    def _get_cipher(self):
        """Inicializa el motor de cifrado usando la llave maestra."""
        if not self.encryption_key:
            raise ValueError("No existe ENCRYPTION_KEY en el entorno.")
        return Fernet(self.encryption_key.encode())

    def encrypt_value(self, plain_text: str) -> str:
        """Cifra un dato sensible para guardarlo en disco."""
        cipher = self._get_cipher()
        return cipher.encrypt(plain_text.encode()).decode()

    def decrypt_value(self, encrypted_text: str) -> str:
        """Descifra un dato para usarlo en memoria."""
        try:
            cipher = self._get_cipher()
            return cipher.decrypt(encrypted_text.encode()).decode()
        except Exception:
            logger.error("❌ GHOST_SHELL: Fallo al descifrar secreto. ¿Llave maestra correcta?")
            return ""

    def save_to_yaml(self):
        """Guarda la configuración actual en config.yaml (menos la Master Key)."""
        data = self.model_dump(exclude={'encryption_key'})
        # Guardamos el archivo en la raíz del proyecto
        config_path = Path("config.yaml")
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            logger.success("📁 Configuración sincronizada en config.yaml")
        except Exception as e:
            logger.error(f"Error al guardar config.yaml: {e}")

    def validate_security(self):
        if not self.encryption_key or len(self.encryption_key) < 32:
            logger.critical("🚨 GHOST_SHELL: ENCRYPTION_KEY no detectada o inválida.")
            return False
        return True

config = Settings()

