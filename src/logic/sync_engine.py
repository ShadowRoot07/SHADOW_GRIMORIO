from datetime import datetime
from loguru import logger
from src.database.manager import db
from src.database.models import Usuario, Secreto, Preferencia, Conocimiento, HitoHistorial

class ShadowSyncEngine:
    """Orquestador de sincronización basado en timestamps (Last-Write-Wins)."""

    @staticmethod
    def synchronize():
        from src.database.models import Usuario, Proyecto, Secreto, Preferencia, Conocimiento, HitoHistorial, Rango
        
        if not db.online:
            logger.info("📡 SYNC: Saltando sincronización (Modo Offline).")
            return

        logger.info("🔄 SYNC: Iniciando ritual de sincronización Espejo...")
        
        # JERARQUÍA ESTRICTA: De lo más general (maestros) a lo más específico (datos)
        modelos_infra = [Rango, Usuario, Proyecto]
        modelos_datos = [Secreto, Preferencia, Conocimiento, HitoHistorial]

        session_local = db.SessionLocal()
        session_remote = db.SessionRemote()

        try:
            # 1. INFRAESTRUCTURA
            for modelo in modelos_infra:
                items = session_local.query(modelo).all()
                for item in items:
                    session_remote.merge(item)
                session_remote.commit()
                # Re-abrimos para evitar estados 'detatched'
                session_remote = db.SessionRemote()

            # 2. DATOS
            for modelo in modelos_datos:
                items = session_local.query(modelo).all()
                for item in items:
                    try:
                        session_remote.merge(item)
                    except Exception as e:
                        session_remote.rollback()
                        logger.warning(f"⚠️ SYNC: Saltando item de {modelo.__tablename__}: {str(e)[:40]}...")
                        continue

            session_local.commit()
            session_remote.commit()
            logger.success("✅ SYNC: Ritual de Espejo completado con éxito.")

        except Exception as e:
            if session_remote: session_remote.rollback()
            logger.error(f"🚨 SYNC: Fallo crítico en el ritual: {e}")
        finally:
            session_local.close()
            session_remote.close()

sync_engine = ShadowSyncEngine() 
