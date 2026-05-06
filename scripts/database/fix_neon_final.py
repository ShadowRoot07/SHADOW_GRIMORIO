import sys
from pathlib import Path

# Forzar que Python encuentre la carpeta 'src'
base_dir = Path(__file__).resolve().parents[2]
if str(base_dir) not in sys.path:
    sys.path.insert(0, str(base_dir))

from src.database.manager import db
from src.database.models import Rango
from loguru import logger

def ritual_de_alineacion():
    logger.info("📡 Inicializando motores duales...")
    # PASO CRÍTICO: Arrancar los motores de la DB
    db.init_db() 
    
    if not db.online:
        logger.error("❌ No se puede alinear: Neon está fuera de línea.")
        return

    logger.info("📡 Conectando con Neon para inyectar rangos...")
    session = db.SessionRemote() 
    
    try:
        # Definimos los rangos que Neon NECESITA conocer
        rangos_maestros = [
            {"id": 1, "nombre": "Iniciado", "descripcion": "Recién llegado."},
            {"id": 2, "nombre": "Shadow_Coder", "descripcion": "Arquitecto de sombras."}
        ]
        
        for data in rangos_maestros:
            existe = session.query(Rango).filter_by(id=data['id']).first()
            if not existe:
                logger.warning(f"Inyectando Rango {data['id']} ({data['nombre']})...")
                nuevo = Rango(**data)
                session.add(nuevo)
            else:
                logger.info(f"Rango {data['id']} ya presente en Neon.")
        
        session.commit()
        logger.success("✅ Neon alineado. El error de ForeignKey debería desaparecer.")
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Fallo en la inyección: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    ritual_de_alineacion()

