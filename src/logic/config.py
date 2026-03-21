from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    # Definimos las mismas variables del .env
    shadow_alias: str = "Shadow"
    groq_api_key: SecretStr
    database_url: str = "sqlite:///./data/shadow_local.db"
    github_token: SecretStr
    
    # Configuración para leer el archivo .env
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Instancia global para usar en todo el proyecto
config = Settings()

