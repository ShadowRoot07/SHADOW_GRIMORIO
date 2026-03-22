from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from cryptography.fernet import Fernet
from loguru import logger

class Settings(BaseSettings):
    # --- Identidad y Core ---
    shadow_alias: str = "ShadowRoot07"
    shadow_env: str = "development"
    shadow_theme: str = "CYBERPUNK"

    # --- API Keys y Seguridad ---
    groq_api_key: SecretStr
    github_token: SecretStr
    encryption_key: str = "" # Cambiado a str para manejo de errores manual

    # --- Rutas y Base de Datos ---
    database_url: str = "sqlite:///./data/shadow_local.db"
    sounds_path: str = "./assets/sounds"

    # --- Integración ---
    github_username: str = "ShadowRoot07"

    # --- Parámetros de Cortesía (IA) ---
    groq_model: str = "llama3-8b-8192"
    groq_timeout: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_cipher(self):
        """Retorna el objeto Fernet de forma segura. Si falla, retorna None."""
        try:
            if not self.encryption_key:
                return None
            return Fernet(self.encryption_key.encode())
        except Exception as e:
            logger.error(f"⚠️ [CIFRADO]: Llave maestra inválida: {e}")
            return None

    def guardar_tema(self, nuevo_tema: str):
        self.shadow_theme = nuevo_tema

config = Settings()

