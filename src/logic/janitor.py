import os
import time
import sqlite3
from pathlib import Path
from loguru import logger
from src.logic.config import config

class Janitor:
    """Conserje del sistema: Optimización y limpieza de residuos."""

    def __init__(self):
        self.log_dir = Path("logs")
        self.db_path = Path("data/shadow_local.db")
        self.temp_patterns = [".tmp", ".shadow", ".bak"]
        # Evitamos tocar el territorio del Fantasma para no causar Warnings de IO
        self.ghost_temp = self.log_dir / "session_temp"

    def limpiar_logs(self, dias=3):
        ahora = time.time()
        limite = ahora - (dias * 86400)
        eliminados = 0

        if not self.log_dir.exists():
            return 0

        for archivo in os.listdir(self.log_dir):
            ruta = self.log_dir / archivo
            if ruta.is_file() and archivo.endswith(".log"):
                try:
                    if ruta.stat().st_mtime < limite:
                        ruta.unlink(missing_ok=True)
                        eliminados += 1
                except Exception as e:
                    logger.debug(f"Janitor: Log {archivo} inaccesible en este momento.")

        return eliminados

    def purgar_temporales(self):
        """Elimina residuos evitando colisiones con GHOST_SHELL."""
        eliminados = 0
        # Buscamos en raíz y data, pero filtramos rutas críticas
        directorios = [Path("."), Path("data")]

        for d in directorios:
            if not d.exists(): continue
            for archivo in os.listdir(d):
                ruta = d / archivo
                # Regla de Oro: Si es el directorio de sesión activa, NO TOCAR
                if self.ghost_temp in ruta.parents or ruta == self.ghost_temp:
                    continue

                if any(archivo.endswith(pat) for pat in self.temp_patterns):
                    try:
                        if ruta.exists():
                            ruta.unlink(missing_ok=True)
                            eliminados += 1
                    except:
                        pass # Silencio atómico para archivos volátiles
        return eliminados

    def optimizar_db(self):
        if not self.db_path.exists():
            return False
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("VACUUM")
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Janitor falló optimizando DB: {e}")
            return False

    async def ejecutar_limpieza_profunda(self):
        logger.info("🧹 JANITOR: Iniciando limpieza profunda...")
        logs = self.limpiar_logs()
        temps = self.purgar_temporales()
        db_ok = self.optimizar_db()
        resumen = f"Logs: {logs} | Temps: {temps} | DB: {'OK' if db_ok else 'FAIL'}"
        logger.success(f"🧹 JANITOR: Mantenimiento completado. {resumen}")
        return resumen

janitor = Janitor()

