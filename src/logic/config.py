from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    # --- Identidad y Core ---
    shadow_alias: str = "ShadowRoot07"
    shadow_env: str = "development"
    
    # --- API Keys y Seguridad ---
    groq_api_key: SecretStr
    github_token: SecretStr
    encryption_key: SecretStr  # Detectada en el error
    
    # --- Rutas y Base de Datos ---
    database_url: str = "sqlite:///./data/shadow_local.db"
    sounds_path: str = "./assets/sounds"  # Detectada en el error
    
    # --- Integración ---
    github_username: str = "ShadowRoot07" # Detectada en el error

    # --- Parámetros de Cortesía (IA) ---
    groq_model: str = "llama3-8b-8192"
    groq_timeout: int = 30
    groq_retry_limit: int = 3
    groq_cooldown: float = 0.5

    # Configuración del motor de Pydantic
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"  # <-- ESTA ES LA CLAVE: Ignora lo que no esté aquí arriba
    )

# Instancia global
config = Settings()

