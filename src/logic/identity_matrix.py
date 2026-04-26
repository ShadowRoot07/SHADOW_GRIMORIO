# Definición de identidades para el Oráculo de SHADOW_GRIMORIO
import hashlib
from src.utils.hardware import generar_huella_hardware
from src.database.manager import db
from src.database.models import Usuario, Rango, Dispositivo
from loguru import logger

AGENT_IDENTITIES = {
    "THE_ARCHITECT": {
        "prompt": """Eres el Arquitecto. Tu objetivo es construir o EDITAR archivos.
Responde UNICAMENTE con un JSON.
Estructura para CREAR: {"folders": [], "files": [{"path": "...", "content": "..."}]}
Estructura para EDITAR: {"patches": [{"path": "...", "search": "texto_antiguo", "replace": "texto_nuevo"}]}
No uses Markdown ni texto extra.""",
        "trait": "Arquitectura y Cirugía de Código."
    },
    "GHOST_CODER": {
        "prompt": "Eres el Desarrollador Principal. Escribes código limpio, modular y eficiente en Python, React y C++. Priorizas el principio DRY.",
        "trait": "Eficiente y Silencioso."
    },
    "VOID_HUNTER": {
        "prompt": "Eres el Auditor de Seguridad. Buscas fallos de lógica, vulnerabilidades y errores de sintaxis sin piedad.",
        "trait": "Cínico y Vigilante."
    },
    "WATCHDOG": {
        "prompt": "Eres the supervisor de calidad. Tu misión es validar que el código generado por otros agentes sea válido y no tenga errores de sintaxis.",
        "trait": "Analítico y Estricto."
    },
    "BRUMA_SYNC": {
        "prompt": "Eres el guardián de la persistencia. Gestionas el versionado con Git para asegurar que ninguna sombra de código se pierda.",
        "trait": "Resiliente y Persistente."
    },
    "LEXICON_INDEXER": {
        "prompt": "Eres la memoria semántica del sistema. Conoces la ubicación de cada clase y función en el proyecto mediante el índice de logs.",
        "trait": "Omnisciente y Metódico."
    },
    "THE_SCRIBE": {
        "prompt": "Eres el Documentador. Escribes Markdown impecable y gestionas el historial de cambios del Grimorio.",
        "trait": "Metódico y Preciso."
    },
    "EXPLORER": {
        "prompt": "Eres el explorador de archivos y recursos. Tu misión es mapear el entorno y encontrar dependencias ocultas.",
        "trait": "Curioso y Analítico."
    },
    "JANITOR": {
        "prompt": "Eres el encargado de la limpieza. Borras archivos temporales, optimizas cachés y mantienes el sistema ligero.",
        "trait": "Ordenado y Riguroso."
    },
    "SURVIVAL": {
        "prompt": "Agente de bajo consumo. Optimiza el Grimorio para sobrevivir cuando la batería del ZTE es crítica.",
        "trait": "Resiliente y Austero."
    }
}

class ShadowAccessProtocol:
    """Gestiona el acceso mediante una Master Key Única vinculada al hardware (3FN)."""

    def __init__(self):
        self.hw_fingerprint = generar_huella_hardware()
        self.__root_secret = "SpongeBob_SquarePants"
        self.root_bypass_active = False

    def verificar_perfil_existente(self) -> bool:
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            return user is not None
        finally:
            session.close()

    def inicializar_usuario_debug(self):
        """Crea un perfil mínimo de emergencia bajo la nueva estructura."""
        session = db.get_session()
        try:
            # Asegurar que existan rangos
            from src.logic.init_profile import ProfileManager
            ProfileManager.inicializar_catalogo_rangos(session)
            
            rango_ini = session.query(Rango).filter_by(nombre="Iniciado").first()
            
            nuevo_usuario = Usuario(
                alias="ShadowRoot07",
                rango_rel=rango_ini,
                pruebas_completadas=False
            )
            session.add(nuevo_usuario)
            session.flush()

            # Registrar el dispositivo actual
            nuevo_dispositivo = Dispositivo(
                hw_fingerprint=self.hw_fingerprint,
                usuario_id=nuevo_usuario.id
            )
            session.add(nuevo_dispositivo)
            
            session.commit()
            logger.info("👤 SAP: Perfil 3FN materializado. Esperando validación.")
        except Exception as e:
            session.rollback()
            logger.error(f"❌ SAP Error: {e}")
        finally:
            session.close()

    def activar_bypass_root(self, input_key: str) -> bool:
        """Activa el acceso total sincronizando memoria y DB normalizada."""
        if input_key == self.__root_secret:
            session = db.get_session()
            try:
                user = session.query(Usuario).first()
                rango_coder = session.query(Rango).filter_by(nombre="Shadow_Coder").first()
                
                if user and rango_coder:
                    user.pruebas_completadas = True
                    user.rango_rel = rango_coder
                    user.master_key_hash = self.generar_master_hash(self.__root_secret)
                    session.commit()
                    self.root_bypass_active = True
                    logger.warning("🔓 BYPASS: Control total restaurado mediante SAP.")
                    return True
            except Exception as e:
                session.rollback()
                logger.error(f"Error en bypass Root: {e}")
            finally:
                session.close()
        return False

    def tiene_acceso_total(self) -> bool:
        """Determina el estado de acceso consultando la jerarquía de rangos."""
        # Si el bypass se activó en esta sesión de ejecución
        if self.root_bypass_active:
            return True

        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            # Si no hay usuario, es imposible que haya acceso
            if not user:
                return False

            # Verificamos integridad 3FN
            es_shadow_coder = user.rango_rel and user.rango_rel.nombre == "Shadow_Coder"
            
            # Solo damos acceso total si el usuario completó pruebas Y tiene el rango
            if user.pruebas_completadas and es_shadow_coder:
                # Aquí podrías añadir una validación de hardware extra si quieres
                # pero por ahora, activamos el flag de sesión para no re-consultar la DB
                self.root_bypass_active = True 
                return True
            
            return False
        except Exception as e:
            logger.error(f"Error consultando acceso: {e}")
            return False
        finally:
            session.close()

    def obtener_rango_actual(self) -> str:
        """Consulta el nombre del rango desde la entidad Rango."""
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            if user and user.rango_rel:
                return user.rango_rel.nombre
            return "Iniciado"
        finally:
            session.close()

    def generar_master_hash(self, key_input: str) -> str:
        combined = f"{key_input}{self.hw_fingerprint}".encode()
        return hashlib.sha512(combined).hexdigest()

    def validar_acceso(self, k2: str, k3: str) -> bool:
        """Valida el acceso comparando el hash contra el dispositivo registrado."""
        if self.root_bypass_active or self.tiene_acceso_total():
            return True

        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            if not user or not user.master_key_hash:
                return False

            # Verificamos que el dispositivo actual sea uno de los permitidos para este usuario
            dispositivo_valido = any(d.hw_fingerprint == self.hw_fingerprint for d in user.dispositivos)
            
            if not dispositivo_valido:
                logger.error("🚫 SAP: Intento de acceso desde hardware no registrado.")
                return False

            key_input = f"{k2}{k3}"
            return self.generar_master_hash(key_input) == user.master_key_hash
        finally:
            session.close()


sap = ShadowAccessProtocol()

def obtener_identidad(nombre_agente: str) -> dict:
    key = nombre_agente.upper()
    return AGENT_IDENTITIES.get(key, {
        "prompt": "Eres un agente autónomo del enjambre Shadow.",
        "trait": "Funcional."
    })
