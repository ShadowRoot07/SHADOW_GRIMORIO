import sys
import threading
import time
import signal
from pathlib import Path
from src.logic.config import config, BASE_DIR
from src.logic.ghost_shell import init_ghost, ghost
from src.logic.survival_protocol import survival
from src.logic.init_profile import ProfileManager
from src.database.manager import db
from src.tui.app import ShadowGrimorio
from loguru import logger

def graceful_shutdown(signum, frame):
    if ghost:
        ghost.burn_session()
    db.shutdown()
    logger.info("--- 💀 SHADOW_GRIMORIO FUERA DE LÍNEA (EXIT EXITOSO) 💀 ---")
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

def loop_supervivencia():
    while True:
        try:
            survival.monitorear()
        except Exception:
            pass
        time.sleep(3)

def iniciar_sistema():
    # 0. Asegurar directorios críticos
    (BASE_DIR / "logs").mkdir(exist_ok=True)
    (BASE_DIR / "data").mkdir(exist_ok=True)

    logger.remove()
    # Ruta absoluta para logs
    logger.add(str(BASE_DIR / "logs" / "shadow_grimorio.log"), rotation="1 MB", level="DEBUG")
    logger.add(sys.stderr, level="INFO")

    if not config.validate_security():
        logger.critical("🚨 GHOST_SHELL: Abortando inicio. Fallo de seguridad en .env.")
        sys.exit(1)

    init_ghost(config.encryption_key)
    db.init_db()

    threading.Thread(target=loop_supervivencia, daemon=True).start()

    try:
        logger.info(f"--- 💀 INICIANDO PROTOCOLO SHADOW_GRIMORIO v1.0_beta 💀 ---")
        logger.info(f"📍 Raíz detectada: {BASE_DIR}")
        
        es_nuevo = ProfileManager.es_primera_vez()
        app = ShadowGrimorio(es_primera_vez=es_nuevo)
        app.run()
    except Exception as e:
        logger.exception(f"Fallo crítico en el Núcleo: {e}")
    finally:
        graceful_shutdown(0, None)

if __name__ == "__main__":
    iniciar_sistema()

