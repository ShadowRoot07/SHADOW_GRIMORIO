from src.database.manager import db
from src.logic.ghost_shell import init_ghost
from src.logic.config import config

init_ghost(config.encryption_key)
secreto = db.get_secret("TEST_KEY")
print(f"--- 🔓 TEST DE REVELACIÓN ---")
print(f"Valor recuperado: {secreto}")

