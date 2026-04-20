from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.database.models import Base, Secreto
from src.logic.config import config
from src.logic.ghost_shell import ghost
from loguru import logger

class DatabaseManager:
    """Orquestador de persistencia con soporte para GHOST_SHELL."""

    def __init__(self):
        self.db_url = str(config.database_url)
        self.engine = None
        self.SessionLocal = None

    def init_db(self, drop_all: bool = False):
        """Materializa las tablas y gestiona la integridad del esquema."""
        try:
            if not self.engine:
                self.engine = create_engine(self.db_url)
                self.SessionLocal = sessionmaker(
                    autocommit=False,
                    autoflush=False,
                    bind=self.engine
                )

            if drop_all:
                logger.warning("⚠️ DATABASE: Ejecutando purga total de tablas...")
                Base.metadata.drop_all(bind=self.engine)

            Base.metadata.create_all(bind=self.engine)
            logger.success("📁 DATABASE: Memoria sincronizada y Bóveda preparada.")
        except Exception as e:
            logger.error(f"❌ DATABASE: Fallo al materializar tablas: {e}")

    def get_session(self):
        if not self.SessionLocal:
            self.init_db()
        return self.SessionLocal()

    def save_secret(self, nombre: str, valor_plano: str):
        """Cifra y guarda un secreto en la base de datos."""
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
        """Recupera y descifra un secreto de la bóveda."""
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

