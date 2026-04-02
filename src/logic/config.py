from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field
from cryptography.fernet import Fernet
from loguru import logger
from pathlib import Path

class Settings(BaseSettings):
    # --- Identidad y Core ---
    shadow_alias: str = "ShadowRoot07"
    shadow_env: str = "development"
    shadow_theme: str = "CYBERPUNK"

    # --- API Keys y Seguridad ---
    groq_api_key: SecretStr = Field(alias="GROQ_API_KEY")
    github_token: SecretStr = Field(alias="GITHUB_TOKEN")
    encryption_key: str = Field(default="", alias="ENCRYPTION_KEY")

    # --- Rutas ---
    database_url: str = "sqlite:///./data/shadow_local.db"
    sounds_path: str = "./assets/sounds"
    # Ruta al índice para que otros módulos lo encuentren fácil
    lexicon_path: Path = Path("./logs/lexicon_index.json")

    # --- Integración ---
    github_username: str = "ShadowRoot07"

    # --- Parámetros de Cortesía (IA) ---
    # FIX: Cambiado a Llama 3.3 (El 3-70b-8192 ya no existe en Groq)
    groq_model: str = "llama-3.3-70b-versatile"
    groq_timeout: int = 30
    groq_cooldown: int = 2
    groq_retry_limit: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    def get_cipher(self):
        try:
            if not self.encryption_key: return None
            return Fernet(self.encryption_key.encode())
        except Exception as e:
            logger.error(f"⚠️ [CIFRADO]: Llave maestra inválida: {e}")
            return None

config = Settings()

