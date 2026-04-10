from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field
from cryptography.fernet import Fernet
from loguru import logger
from pathlib import Path
import os

class Settings(BaseSettings):
    # --- Identidad y Core ---
    shadow_alias: str = "ShadowRoot07"
    shadow_env: str = "development"
    shadow_theme: str = "CYBERPUNK"

    # --- API Keys (Ahora pueden venir cifradas o del entorno) ---
    groq_api_key: str = Field(alias="GROQ_API_KEY")
    github_token: str = Field(alias="GITHUB_TOKEN")
    encryption_key: str = Field(default="", alias="ENCRYPTION_KEY")

    # --- Rutas ---
    database_url: str = "sqlite:///./data/shadow_local.db"
    sounds_path: str = "./assets/sounds"
    lexicon_path: Path = Path("./logs/lexicon_index.json")

    # --- Integración ---
    github_username: str = "ShadowRoot07"

    # --- IA Config ---
    groq_model: str = "llama-3.3-70b-versatile"
    groq_timeout: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    def validate_security(self):
        """Verifica que la llave de cifrado sea robusta."""
        if not self.encryption_key or len(self.encryption_key) < 32:
            logger.critical("🚨 GHOST_SHELL: ENCRYPTION_KEY no detectada o demasiado corta.")
            return False
        return True

config = Settings()

