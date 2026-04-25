import os
from cryptography.fernet import Fernet
from pathlib import Path
from src.database.manager import db
from src.database.models import Usuario, Rango, Dispositivo, Preferencia, Conocimiento
from loguru import logger

class ProfileManager:
    @staticmethod
    def es_primera_vez():
        """Verifica si el sistema necesita una inicialización completa."""
        env_path = Path(".env")
        tiene_key = False
        if env_path.exists():
            with open(env_path, "r") as f:
                content = f.read()
                tiene_key = "ENCRYPTION_KEY" in content and len(content.split("ENCRYPTION_KEY=")[1].strip()) > 0

        if not tiene_key:
            return True

        try:
            session = db.get_session()
            # Verificamos si existe al menos un usuario en la nueva estructura
            user = session.query(Usuario).first()
            session.close()
            return user is None
        except Exception as e:
            logger.warning(f"⚠️ Estructura de DB incompatible detectada: {e}")
            return True

    @staticmethod
    def inicializar_catalogo_rangos(session):
        """Asegura que la tabla de Rangos esté poblada según 3FN."""
        rangos_definidos = [
            ("Iniciado", 1),
            ("Shadow_Coder", 2),
            ("Arquitecto", 3)
        ]
        for nombre, nivel in rangos_definidos:
            existe = session.query(Rango).filter_by(nombre=nombre).first()
            if not existe:
                session.add(Rango(nombre=nombre, nivel_acceso=nivel))
        session.flush()

    @staticmethod
    def registrar_usuario(alias, raw_master_key):
        """Sella el perfil normalizado con Master Key y hardware vinculado."""
        from src.logic.identity_matrix import sap
        session = db.get_session()
        try:
            # 1. Preparar Catálogo de Rangos
            ProfileManager.inicializar_catalogo_rangos(session)
            
            # 2. Limpiar datos antiguos para evitar conflictos de integridad
            session.query(Preferencia).delete()
            session.query(Dispositivo).delete()
            session.query(Usuario).delete()

            # 3. Obtener Rango objetivo
            rango_coder = session.query(Rango).filter_by(nombre="Shadow_Coder").first()

            # 4. Crear Usuario
            nuevo_user = Usuario(
                alias=alias,
                rango_rel=rango_coder,
                master_key_hash=sap.generar_master_hash(raw_master_key),
                pruebas_completadas=True
            )
            session.add(nuevo_user)
            session.flush() # Para obtener el ID del nuevo_user

            # 5. Vincular Hardware y Preferencias (3FN)
            nuevo_dispositivo = Dispositivo(
                hw_fingerprint=sap.hw_fingerprint,
                nombre_modelo="ZTE Blade A54",
                usuario_id=nuevo_user.id
            )
            nuevas_prefs = Preferencia(
                tema="CYBERPUNK",
                usuario_id=nuevo_user.id
            )
            
            # 6. Conocimientos Base
            tech_base = [
                Conocimiento(tecnologia="Python", nivel=8),
                Conocimiento(tecnologia="FastAPI", nivel=7),
                Conocimiento(tecnologia="PostgreSQL", nivel=7)
            ]
            
            session.add_all([nuevo_dispositivo, nuevas_prefs])
            session.add_all(tech_base)

            session.commit()
            logger.success(f"⚡ [CORE]: Perfil 3FN de {alias} materializado con éxito.")
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error al sellar perfil normalizado: {e}")
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

