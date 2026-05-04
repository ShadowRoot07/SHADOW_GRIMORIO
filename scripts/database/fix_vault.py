# Ejecuta esto en un archivo llamado fix_vault.py o directo en python3 -c
from src.database.manager import db
from src.logic.vault import vault
from src.logic.ghost_shell import init_ghost
import os
from dotenv import load_dotenv

load_dotenv()
db.init_db()

# 1. Inicializamos el cifrador con la llave del .env
init_ghost(os.getenv("ENCRYPTION_KEY"))

# 2. Inyectamos manualmente K2 y K3 en la DB (Cifradas)
# Usamos los valores exactos de tu .env
vault.store_secret("K2_MENTE", "M1ND-09-122442")
vault.store_secret("K3_ACCION", "BODY-09-8295742")

print("✅ Vault sincronizado. K2 y K3 ahora viven cifradas en la DB.")

