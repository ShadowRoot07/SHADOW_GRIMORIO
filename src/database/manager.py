from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
from src.logic.config import config
from loguru import logger

class DatabaseManager:
    """Orquestador de persistencia Local/Remota."""

    def __init__(self):
        self.db_url = str(config.database_url)

        try:
            self.engine = create_engine(self.db_url)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info(f"Conexión establecida con el Oráculo de Datos.")
            # Intentar crear tablas al iniciar por seguridad
            self.init_db()
        except Exception as e:
            logger.error(f"Error crítico de conexión: {e}")
            raise

    def init_db(self):
        """Crea las tablas si no existen."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.success("Estructuras de memoria (Tablas) sincronizadas.")
        except Exception as e:
            logger.error(f"Fallo al materializar tablas: {e}")

    def get_session(self):
        """Provee una sesión para realizar operaciones."""
        return self.SessionLocal()

# Instancia global
db = DatabaseManager()

