import base64
import httpx
from loguru import logger
from src.logic.config import config
from pathlib import Path

class GitHubSync:
    """Gestiona el respaldo de la base de datos y config en GitHub."""
    
    def __init__(self):
        self.token = config.github_token.get_secret_value()
        self.repo = f"{config.github_username}/SHADOW_BACKUP"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def respaldar_archivo(self, ruta_archivo: str):
        """Sube un archivo a GitHub usando la API de contenidos."""
        path = Path(ruta_archivo)
        if not path.exists():
            logger.error(f"⚠️ Archivo no encontrado para respaldo: {ruta_archivo}")
            return

        url = f"https://api.github.com/repos/{self.repo}/contents/backups/{path.name}"
        
        # 1. Obtener el SHA si el archivo ya existe (para actualizarlo)
        sha = None
        async with httpx.AsyncClient() as client:
            res = await client.get(url, headers=self.headers)
            if res.status_code == 200:
                sha = res.json().get("sha")

            # 2. Leer y codificar contenido
            with open(path, "rb") as f:
                content = base64.b64encode(f.read()).decode()

            # 3. Payload del Commit
            data = {
                "message": f"🤖 SHADOW_SYNC: Respaldo automático {path.name}",
                "content": content,
                "branch": "main"
            }
            if sha:
                data["sha"] = sha

            # 4. Push a GitHub
            put_res = await client.put(url, headers=self.headers, json=data)
            
            if put_res.status_code in [200, 201]:
                logger.success(f"☁️ [SYNC]: {path.name} respaldado en la nube con éxito.")
            else:
                logger.error(f"❌ [SYNC]: Error al subir {path.name}: {put_res.text}")

sync_manager = GitHubSync()

