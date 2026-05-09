from src.logic.vault import vault
from src.logic.config import config
import json

# 1. Guardar un secreto
test_api_key = "gsk_shadow_123456789"
vault.store_secret("GROQ_TEST", test_api_key)

# 2. Verificar que en el archivo NO es legible
with open("data/shadow_vault.json", "r") as f:
    contenido = json.load(f)
    print(f"🔒 Contenido en disco: {contenido['GROQ_TEST']}")
    if test_api_key not in contenido['GROQ_TEST']:
        print("✅ ÉXITO: El secreto está cifrado.")

# 3. Recuperar y descifrar
recuperado = vault.get_secret("GROQ_TEST")
print(f"🔑 Secreto recuperado: {recuperado}")

if recuperado == test_api_key:
    print("✅ ÉXITO: Descifrado perfecto.")

