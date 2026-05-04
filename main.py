# main.py - REFACTORIZADO
import sys
import threading
import time
import signal
import io
from src.logic.ghost_shell import ghost
from src.logic.survival_protocol import survival
from src.logic.init_profile import ProfileManager
from src.database.manager import db
from src.database.models import Usuario
from src.tui.app import ShadowGrimorio
from loguru import logger

log_capture = io.StringIO()

def graceful_shutdown(signum=None, frame=None):
    logger.info("📡 INICIANDO PROTOCOLO DE SALIDA...")

    try:
        from src.logic.agent_manager import manager
        activos = [n for n, s in manager.listar_agentes().items() if s == "on"]
        if activos:
            print(f"\n[!] Cerrando agentes activos: {', '.join(activos)}")
    except: pass

    
    # Intentar sincronización antes de apagar todo
    try:
        from src.logic.sync_engine import sync_engine
        # El sync_engine revisará por sí mismo si db.online es True
        sync_engine.synchronize()
    except Exception as e:
        logger.error(f"⚠️ Fallo en la sincronización final: {e}")

    if ghost:
        ghost.burn_session()
        
    db.shutdown()
    logger.info("--- 💀 SHADOW_GRIMORIO FUERA DE LÍNEA (EXIT EXITOSO) 💀 ---")
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

def loop_supervivencia():
    """Monitoreo de recursos en segundo plano."""
    while True:
        try:
            survival.monitorear()
        except Exception:
            pass
        time.sleep(5) # Aumentado para ahorrar batería en ZTE

def iniciar_sistema():
    from src.logic.config import BASE_DIR
    (BASE_DIR / "logs").mkdir(exist_ok=True)

    logger.remove()
    
    # 1. Archivo físico (Siempre confiable)
    logger.add(str(BASE_DIR / "logs" / "shadow_grimorio.log"), rotation="1 MB", level="DEBUG")

    # 2. Captura en Memoria (Para escupirlos al final)
    logger.add(log_capture, level="DEBUG", format="{time:HH:mm:ss} | {level} | {message}")

    # 3. Terminal (Solo para el arranque y el cierre)
    logger.add(sys.stderr, level="INFO", colorize=True)

    db.init_db()

    db.run_migrations()

    # Lanzar hilo de supervivencia
    monitor_thread = threading.Thread(target=loop_supervivencia, daemon=True)
    monitor_thread.start()

    try:
        logger.info("💀 NÚCLEO ACTIVADO - Lanzando interfaz...")
        es_nuevo = ProfileManager.es_primera_vez()
        
        app = ShadowGrimorio(es_primera_vez=es_nuevo)
        app.run()
        
    except Exception as e:
        logger.exception(f"Fallo crítico: {e}")
    finally:
        # --- AQUÍ ESTÁ EL TRUCO ---
        # Al cerrar la app, volcamos TODO el buffer de DEBUG a la terminal de golpe
        print("\n" + "="*50)
        print("📊 VOLCADO DE LOGS DE DEPURACIÓN (RITUAL CHECK):")
        print("="*50)
        print(log_capture.getvalue()) 
        print("="*50)
        graceful_shutdown()

if __name__ == "__main__":
    iniciar_sistema()

