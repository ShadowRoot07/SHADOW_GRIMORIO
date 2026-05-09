import os
from sqlalchemy import text
from src.database.manager import db
from src.database.models import Base
from loguru import logger

def protocol_lazaro():
    logger.warning("💀 Iniciando Protocolo Lázaro: Purga total de bases de datos...")

    # 1. Inicializar motores
    db.init_db()

    # Operamos sobre ambas sesiones
    # Usamos una tupla (nombre, sesión, es_postgres)
    sessions_config = [
        ("LOCAL (ZTE)", db.SessionLocal(), False),
        ("REMOTO (Neon)", db.SessionRemote(), True)
    ]

    tables = ["conocimientos", "preferencias", "dispositivos", "usuarios", "rangos", "secretos", "proveedores"]

    try:
        for name, session, is_postgres in sessions_config:
            if not session:
                logger.warning(f"⚠️ Saltando {name}: Sesión no disponible.")
                continue

            logger.info(f"🧹 Purgando espejo: {name}")
            for table in tables:
                # 2. Lógica de dialecto: Solo Postgres usa CASCADE
                suffix = " CASCADE" if is_postgres else ""
                query = f"DROP TABLE IF EXISTS {table}{suffix};"
                
                session.execute(text(query))
            
            session.commit()
            logger.debug(f"✅ Tablas eliminadas en {name}.")

        # 3. Re-materializar estructuras
        logger.info("🏗️ Re-construyendo estructuras con Timestamps...")
        Base.metadata.create_all(bind=db.engine_local)
        if db.online:
            Base.metadata.create_all(bind=db.engine_remote)
        
        logger.success("✨ Protocolo Lázaro completado con éxito.")

    except Exception as e:
        logger.error(f"❌ Fallo en Lázaro: {e}")
        # Intentar rollback en las sesiones activas
        for _, session, _ in sessions_config:
            if session: session.rollback()
    finally:
        # 4. Limpieza de conexiones
        for _, session, _ in sessions_config:
            if session: session.close()
        db.shutdown()

if __name__ == "__main__":
    protocol_lazaro()

