import os
from cryptography.fernet import Fernet
from pathlib import Path
from src.database.manager import db
from src.database.models import Usuario, Conocimiento
from loguru import logger

class ProfileManager:
    @staticmethod
    def es_primera_vez():
        # Mantenemos tu lógica de DB
        session = db.get_session()
        try:
            existe = session.query(Usuario).first()
            # Si no hay usuario O no hay archivo .env, es primera vez
            return existe is None or not Path(".env").exists()
        finally:
            session.close()

    @staticmethod
    def generar_llave_maestra():
        """Genera y asegura la ENCRYPTION_KEY en el archivo .env."""
        env_path = Path(".env")
        nueva_llave = Fernet.generate_key().decode()
        
        if not env_path.exists():
            with open(env_path, "w") as f:
                f.write(f"ENCRYPTION_KEY={nueva_llave}\n")
                f.write("SHADOW_THEME=CYBERPUNK\n")
            logger.success("🔐 [SECURITY]: Master Key generada en nuevo .env")
        else:
            with open(env_path, "r") as f:
                contenido = f.read()
            if "ENCRYPTION_KEY" not in contenido:
                with open(env_path, "a") as f:
                    f.write(f"\nENCRYPTION_KEY={nueva_llave}")
                logger.success("🔐 [SECURITY]: Master Key inyectada en .env existente.")

    @staticmethod
    def registrar_usuario(alias, lenguajes_iniciales):
        # ... (Tu lógica original de registro de usuario se mantiene exactamente igual)
        session = db.get_session()
        try:
            nuevo_user = Usuario(alias=alias, rango="Iniciado de Sombras")
            session.add(nuevo_user)
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

