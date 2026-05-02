import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context

# Añadimos la raíz del proyecto al path para que Python encuentre 'src'
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), '..')))

# --- IMPORTACIONES DEL GRIMORIO ---
from src.database.models import Base
from src.database.manager import db # Importamos tu orquestador

# Configuración de logs de Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 1. VINICULACIÓN DE METADATOS (Para Autogenerate)
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Modo offline: genera scripts SQL sin conectarse."""
    # Prioridad: URL local de tu manager
    url = db.url_local
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Modo online: se conecta físicamente a la DB."""
    # Usamos la URL local por defecto para las migraciones en el ZTE
    # Si quieres migrar Neon, podrías cambiar esto a db.url_remote
    connectable = create_engine(db.url_local, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

