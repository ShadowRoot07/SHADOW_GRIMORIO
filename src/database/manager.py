from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Secreto
from src.logic.config import config
from src.logic.ghost_shell import ghost
from loguru import logger

class DatabaseManager:
    """Orquestador de persistencia con soporte para GHOST_SHELL y Detección Automática de Motor."""

    def __init__(self):
        self.db_url = str(config.database_url)
        self.engine = None
        self.SessionLocal = None

    def init_db(self, drop_all: bool = False):
        """Materializa las tablas detectando si el motor es SQLite o PostgreSQL."""
        try:
            if not self.engine:
                # 1. Detectar el motor desde la URL
                is_sqlite = self.db_url.startswith("sqlite")
                
                # 2. Configurar argumentos de conexión específicos
                connect_args = {}
                if is_sqlite:
                    # Blindaje solo para SQLite (evita bloqueos de hilos en Termux)
                    connect_args["check_same_thread"] = False
                
                # Para PostgreSQL (Neon), SQLAlchemy maneja el SSL mediante la URL, 
                # así que no necesitamos inyectar argumentos extras aquí.

                self.engine = create_engine(
                    self.db_url,
                    connect_args=connect_args,
                    pool_pre_ping=True  # Verifica si la conexión sigue viva (vital para Neon)
                )

                # 3. Optimizaciones específicas de motor
                if is_sqlite:
                    @event.listens_for(self.engine, "connect")
                    def set_sqlite_pragma(dbapi_connection, connection_record):
                        cursor = dbapi_connection.cursor()
                        cursor.execute("PRAGMA journal_mode=WAL")
                        cursor.execute("PRAGMA synchronous=NORMAL")
                        cursor.close()
                    logger.info("📁 DATABASE: SQLite detectado. Modo WAL y Blindaje activado.")
                else:
                    logger.info("🌐 DATABASE: PostgreSQL (Remote) detectado. Conexión segura establecida.")

                self.SessionLocal = sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self.engine
                )

            if drop_all:
                Base.metadata.drop_all(bind=self.engine)

            Base.metadata.create_all(bind=self.engine)
            logger.success(f"📁 DATABASE: Sistema de tablas materializado en {self.db_url.split(':')[0]}.")
        except Exception as e:
            logger.error(f"❌ DATABASE: Fallo al materializar tablas: {e}")

    def shutdown(self):
        """Cierra todas las conexiones del pool de forma segura."""
        if self.engine:
            self.engine.dispose()
            logger.info("📁 DATABASE: Conexiones al motor liberadas.")

    def get_session(self):
        if not self.SessionLocal:
            self.init_db()
        return self.SessionLocal()

    def save_secret(self, nombre: str, valor_plano: str):
        if not ghost or not ghost.cipher:
            logger.error(f"❌ DATABASE: No se puede cifrar '{nombre}' sin GHOST_SHELL activo.")
            return
        session = self.get_session()
        try:
            ruido = ghost.obfuscate_data(valor_plano)
            secreto = session.query(Secreto).filter_by(nombre=nombre).first()
            if secreto:
                secreto.valor_cifrado = ruido
            else:
                secreto = Secreto(nombre=nombre, valor_cifrado=ruido)
                session.add(secreto)
            session.commit()
            logger.success(f"🔒 GHOST_SHELL: Secreto '{nombre}' materializado.")
        except Exception as e:
            session.rollback()
            logger.error(f"❌ DATABASE: Error al guardar secreto: {e}")
        finally:
            session.close()

    def get_secret(self, nombre: str) -> str:
        session = self.get_session()
        try:
            secreto = session.query(Secreto).filter_by(nombre=nombre).first()
            return ghost.reveal_data(secreto.valor_cifrado) if secreto else ""
        except Exception as e:
            logger.error(f"❌ DATABASE: Error al revelar secreto: {e}")
            return ""
        finally:
            session.close()

db = DatabaseManager()

