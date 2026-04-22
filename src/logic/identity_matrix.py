# Definición de identidades para el Oráculo de SHADOW_GRIMORIO
import hashlib
from src.utils.hardware import generar_huella_hardware
from src.database.manager import db
from src.database.models import Usuario
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
    """Gestiona el acceso mediante una Master Key Única vinculada al hardware."""

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
        session = db.get_session()
        try:
            nuevo_usuario = Usuario(
                alias="ShadowRoot07",
                rango="Iniciado",
                pruebas_completadas=False,
                hw_fingerprint=self.hw_fingerprint
            )
            session.add(nuevo_usuario)
            session.commit()
            logger.info("👤 SAP: Perfil materializado. Esperando validación técnica.")
        except Exception as e:
            session.rollback()
            logger.error(f"❌ SAP Error: {e}")
        finally:
            session.close()

    def activar_bypass_root(self, input_key: str) -> bool:
        """Activa el acceso total si la llave coincide con el secreto del Arquitecto."""
        if input_key == self.__root_secret:
            self.root_bypass_active = True
            session = db.get_session()
            try:
                user = session.query(Usuario).first()
                if user:
                    user.pruebas_completadas = True
                    user.rango = "Shadow_Coder"
                    user.master_key_hash = self.generar_master_hash(self.__root_secret)
                    session.commit()
                    logger.warning("🔓 BYPASS: El Arquitecto ha tomado control total.")
                    return True
            except Exception as e:
                session.rollback()
                logger.error(f"Error en bypass Root: {e}")
            finally:
                session.close()
        return False

    def generar_master_hash(self, key_input: str) -> str:
        combined = f"{key_input}{self.hw_fingerprint}".encode()
        return hashlib.sha512(combined).hexdigest()

    def validar_acceso(self, k2: str, k3: str) -> bool:
        """Valida las llaves del ritual o el bypass root."""
        # 1. Prioridad: Bypass en memoria o Rango en DB
        if self.root_bypass_active or self.tiene_acceso_total():
            return True

        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            if not user or not user.master_key_hash:
                return False

            key_input = f"{k2}{k3}"
            return self.generar_master_hash(key_input) == user.master_key_hash
        finally:
            session.close()

    def tiene_acceso_total(self) -> bool:
        """Verifica si el usuario tiene privilegios elevados (Persistente)."""
        if self.root_bypass_active:
            return True
            
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            if not user: 
                return False
            # Si el usuario ya es Shadow_Coder en DB, sincronizamos la memoria
            if user.pruebas_completadas and user.rango == "Shadow_Coder":
                self.root_bypass_active = True
                return True
            return False
        finally:
            session.close()

sap = ShadowAccessProtocol()

def obtener_identidad(nombre_agente: str) -> dict:
    key = nombre_agente.upper()
    return AGENT_IDENTITIES.get(key, {
        "prompt": "Eres un agente autónomo del enjambre Shadow.",
        "trait": "Funcional."
    })
