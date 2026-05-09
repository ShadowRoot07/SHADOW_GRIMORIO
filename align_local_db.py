import sys
import os
from pathlib import Path

# 1. Configuración de rutas para el entorno Termux
base_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(base_dir))

from src.database.manager import db
from src.database.models import Base, Rango, Usuario, Proyecto
from src.logic.init_profile import ProfileManager
from loguru import logger
from sqlalchemy import text

def alinear_espejo_local():
    logger.info("📡 INICIANDO ALINEACIÓN DE NÚCLEO LOCAL (SQLite)...")
    
    # Aseguramos que la carpeta data exista
    (base_dir / "data").mkdir(exist_ok=True)
    
    # 2. Inicializar motor local
    db.init_db()
    engine = db.engine_local
    
    if not engine:
        logger.error("❌ No se pudo vincular el motor local.")
        return

    try:
        with engine.connect() as conn:
            # 3. Optimización para Móvil (Modo WAL)
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            
            # 4. Sincronización de Estructura vía Alembic
            logger.info("⚙️ Aplicando esquemas de Alembic...")
            db.run_migrations()
            
            # 5. Inyección de Datos Maestros (Rangos)
            session = db.SessionLocal()
            try:
                logger.info("💉 Inyectando jerarquía de rangos...")
                ProfileManager.inicializar_catalogo_rangos(session)
                
                # 6. Asegurar existencia del Proyecto SHADOW_GRIMORIO
                # Esto es vital para que los hitos de memoria tengan un padre
                grimorio = session.query(Proyecto).filter_by(nombre="SHADOW_GRIMORIO").first()
                if not grimorio:
                    logger.info("🆕 Registrando proyecto SHADOW_GRIMORIO en el núcleo...")
                    grimorio = Proyecto(
                        nombre="SHADOW_GRIMORIO",
                        path_local=str(base_dir),
                        rama_actual="feature/spica-neural-link-v1"
                    )
                    session.add(grimorio)
                
                session.commit()
                logger.success("✅ BASE DE DATOS LOCAL ALINEADA Y LISTA.")
                
            except Exception as e:
                session.rollback()
                logger.error(f"❌ Fallo en la inyección de datos: {e}")
            finally:
                session.close()

    except Exception as e:
        logger.error(f"💥 Error crítico de alineación: {e}")

if __name__ == "__main__":
    alinear_espejo_local()

