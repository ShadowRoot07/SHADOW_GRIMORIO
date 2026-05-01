from datetime import datetime
from loguru import logger
from src.database.manager import db
from src.database.models import Usuario, Secreto, Preferencia, Conocimiento

class ShadowSyncEngine:
    """Orquestador de sincronización basado en timestamps (Last-Write-Wins)."""

    @staticmethod
    def synchronize():
        if not db.online:
            logger.info("📡 SYNC: Saltando sincronización (Modo Offline).")
            return

        logger.info("🔄 SYNC: Iniciando ritual de sincronización Espejo...")
        
        # Lista de modelos a sincronizar
        modelos = [Usuario, Secreto, Preferencia, Conocimiento]
        
        session_local = db.SessionLocal()
        session_remote = db.SessionRemote()

        try:
            for modelo in modelos:
                # 1. Obtener registros de ambos mundos
                items_local = session_local.query(modelo).all()
                items_remote = session_remote.query(modelo).all()

                # Crear diccionarios para búsqueda rápida por ID o nombre_llave
                remote_map = { (getattr(i, 'id', None) or getattr(i, 'nombre_llave', None)): i for i in items_remote }

                for local_item in items_local:
                    key = getattr(local_item, 'id', None) or getattr(local_item, 'nombre_llave', None)
                    remote_item = remote_map.get(key)

                    if not remote_item:
                        # No existe en la nube, lo subimos
                        session_remote.merge(local_item)
                    else:
                        # Ambos existen: Comparar fechas
                        if local_item.updated_at > remote_item.updated_at:
                            logger.debug(f"📤 SYNC: Actualizando {modelo.__tablename__} en remoto (Local es más nuevo).")
                            session_remote.merge(local_item)
                        elif remote_item.updated_at > local_item.updated_at:
                            logger.debug(f"📥 SYNC: Actualizando {modelo.__tablename__} en local (Remoto es más nuevo).")
                            session_local.merge(remote_item)

            session_local.commit()
            session_remote.commit()
            logger.success("✅ SYNC: Grimorio sincronizado exitosamente.")

        except Exception as e:
            session_local.rollback()
            session_remote.rollback()
            logger.error(f"❌ SYNC: Fallo en el ritual de sincronización: {e}")
        finally:
            session_local.close()
            session_remote.close()

sync_engine = ShadowSyncEngine()

