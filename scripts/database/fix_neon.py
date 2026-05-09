# Crea un archivo temporal llamado fix_neon.py
import sys
from pathlib import Path

# Fix de Path para que reconozca 'src'
raiz = Path(__file__).resolve().parent
if str(raiz) not in sys.path:
    sys.path.append(str(raiz))

from src.database.manager import db
from src.logic.init_profile import ProfileManager
from loguru import logger

def alinear_neon():
    logger.info("📡 Conectando con Neon para alinear rangos...")
    # Obtenemos sesión (esto disparará la conexión a Neon si está configurado)
    session = db.get_session()
    try:
        # Forzamos la creación de los rangos (Shadow_Coder, etc.) en la nube
        ProfileManager.inicializar_catalogo_rangos(session)
        session.commit()
        logger.success("✅ Rangos alineados en Neon. El error de ForeignKey debería desaparecer.")
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Error al alinear: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    alinear_neon()

