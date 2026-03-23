import os
import time
import sqlite3
from loguru import logger
from src.logic.config import config

class Janitor:
    """Conserje del sistema: Optimización y limpieza de residuos."""

    def __init__(self):
        self.log_dir = "logs"
        self.db_path = "data/shadow_local.db"
        self.temp_patterns = [".tmp", ".shadow", ".bak"]

    def limpiar_logs(self, dias=3):
        """Elimina logs antiguos para ahorrar espacio en el ZTE."""
        ahora = time.time()
        limite = ahora - (dias * 86400)
        eliminados = 0

        if not os.path.exists(self.log_dir):
            return 0

        for archivo in os.listdir(self.log_dir):
            ruta = os.path.join(self.log_dir, archivo)
            if os.path.isfile(ruta) and archivo.endswith(".log"):
                if os.path.getmtime(ruta) < limite:
                    try:
                        os.remove(ruta)
                        eliminados += 1
                    except Exception as e:
                        logger.error(f"Janitor no pudo borrar log {archivo}: {e}")
        
        return eliminados

    def purgar_temporales(self):
        """Elimina archivos residuales de sesiones previas o backups."""
        eliminados = 0
        # Buscamos en la raíz y en data/
        directorios = [".", "data"]
        
        for d in directorios:
            if not os.path.exists(d): continue
            for archivo in os.listdir(d):
                if any(archivo.endswith(pat) for pat in self.temp_patterns):
                    try:
                        os.remove(os.path.join(d, archivo))
                        eliminados += 1
                    except:
                        pass
        return eliminados

    def optimizar_db(self):
        """Compacta la base de datos SQLite (VACUUM)."""
        if not os.path.exists(self.db_path):
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
        """Ejecuta el protocolo completo de mantenimiento."""
        logger.info("🧹 JANITOR: Iniciando limpieza profunda...")
        
        logs = self.limpiar_logs()
        temps = self.purgar_temporales()
        db_ok = self.optimizar_db()
        
        resumen = f"Logs: {logs} | Temps: {temps} | DB: {'OK' if db_ok else 'FAIL'}"
        logger.success(f"🧹 JANITOR: Mantenimiento completado. {resumen}")
        return resumen

# Instancia única para el sistema
janitor = Janitor()

