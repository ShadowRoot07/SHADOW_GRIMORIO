import sys
from src.database.manager import db
from src.tui.app import ShadowGrimorio
from loguru import logger

def iniciar_sistema():
    # Limpiamos configuraciones previas
    logger.remove()
    
    # 1. Log a archivo (para persistencia)
    logger.add("logs/shadow_grimorio.log", rotation="1 MB", level="DEBUG")
    
    # 2. Log a terminal (para desarrollo en vivo)
    # Usamos enqueue=True para que no bloquee la TUI
    logger.add(sys.stderr, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>", level="DEBUG")

    logger.info("--- 💀 INICIANDO PROTOCOLO SHADOW_GRIMORIO v1.0 💀 ---")

    db.init_db()
    app = ShadowGrimorio()
    app.run()

if __name__ == "__main__":
    iniciar_sistema()

