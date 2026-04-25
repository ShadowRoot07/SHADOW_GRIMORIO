import sys
import threading
import time
import signal
from src.logic.config import config
from src.logic.ghost_shell import init_ghost, ghost
from src.logic.survival_protocol import survival
from src.logic.init_profile import ProfileManager
from src.database.manager import db
from src.tui.app import ShadowGrimorio
from loguru import logger

def graceful_shutdown(signum, frame):
    """Captura señales de interrupción para cerrar todo ordenadamente."""
    logger.warning(f"⚠️ SISTEMA: Recibida señal {signum}. Iniciando purga de seguridad...")
    if ghost:
        ghost.burn_session()
    db.shutdown()
    logger.info("--- 💀 SHADOW_GRIMORIO FUERA DE LÍNEA (EXIT EXITOSO) 💀 ---")
    sys.exit(0)

# Registrar señales de cierre
signal.signal(signal.SIGINT, graceful_shutdown)  # Ctrl+C
signal.signal(signal.SIGTERM, graceful_shutdown) # Kill comando

def loop_supervivencia():
    while True:
        try:
            survival.monitorear()
        except Exception:
            pass
        time.sleep(3)

def iniciar_sistema():
    logger.remove()
    logger.add("logs/shadow_grimorio.log", rotation="1 MB", level="DEBUG")
    logger.add(sys.stderr, level="INFO")

    if not config.validate_security():
        logger.critical("🚨 GHOST_SHELL: Abortando inicio. Fallo de seguridad en .env.")
        sys.exit(1)

    init_ghost(config.encryption_key)
    db.init_db()

    threading.Thread(target=loop_supervivencia, daemon=True).start()

    try:
        logger.info("--- 💀 INICIANDO PROTOCOLO SHADOW_GRIMORIO v1.0_beta 💀 ---")
        es_nuevo = ProfileManager.es_primera_vez()
        app = ShadowGrimorio(es_primera_vez=es_nuevo)
        app.run()
    except Exception as e:
        logger.exception(f"Fallo crítico en el Núcleo: {e}")
    finally:
        # Esto se ejecuta si la TUI se cierra normalmente (con action_quit)
        graceful_shutdown(0, None)

if __name__ == "__main__":
    iniciar_sistema()

