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
        # 1. Verificar existencia de .env y ENCRYPTION_KEY
        env_path = Path(".env")
        tiene_key = False
        if env_path.exists():
            with open(env_path, "r") as f:
                content = f.read()
                tiene_key = "ENCRYPTION_KEY" in content and len(content.split("ENCRYPTION_KEY=")[1].strip()) > 0
        
        if not tiene_key:
            return True

        # 2. Verificar existencia de usuario en DB
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            return user is None
        except Exception as e:
            # Si la tabla no existe o la columna está mal, es mejor re-inicializar
            logger.warning(f"⚠️ Estructura de DB antigua o corrupta detectada: {e}")
            return True 
        finally:
            session.close()

    @staticmethod
    def generar_llave_maestra():
        """Genera y asegura la ENCRYPTION_KEY en el .env."""
        env_path = Path(".env")
        nueva_llave = Fernet.generate_key().decode()

        if not env_path.exists():
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"ENCRYPTION_KEY={nueva_llave}\n")
                f.write("SHADOW_THEME=CYBERPUNK\n")
            logger.success("🔐 [SECURITY]: Master Key generada en nuevo .env")
        else:
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            if not any("ENCRYPTION_KEY" in line for line in lines):
                with open(env_path, "a", encoding="utf-8") as f:
                    f.write(f"\nENCRYPTION_KEY={nueva_llave}\n")
                logger.success("🔐 [SECURITY]: Master Key inyectada con éxito.")

    @staticmethod
    def registrar_usuario(alias, k1, k2, k3, super_key):
        """Sella el perfil del programador con sus llaves SAP."""
        session = db.get_session()
        try:
            # Limpiamos cualquier rastro previo para evitar conflictos de ID
            session.query(Usuario).delete()
            
            nuevo_user = Usuario(
                alias=alias,
                rango="Arquitecto Digital",
                hw_fingerprint=k1,
                super_key_hash=super_key,
                pruebas_completadas=1
            )
            session.add(nuevo_user)

            # Stack tecnológico inicial (ShadowRoot07 Essentials)
            tech_base = ["Python", "FastAPI", "React", "PostgreSQL", "NeoVim", "Termux"]
            for tech in tech_base:
                conocimiento = Conocimiento(tecnologia=tech, dominado=True, nivel=90)
                session.add(conocimiento)

            session.commit()
            logger.success(f"⚡ [CORE]: Perfil de {alias} sellado y encriptado.")
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error al sellar el perfil: {e}")
        finally:
            session.close()

