from src.database.manager import db
from src.logic.ghost_shell import init_ghost
from src.logic.config import config

# Necesitamos inicializar el fantasma para que tenga la llave
init_ghost(config.encryption_key)

print("--- 🔐 TEST DE CIFRADO ---")
db.save_secret("TEST_KEY", "shadow_root_secret_123")
print("Secreto guardado.")

