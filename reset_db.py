from sqlalchemy import text
from src.database.manager import db
from src.database.models import Base
from loguru import logger

def protocol_lazaro():
    logger.warning("💀 Iniciando Protocolo Lázaro: Purga total de Neon...")
    
    session = db.get_session()
    engine = db.engine
    
    try:
        # 1. Forzar borrado en cascada (Exclusivo de PostgreSQL)
        # Esto elimina las tablas ignorando las restricciones de llave foránea
        tables = ["conocimientos", "preferencias", "dispositivos", "usuarios", "rangos", "secretos", "proveedores"]
        
        for table in tables:
            session.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE;"))
        
        session.commit()
        logger.success("🧹 Tablas antiguas purgadas con CASCADE.")

        # 2. Re-materializar usando SQLAlchemy
        Base.metadata.create_all(bind=engine)
        logger.success("🏗️ Nueva estructura 3FN materializada en Neon.")
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Fallo en Protocolo Lázaro: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    protocol_lazaro()

