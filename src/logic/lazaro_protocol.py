import httpx
import base64
import os
from pathlib import Path
from src.logic.config import config
from loguru import logger

class LazaroProtocol:
    def __init__(self):
        self.token = config.github_token.get_secret_value()
        # Aseguramos que el repo de backup tenga un nombre coherente
        self.repo = f"{config.github_username}/SHADOW_BACKUP"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def ejecutar(self):
        cipher = config.get_cipher()
        if not cipher:
            logger.error("❌ [LÁZARO]: Llave maestra no encontrada en el .env. Abortando resurrección.")
            return

        logger.info("🧟 [PROTOCOLO LÁZARO]: Iniciando recuperación de botín cifrado...")

        # Archivos críticos para reconstruir el sistema
        archivos = ["data/shadow_local.db", "config.yaml"]

        async with httpx.AsyncClient(timeout=20.0) as client:
            for ruta in archivos:
                nombre_base = os.path.basename(ruta)
                url = f"https://api.github.com/repos/{self.repo}/contents/backups/{nombre_base}.shadow"
                
                try:
                    res = await client.get(url, headers=self.headers)
                    
                    if res.status_code == 200:
                        datos_repo = res.json()
                        # GitHub envía el base64 con saltos de línea, lo limpiamos
                        content_b64 = datos_repo['content'].replace("\n", "")
                        encrypted_data = base64.b64decode(content_b64)

                        try:
                            decrypted_data = cipher.decrypt(encrypted_data)
                            
                            # Crear carpetas si no existen (ej: data/)
                            path_obj = Path(ruta)
                            path_obj.parent.mkdir(parents=True, exist_ok=True)
                            
                            with open(ruta, "wb") as f:
                                f.write(decrypted_data)
                            logger.success(f"✅ {ruta} resucitado con éxito.")
                            
                        except Exception:
                            logger.error(f"❌ Error al descifrar {ruta}: ¿La llave maestra es la correcta?")
                    else:
                        logger.warning(f"⚠️ No hay respaldo para {ruta} (Status: {res.status_code}).")
                
                except httpx.RequestError as e:
                    logger.error(f"🌐 Error de red en Lázaro: {e}")
                    break # Si no hay red, no seguimos intentando

lazaro = LazaroProtocol()

