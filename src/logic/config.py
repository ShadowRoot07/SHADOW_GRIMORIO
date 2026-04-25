import os
import yaml
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from cryptography.fernet import Fernet
from loguru import logger

# --- ANCLAJE DE RAÍZ ABSOLUTO ---
# Detecta la ubicación de este archivo y sube dos niveles (src/logic -> raíz)
BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    # Definimos rutas absolutas dinámicas
    base_dir: Path = BASE_DIR
    shadow_alias: str = "ShadowRoot07"
    shadow_env: str = "development"
    shadow_theme: str = "CYBERPUNK"
    
    # Rutas blindadas
    database_url: str = f"sqlite:///{BASE_DIR}/data/shadow_local.db"
    sounds_path: Path = BASE_DIR / "assets" / "sounds"
    lexicon_path: Path = BASE_DIR / "logs" / "lexicon_index.json"
    
    github_username: str = "ShadowRoot07"
    groq_model: str = "llama-3.3-70b-versatile"
    groq_timeout: int = 30
    groq_cooldown: int = 2
    groq_retry_limit: int = 3

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    github_token: str = Field(default="", alias="GITHUB_TOKEN")
    encryption_key: str = Field(default="", alias="ENCRYPTION_KEY")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"), # Ruta absoluta al .env
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True 
    )

    def _get_cipher(self):
        if not self.encryption_key:
            raise ValueError("No existe ENCRYPTION_KEY en el entorno.")
        return Fernet(self.encryption_key.encode())

    def encrypt_value(self, plain_text: str) -> str:
        cipher = self._get_cipher()
        return cipher.encrypt(plain_text.encode()).decode()

    def decrypt_value(self, encrypted_text: str) -> str:
        try:
            cipher = self._get_cipher()
            return cipher.decrypt(encrypted_text.encode()).decode()
        except Exception:
            logger.error("❌ GHOST_SHELL: Fallo al descifrar secreto.")
            return ""

    def save_to_yaml(self):
        """Guarda la configuración en config.yaml en la raíz absoluta."""
        exclude_fields = {'groq_api_key', 'github_token', 'encryption_key', 'database_url'}
        data = self.model_dump(exclude=exclude_fields)
        
        # Convertir Paths a strings para YAML
        data['lexicon_path'] = str(self.lexicon_path)
        data['base_dir'] = str(self.base_dir)
        data['sounds_path'] = str(self.sounds_path)

        config_path = self.base_dir / "config.yaml"
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            logger.success(f"📁 Configuración sincronizada en {config_path}")
        except Exception as e:
            logger.error(f"Error al guardar config.yaml: {e}")

    def validate_security(self):
        if not self.encryption_key or len(self.encryption_key) < 32:
            logger.critical("🚨 GHOST_SHELL: ENCRYPTION_KEY no detectada o inválida.")
            return False
        return True

config = Settings()

