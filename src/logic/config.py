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

    # --- API Keys y Seguridad (Mapeo explícito) ---
    groq_api_key: SecretStr = Field(alias="GROQ_API_KEY")
    github_token: SecretStr = Field(alias="GITHUB_TOKEN")
    encryption_key: str = Field(default="", alias="ENCRYPTION_KEY")

    # --- Rutas y Base de Datos ---
    database_url: str = "sqlite:///./data/shadow_local.db"
    sounds_path: str = "./assets/sounds"

    # --- Integración ---
    github_username: str = "ShadowRoot07"

    # --- Parámetros de Cortesía (IA) ---
    groq_model: str = "llama3-70b-8192"
    groq_timeout: int = 30
    groq_cooldown: int = 2
    groq_retry_limit: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False # Para evitar errores de mayúsculas en el .env
    )

    def get_cipher(self):
        try:
            if not self.encryption_key:
                return None
            return Fernet(self.encryption_key.encode())
        except Exception as e:
            logger.error(f"⚠️ [CIFRADO]: Llave maestra inválida: {e}")
            return None

    def guardar_tema(self, nuevo_tema: str):
        """Actualiza el tema en memoria y persiste si es necesario."""
        self.shadow_theme = nuevo_tema
        # Opcional: Escribir de vuelta al .env o DB aquí

config = Settings()

