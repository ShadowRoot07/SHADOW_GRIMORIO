import sys
from pathlib import Path

# Asegurar que Python vea la carpeta 'src' desde la raíz
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.database.manager import db
from src.database.models import Rango, Usuario # <--- AQUÍ ESTABA EL FALLO
from loguru import logger

def sanear_sistema():
    logger.info("🔧 Iniciando saneamiento de cimientos...")
    db.init_db()
    
    # Definimos los motores a sanear
    motores = [("Local", db.SessionLocal)]
    if db.online:
        motores.append(("Neon", db.SessionRemote))

    rangos_definidos = [
        (1, "Iniciado", 1),
        (2, "Shadow_Coder", 2),
        (3, "Arquitecto", 3)
    ]

    for nombre_engine, SessionClass in motores:
        if SessionClass is None:
            logger.warning(f"⚠️ {nombre_engine} no está disponible.")
            continue

        logger.info(f"⚙️ Saneando {nombre_engine}...")
        session = SessionClass()
        try:
            for rid, nombre, nivel in rangos_definidos:
                # Buscamos si existe por ID o por Nombre para evitar UniqueViolation
                existe = session.query(Rango).filter(
                    (Rango.id == rid) | (Rango.nombre == nombre)
                ).first()

                if not existe:
                    nuevo_rango = Rango(id=rid, nombre=nombre, nivel_acceso=nivel)
                    session.add(nuevo_rango)
                    logger.info(f"   [+] Inyectado: {nombre}")
                else:
                    # Si existe pero los datos no coinciden, lo actualizamos (Alineación)
                    existe.nombre = nombre
                    existe.nivel_acceso = nivel
                    logger.info(f"   [=] Sincronizado: {nombre}")
            
            session.commit()
            logger.success(f"✅ {nombre_engine} alineado correctamente.")
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Fallo crítico en {nombre_engine}: {e}")
        finally:
            session.close()

if __name__ == "__main__":
    sanear_sistema()

