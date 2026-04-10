from src.database.manager import db
from src.logic.ghost_shell import ghost
from src.logic.config import config
import os

# 1. Forzar inicialización manual
print(f"Usando llave: {config.encryption_key[:5]}...")
ghost.setup_key(config.encryption_key)

# 2. Intentar guardar
print("Guardando secreto...")
db.save_secret("DEBUG_KEY", "valor_secreto_zte")

# 3. Intentar leer inmediatamente
recuperado = db.get_secret("DEBUG_KEY")
print(f"Recuperado: {recuperado}")

if recuperado == "valor_secreto_zte":
    print("✅ ¡SISTEMA OPERATIVO!")
else:
    print("❌ ALGO FALLÓ.")

