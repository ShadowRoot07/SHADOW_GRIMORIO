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
        # 1. Capa de Seguridad (.env)
        env_path = Path(".env")
        tiene_key = False
        if env_path.exists():
            with open(env_path, "r") as f:
                content = f.read()
                tiene_key = "ENCRYPTION_KEY" in content and len(content.split("ENCRYPTION_KEY=")[1].strip()) > 0

        if not tiene_key:
            return True

        # 2. Capa de Datos (Usuario)
        try:
            session = db.get_session()
            user = session.query(Usuario).first()
            session.close()
            return user is None
        except Exception as e:
            # Captura errores de columnas faltantes o tablas inexistentes
            logger.warning(f"⚠️ Estructura de DB antigua o corrupta detectada: {e}")
            # En caso de error de esquema, asumimos que es necesario re-inicializar
            return True

    @staticmethod
    def registrar_usuario(alias, raw_master_key):
        """Sella el perfil con la Master Key única y huella de hardware."""
        from src.logic.identity_matrix import sap
        session = db.get_session()
        try:
            # Limpiar perfiles antiguos para evitar colisiones de Master Key
            session.query(Usuario).delete()

            nuevo_user = Usuario(
                alias=alias,
                rango="Shadow_Coder",
                hw_fingerprint=sap.hw_fingerprint,
                master_key_hash=sap.generar_master_hash(raw_master_key),
                pruebas_completadas=True
            )
            session.add(nuevo_user)
            
            # Inicializar conocimientos base (opcional)
            tech_base = [
                Conocimiento(tecnologia="Python", dominado=True, nivel=8),
                Conocimiento(tecnologia="FastAPI", dominado=True, nivel=7),
                Conocimiento(tecnologia="PostgreSQL", dominado=True, nivel=7)
            ]
            session.add_all(tech_base)
            
            session.commit()
            logger.success(f"⚡ [CORE]: Perfil de {alias} sellado con éxito.")
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error al sellar el perfil: {e}")
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
            logger.success("🔐 [SECURITY]: Master Key generada.")
        else:
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if not any("ENCRYPTION_KEY" in line for line in lines):
                with open(env_path, "a", encoding="utf-8") as f:
                    f.write(f"\nENCRYPTION_KEY={nueva_llave}\n")
                logger.success("🔐 [SECURITY]: Master Key inyectada.")

