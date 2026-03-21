from src.database.manager import db
from src.database.models import Usuario, Conocimiento
from loguru import logger

class ProfileManager:
    @staticmethod
    def es_primera_vez():
        session = db.get_session()
        try:
            existe = session.query(Usuario).first()
            return existe is None
        finally:
            session.close()

    @staticmethod
    def registrar_usuario(alias, lenguajes_iniciales):
        session = db.get_session()
        try:
            # 1. Crear el perfil de ShadowRoot07
            nuevo_user = Usuario(alias=alias, rango="Iniciado de Sombras")
            session.add(nuevo_user)
            
            # 2. Registrar lo que ya sabes (Python, C++, etc.)
            for tech in lenguajes_iniciales:
                conocimiento = Conocimiento(tecnologia=tech, dominado=True, nivel=80)
                session.add(conocimiento)
                
            session.commit()
            logger.success(f"Perfil de {alias} sincronizado con el núcleo.")
        except Exception as e:
            session.rollback()
            logger.error(f"Error al sellar el perfil: {e}")
        finally:
            session.close()

