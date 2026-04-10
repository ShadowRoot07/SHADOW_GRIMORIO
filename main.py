import sys
import threading
import time
from src.logic.config import config
from src.logic.ghost_shell import init_ghost, ghost
from src.logic.survival_protocol import survival
from src.database.manager import db
from src.tui.app import ShadowGrimorio
from loguru import logger

def loop_supervivencia():
    while True:
        try:
            survival.monitorear()
        except Exception:
            pass
        time.sleep(3)

def iniciar_sistema():
    # Logs iniciales
    logger.remove()
    logger.add("logs/shadow_grimorio.log", rotation="1 MB", level="DEBUG")
    logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> - <level>{message}</level>", level="INFO")

    # 1. Seguridad Obligatoria
    if not config.validate_security():
        logger.critical("🚨 GHOST_SHELL: Abortando inicio. Fallo de seguridad.")
        sys.exit(1)
    
    # 2. Inicializar Protocolos
    init_ghost(config.encryption_key)
    logger.info("👻 GHOST_SHELL: Capa de invisibilidad activa.")
    
    # Iniciar telemetría
    threading.Thread(target=loop_supervivencia, daemon=True).start()

    try:
        logger.info("--- 💀 INICIANDO PROTOCOLO SHADOW_GRIMORIO v1.0 💀 ---")
        db.init_db()
        
        # Lanzar TUI
        app = ShadowGrimorio()
        app.run()
        
    except Exception as e:
        logger.exception(f"Fallo crítico en el Núcleo: {e}")
    finally:
        # Esto se ejecuta SIEMPRE al cerrar, incluso con Error o Ctrl+C
        if ghost:
            ghost.burn_session()
        logger.info("--- 💀 CONEXIÓN CERRADA: SHADOW_GRIMORIO FUERA DE LÍNEA 💀 ---")

if __name__ == "__main__":
    iniciar_sistema()

