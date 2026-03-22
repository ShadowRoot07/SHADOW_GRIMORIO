import httpx
import base64
import os
from src.logic.config import config
from loguru import logger

class LazaroProtocol:
    def __init__(self):
        self.token = config.github_token.get_secret_value()
        self.repo = f"{config.github_username}/SHADOW_BACKUP"
        self.headers = {"Authorization": f"token {self.token}"}

    async def ejecutar(self):
        cipher = config.get_cipher()
        if not cipher:
            print("\n❌ [ERROR]: No se puede ejecutar LÁZARO sin una llave válida en el .env")
            return

        print("\n[🧟] INICIANDO PROTOCOLO LÁZARO: Recuperando botín cifrado...")

        archivos = ["data/shadow_local.db", "config.yaml"]

        async with httpx.AsyncClient() as client:
            for ruta in archivos:
                nombre_base = os.path.basename(ruta)
                url = f"https://api.github.com/repos/{self.repo}/contents/backups/{nombre_base}.shadow"
                res = await client.get(url, headers=self.headers)

                if res.status_code == 200:
                    content_b64 = res.json()['content']
                    encrypted_data = base64.b64decode(content_b64)

                    try:
                        decrypted_data = cipher.decrypt(encrypted_data)
                        os.makedirs(os.path.dirname(ruta), exist_ok=True)
                        with open(ruta, "wb") as f:
                            f.write(decrypted_data)
                        print(f"✅ {ruta} restaurado con éxito.")
                    except Exception as e:
                        print(f"❌ Error al descifrar {ruta}: Llave maestra incorrecta o corrupta.")
                else:
                    print(f"⚠️ No se encontró respaldo para {ruta} en la nube.")

lazaro = LazaroProtocol()

