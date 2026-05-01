import os
from cryptography.fernet import Fernet
from pathlib import Path
from src.database.manager import db
from src.database.models import Usuario, Rango, Dispositivo, Preferencia, Conocimiento
from loguru import logger

class ProfileManager:
    @staticmethod
    def es_primera_vez():
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            # Si hay usuario Y tiene un master_key_hash, ya no es primera vez
            if user and user.master_key_hash:
                return False
            return user is None
        finally:
            session.close()

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
        
        # --- NORMALIZACIÓN DE ENTRADA ---
        # Aseguramos que la llave se limpie igual que en el login (Ritual)
        llave_limpia = str(raw_master_key).strip()
        
        logger.critical(f"🛠️ [DB_INIT]: Iniciando proceso de registro para {alias}")
        logger.debug(f"🔑 [DEBUG_INIT]: Usando HW_FINGERPRINT: {sap.hw_fingerprint[:8]}...")
        
        try:
            # 1. Preparar Catálogo de Rangos
            ProfileManager.inicializar_catalogo_rangos(session)

            # 2. Limpiar datos antiguos para evitar conflictos
            session.query(Preferencia).delete()
            session.query(Dispositivo).delete()
            session.query(Usuario).delete()

            # 3. Obtener Rango 'Iniciado'
            rango_inicio = session.query(Rango).filter_by(nombre="Iniciado").first()

            # 4. Crear Usuario con el hash generado por el protocolo SAP
            nuevo_user = Usuario(
                alias=alias,
                rango_rel=rango_inicio,
                # USAMOS LA LLAVE LIMPIA QUE VIENE DEL WIZARD
                master_key_hash=sap.generar_master_hash(llave_limpia), 
                pruebas_completadas=False,
                progreso_trials="F1_S1_P0"
            )

            logger.critical(f"💉 [DB_INJECTION]: Objeto creado. Pruebas={nuevo_user.pruebas_completadas} | Rango={rango_inicio.nombre}")

            session.add(nuevo_user)
            session.commit()

            logger.success("✅ [DB_WRITE]: Commit inicial completado.")
            session.refresh(nuevo_user)
            
            # 5. Vincular Hardware y Preferencias (Mantenemos tu lógica 3FN)
            nuevo_dispositivo = Dispositivo(
                hw_fingerprint=sap.hw_fingerprint, # <--- USAMOS LA HUELLA ACTUAL DE SAP
                nombre_modelo="ZTE Blade A54",
                usuario_id=nuevo_user.id
            )
            nuevas_prefs = Preferencia(
                tema="CYBERPUNK",
                usuario_id=nuevo_user.id
            )

            # 6. Conocimientos Base (Mantenemos tus datos de ShadowRoot07)
            tech_base = [
                Conocimiento(tecnologia="Python", nivel=8, usuario_id=nuevo_user.id),
                Conocimiento(tecnologia="FastAPI", nivel=7, usuario_id=nuevo_user.id),
                Conocimiento(tecnologia="PostgreSQL", nivel=7, usuario_id=nuevo_user.id)
            ]

            session.add_all([nuevo_dispositivo, nuevas_prefs])
            session.add_all(tech_base)

            session.commit()
            logger.success(f"⚡ [CORE]: Perfil de {alias} materializado. HW_ID vinculado: {sap.hw_fingerprint[:8]}...")
            
        except Exception as e:
            logger.critical(f"💥 [DB_FATAL]: Error en la transacción: {e}")
            session.rollback()
            logger.error(f"❌ Error al sellar perfil: {e}")
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

