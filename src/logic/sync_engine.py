from datetime import datetime
from loguru import logger
from src.database.manager import db
from src.database.models import Usuario, Secreto, Preferencia, Conocimiento, HitoHistorial

class ShadowSyncEngine:
    """Orquestador de sincronización basado en timestamps (Last-Write-Wins)."""

    @staticmethod
    def synchronize():
        from src.database.models import Usuario, Proyecto, Secreto, Preferencia, Conocimiento, HitoHistorial, Rango, Proveedor, Dispositivo
        
        if not db.online:
            logger.info("📡 SYNC: Saltando sincronización (Modo Offline).")
            return

        logger.info("🔄 SYNC: Iniciando ritual de sincronización Espejo...")
        
        # Jerarquía completa: Proveedores y Rangos deben existir antes que Secretos y Usuarios
        modelos_prioridad = [Rango, Proveedor, Usuario, Proyecto, Dispositivo]
        modelos_datos = [Secreto, Preferencia, Conocimiento, HitoHistorial]

        session_local = db.SessionLocal()
        session_remote = db.SessionRemote()

        try:
            # Sincronización de Estructura
            for modelo in modelos_prioridad:
                items = session_local.query(modelo).all()
                for item in items:
                    session_remote.merge(item)
                session_remote.commit() 
                session_remote.expunge_all() # Limpiamos memoria para evitar colisiones

            # Sincronización de Datos (Recuerdos, Hitos)
            for modelo in modelos_datos:
                items = session_local.query(modelo).all()
                for item in items:
                    try:
                        session_remote.merge(item)
                    except Exception as e:
                        session_remote.rollback()
                        logger.warning(f"⚠️ SYNC: Saltando item en {modelo.__tablename__}: {str(e)[:50]}")
                        continue
                session_remote.commit()

            session_local.commit()
            logger.success("✅ SYNC: Ritual de Espejo completado.")

        except Exception as e:
            if session_remote: session_remote.rollback()
            logger.error(f"🚨 SYNC: Fallo crítico: {e}")
        finally:
            session_local.close()
            session_remote.close()

sync_engine = ShadowSyncEngine() 
