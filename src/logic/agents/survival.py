import time
import sys
import os
from pathlib import Path

# --- CONFIGURACIÓN DE RUTA CRÍTICA ---
# Asegura que el proceso hijo encuentre el paquete 'src'
current_path = Path(__file__).resolve()
base_path = current_path.parent.parent.parent.parent
sys.path.append(str(base_path))

try:
    from src.logic.hardware_bridge import bridge
    from src.logic.agent_manager import manager
    from loguru import logger
except ImportError as e:
    # Error crítico: Si no encuentra las rutas, imprimimos directo a stderr
    sys.stderr.write(f" [!] Error de importación en SURVIVAL: {e}\n")
    sys.exit(1)

def run():
    """Protocolo de Supervivencia: Monitorea batería y recursos del ZTE."""
    logger.info("🛡️ [SURVIVAL]: Protocolo de monitoreo de hardware iniciado.")

    while True:
        try:
            ram_libre = bridge.obtener_ram_libre()
            bateria = bridge.obtener_bateria()

            # --- LATIDO (HEARTBEAT) ---
            # Esto confirma que el loop no está trabado
            logger.info(f"💓 [LATIDO] RAM: {ram_libre}MB | BATT: {bateria}%")

            # NIVEL 1: ADVERTENCIA (RAM < 500MB)
            if ram_libre < 500:
                logger.warning(f"⚠️ [RAM BAJA]: {ram_libre}MB libres. Suspendiendo GHOST_CODER...")
                manager.apagar_agente("ghost_coder")

            # NIVEL 2: EMERGENCIA (RAM < 200MB)
            if ram_libre < 200:
                logger.critical("🔥 [RAM CRÍTICA]: Iniciando PURGA TOTAL del enjambre.")
                manager.matar_todo()

            # NIVEL 3: BATERÍA CRÍTICA
            if bateria < 10:
                logger.error(f"🪫 [ENERGÍA]: {bateria}% restante. Hibernando.")
                time.sleep(300)
            else:
                # Forzamos el vaciado del búfer para que el log se actualice en tiempo real
                sys.stdout.flush()
                time.sleep(30)
                
        except Exception as e:
            logger.error(f"Error en loop de supervivencia: {e}")
            time.sleep(10)

if __name__ == "__main__":
    # Aseguramos que el directorio de logs exista
    log_dir = base_path / "logs"
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / "daemon_survival.log"
    
    # Configuración del logger: 'enqueue=True' ayuda con el buffering en procesos separados
    logger.remove() # Eliminamos el handler por defecto
    logger.add(sys.stdout, colorize=True, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")
    logger.add(log_file, rotation="1 MB", retention="1 days", enqueue=True)

    try:
        run()
    except KeyboardInterrupt:
        logger.info("🛑 [SURVIVAL]: Apagado manual detectado.")
        sys.exit(0)

