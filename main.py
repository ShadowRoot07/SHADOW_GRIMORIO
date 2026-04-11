import sys
import threading
import time
from src.logic.config import config
from src.logic.ghost_shell import init_ghost, ghost
from src.logic.survival_protocol import survival
from src.logic.init_profile import ProfileManager
from src.logic.session import SessionManager
from src.database.manager import db
from src.tui.app import ShadowGrimorio
from loguru import logger

def loop_supervivencia():
    """Hilo persistente para el monitoreo de recursos del ZTE."""
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
    logger.add(
        sys.stderr, 
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> - <level>{message}</level>", 
        level="INFO"
    )

    # 1. Seguridad Obligatoria (Capa .env)
    if not config.validate_security():
        logger.critical("🚨 GHOST_SHELL: Abortando inicio. Fallo de seguridad en .env.")
        sys.exit(1)

    # 2. Inicializar Capa de Invisibilidad (Cifrado de Sesión)
    init_ghost(config.encryption_key)
    logger.info("👻 GHOST_SHELL: Capa de invisibilidad activa.")

    # 3. Base de Datos
    db.init_db()

    # 4. Hilo de Telemetría
    threading.Thread(target=loop_supervivencia, daemon=True).start()

    try:
        logger.info("--- 💀 INICIANDO PROTOCOLO SHADOW_GRIMORIO v1.0 💀 ---")
        
        # 5. Determinación de Estado: ¿Primera vez o Retorno?
        es_nuevo = ProfileManager.es_primera_vez()
        
        # Lanzar TUI con el estado detectado
        # Pasamos es_nuevo para que la App decida qué Screen mostrar primero
        app = ShadowGrimorio(es_primera_vez=es_nuevo)
        app.run()

    except Exception as e:
        logger.exception(f"Fallo crítico en el Núcleo: {e}")
    finally:
        # Limpieza de rastros
        if ghost:
            ghost.burn_session()
        logger.info("--- 💀 CONEXIÓN CERRADA: SHADOW_GRIMORIO FUERA DE LÍNEA  💀 ---")

if __name__ == "__main__":
    iniciar_sistema()

