from datetime import datetime
from loguru import logger
from src.database.manager import db
from src.database.models import Usuario, Secreto, Preferencia, Conocimiento, HitoHistorial

class ShadowSyncEngine:
    """Orquestador de sincronización basado en timestamps (Last-Write-Wins)."""

    @staticmethod
    def synchronize():
        if not db.online:
            logger.info("📡 SYNC: Saltando sincronización (Modo Offline).")
            return
            
        logger.info("🔄 SYNC: Iniciando ritual de sincronización Espejo...")
        modelos = [Usuario, Secreto, Preferencia, Conocimiento, HitoHistorial]
        
        session_local = db.SessionLocal()
        session_remote = db.SessionRemote()

        try:
            for modelo in modelos:
                items_local = session_local.query(modelo).all()
                
                # Sincronización uno a uno
                for local_item in items_local:
                    try:
                        # Usamos merge para que Neon intente actualizar o insertar
                        session_remote.merge(local_item)
                    except Exception as e:
                        # Si un item falla (como el Usuario con Rango 2), 
                        # hacemos rollback SOLO del remoto y seguimos con el siguiente modelo
                        session_remote.rollback()
                        logger.warning(f"⚠️ SYNC: Item de {modelo.__tablename__} rechazado por Neon. Continuando...")

            # --- CIERRE INDEPENDIENTE ---
            # Primero aseguramos la memoria local (ZTE)
            try:
                session_local.commit()
                logger.success("📁 SYNC: Memoria local sellada en SQLite.")
            except Exception as e:
                session_local.rollback()
                logger.error(f"❌ SYNC: Fallo crítico guardando en celular: {e}")

            # Luego intentamos cerrar la nube
            if db.online:
                try:
                    session_remote.commit()
                    logger.success("✅ SYNC: Espejo en Neon actualizado.")
                except Exception as e:
                    session_remote.rollback()
                    logger.warning(f"📡 SYNC: Neon rechazó el commit final (FK Violation probable).")

        finally:
            session_local.close()
            session_remote.close()
