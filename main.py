# main.py
from src.database.manager import db
from src.tui.app import ShadowGrimorio
from loguru import logger

def iniciar_sistema():
    logger.info("--- INICIANDO PROTOCOLO SHADOW_GRIMORIO ---")
    
    # 1. Inicializar Base de Datos
    db.init_db()
    
    # 2. Lanzar Interfaz
    app = ShadowGrimorio()
    app.run()

if __name__ == "__main__":
    iniciar_sistema()

