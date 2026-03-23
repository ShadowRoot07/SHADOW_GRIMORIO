import os
from cryptography.fernet import Fernet
from pathlib import Path
from src.database.manager import db
from src.database.models import Usuario, Conocimiento
from loguru import logger

class ProfileManager:
    @staticmethod
    def es_primera_vez():
        """Verifica si el sistema necesita una inicialización completa."""
        session = db.get_session()
        try:
            user_exists = session.query(Usuario).first()
            # Es primera vez si no hay usuario en DB o si falta la Master Key en .env
            env_exists = Path(".env").exists()
            
            # Verificación extra: ¿el .env tiene contenido real?
            tiene_key = False
            if env_exists:
                with open(".env", "r") as f:
                    tiene_key = "ENCRYPTION_KEY" in f.read()

            return user_exists is None or not tiene_key
        except Exception as e:
            logger.error(f"⚠️ Error verificando estado del núcleo: {e}")
            return True # Por seguridad, asumimos que falta configurar
        finally:
            session.close()

    @staticmethod
    def generar_llave_maestra():
        """Genera y asegura la ENCRYPTION_KEY sin corromper el .env."""
        env_path = Path(".env")
        nueva_llave = Fernet.generate_key().decode()

        if not env_path.exists():
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"ENCRYPTION_KEY={nueva_llave}\n")
                f.write("SHADOW_THEME=CYBERPUNK\n")
            logger.success("🔐 [SECURITY]: Master Key generada en nuevo .env")
        else:
            with open(env_path, "r", encoding="utf-8") as f:
                lineas = f.readlines()
            
            # Verificamos si ya existe para no duplicar
            tiene_key = any("ENCRYPTION_KEY" in line for line in lineas)
            
            if not tiene_key:
                # Aseguramos que haya un salto de línea antes de añadir
                with open(env_path, "a", encoding="utf-8") as f:
                    # Si la última línea no tiene salto de línea, lo agregamos
                    f.write("\n" + f"ENCRYPTION_KEY={nueva_llave}\n")
                logger.success("🔐 [SECURITY]: Master Key inyectada con éxito.")

    @staticmethod
    def registrar_usuario(alias, lenguajes_iniciales):
        """Registra al usuario y su arsenal tecnológico inicial."""
        session = db.get_session()
        try:
            # Evitar duplicados si se llama por error dos veces
            if session.query(Usuario).filter_by(alias=alias).first():
                logger.info(f"ℹ️ El perfil de {alias} ya está registrado.")
                return

            nuevo_user = Usuario(alias=alias, rango="Iniciado de Sombras")
            session.add(nuevo_user)
            
            # Inyectamos conocimientos base (tu stack actual)
            for tech in lenguajes_iniciales:
                conocimiento = Conocimiento(
                    tecnologia=tech.strip(), 
                    dominado=True, 
                    nivel=80
                )
                session.add(conocimiento)
                
            session.commit()
            logger.success(f"⚡ [CORE]: Perfil de {alias} sellado en la base de datos.")
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error al sellar el perfil: {e}")
        finally:
            session.close()

