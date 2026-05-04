import os
from typing import Dict, Optional, Any
from dotenv import load_dotenv
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Secreto
from src.logic.config import config, BASE_DIR
from src.logic.config import config
from loguru import logger

load_dotenv(BASE_DIR / ".env")

class DatabaseManager:
    """Orquestador de persistencia dual: SQLite (Local) + PostgreSQL (Remoto)."""

    def __init__(self, contexto_inicial=None, **kwargs):
        # URL remota: La buscamos en .env, si no, usamos la de config como fallback
        super().__init__(**kwargs)
        self.contexto_inicial = contexto_inicial # Esto detiene el crash de on_mount
        self.url_remote = os.getenv("DATABASE_URL")
        self.url_local = f"sqlite:///{BASE_DIR}/data/shadow_local.db"
        self.engine_remote = None
        self.engine_local = None
        self.SessionRemote = None
        self.SessionLocal = None
        self.online = False

    def init_db(self, drop_all: bool = False):
        """Inicializa motores duales. La estructura ahora es dictada por Alembic."""
        # --- 1. INICIALIZAR LOCAL (EL ANCLA) ---
        try:
            self.engine_local = create_engine(
                self.url_local,
                connect_args={"check_same_thread": False}
            )
            # Optimización para Termux/ZTE (Mantener rendimiento en móvil)
            @event.listens_for(self.engine_local, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.close()

            self.SessionLocal = sessionmaker(bind=self.engine_local)
            
            # Nota: Si usas drop_all, Alembic perderá el rastro de la versión.
            # Solo usar en desarrollo extremo.
            if drop_all: 
                Base.metadata.drop_all(self.engine_local)
                logger.warning("⚠️ DATABASE: Tablas locales purgadas.")

            logger.success("📁 DATABASE: Espejo Local (SQLite) vinculado.")
        except Exception as e:
            logger.error(f"❌ DATABASE: Fallo crítico en motor local: {e}")

        # --- 2. INICIALIZAR REMOTO (LA NUBE) ---
        if self.url_remote:
            try:
                # connect_timeout=5 para evitar cuelgues por mala señal en el móvil
                self.engine_remote = create_engine(
                    self.url_remote,
                    pool_pre_ping=True,
                    connect_args={'connect_timeout': 5}
                )
                
                # Verificación de pulso con Neon
                with self.engine_remote.connect() as conn:
                    self.online = True

                self.SessionRemote = sessionmaker(bind=self.engine_remote)
                
                if drop_all: 
                    Base.metadata.drop_all(self.engine_remote)
                    logger.warning("⚠️ DATABASE: Tablas remotas purgadas.")

                logger.success("🌐 DATABASE: En línea con Neon (PostgreSQL).")
            except Exception:
                self.online = False
                logger.warning("📡 DATABASE: Modo Offline activo. No se pudo alcanzar el servidor remoto.")
        else:
            logger.error("🚨 DATABASE: No se detectó DATABASE_URL en el entorno.")

    def get_session(self, force_local=False):
        """Retorna la sesión remota si hay internet, de lo contrario la local."""
        if self.online and not force_local:
            return self.SessionRemote()
        return self.SessionLocal()

    def get_secret(self, key_name: str) -> Optional[str]:
        """Consulta un secreto cifrado en la base de datos."""
        from src.database.models import Secreto
        
        # Intentamos usar la sesión local por velocidad (está sincronizada)
        session = self.SessionLocal()
        try:
            secreto = session.query(Secreto).filter_by(nombre_llave=key_name).first()
            if secreto:
                return secreto.valor_cifrado
            return None
        except Exception as e:
            logger.error(f"❌ Error al recuperar secreto {key_name}: {e}")
            return None
        finally:
            session.close()

    def run_migrations(self):
        """Ejecuta las migraciones limpiando el contexto entre motores."""
        from alembic.config import Config
        from alembic import command
        from src.logic.config import BASE_DIR
        import sys

        # Forzar recarga de módulos de alembic para evitar que guarde el dialecto previo
        if 'alembic.runtime.migration' in sys.modules:
            del sys.modules['alembic.runtime.migration']

        alembic_cfg = Config(BASE_DIR / "alembic.ini")
        
        # 1. Migrar Local
        try:
            logger.info("⚙️ ALCHEMY: Sincronizando Local (SQLite)...")
            alembic_cfg.set_main_option("sqlalchemy.url", self.url_local)
            command.upgrade(alembic_cfg, "head")
        except Exception as e:
            logger.error(f"❌ Error Local: {e}")

        # 2. Migrar Remoto
        if self.online and self.url_remote:
            try:
                logger.info("⚙️ ALCHEMY: Sincronizando Neon (PostgreSQL)...")
                # IMPORTANTE: Recargar configuración limpia para el motor remoto
                alembic_cfg = Config(BASE_DIR / "alembic.ini") 
                alembic_cfg.set_main_option("sqlalchemy.url", self.url_remote)
                command.upgrade(alembic_cfg, "head")
                logger.success("✅ Neon actualizado.")
            except Exception as e:
                logger.warning(f"⚠️ Conflicto en Neon: {e}")


    def shutdown(self):
        """Libera todos los recursos."""
        if self.engine_local: self.engine_local.dispose()
        if self.engine_remote: self.engine_remote.dispose()
        logger.info("📁 DATABASE: Conexiones duales liberadas.")

    # --- WRAPPERS PARA GHOST_SHELL ---
    def save_secret(self, nombre: str, valor_plano: str):
        from src.logic.ghost_shell import ghost
        if not ghost or not ghost.cipher:
            logger.error("❌ DATABASE: Sin GHOST_SHELL activo.")
            return

        # Guardamos en la sesión actual (la que el sistema decida)
        session = self.get_session()
        try:
            ruido = ghost.obfuscate_data(valor_plano)
            secreto = session.query(Secreto).filter_by(nombre_llave=nombre).first()
            if secreto:
                secreto.valor_cifrado = ruido
            else:
                secreto = Secreto(nombre_llave=nombre, valor_cifrado=ruido)
                session.add(secreto)
            session.commit()
            logger.success(f"🔒 GHOST_SHELL: Secreto '{nombre}' persistido.")
        except Exception as e:
            session.rollback()
            logger.error(f"❌ DATABASE: Error al guardar secreto: {e}")
        finally:
            session.close()


db = DatabaseManager()

