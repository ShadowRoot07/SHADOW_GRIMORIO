from cryptography.fernet import Fernet
import os

# 1. Generar una llave real y válida
key = Fernet.generate_key().decode()

# 2. Escribirla limpiamente en el .env
with open(".env", "a") as f:
    f.write(f"\nENCRYPTION_KEY={key}\n")

print(f"✅ Nueva llave generada: {key}")
print("🚀 Intenta correr './shadow ui' ahora.")

