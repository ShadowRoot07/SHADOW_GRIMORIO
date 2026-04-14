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
        "prompt": "Eres el supervisor de calidad. Tu misión es validar que el código generado por otros agentes sea válido y no tenga errores de sintaxis.",
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
    """Gestiona el acceso escalonado y las 4 llaves del usuario."""

    def __init__(self):
        self.hw_fingerprint = generar_huella_hardware()

    def verificar_perfil_existente(self) -> bool:
        """Comprueba si existe algún usuario en la base de datos."""
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            return user is not None
        finally:
            session.close()

    def inicializar_usuario_debug(self):
        """Crea el perfil inicial tras un reset de DB para iniciar el SAP."""
        session = db.get_session()
        try:
            nuevo_usuario = Usuario(
                alias="ShadowRoot07",
                rango="Iniciado",
                pruebas_completadas=False
            )
            session.add(nuevo_usuario)
            session.commit()
            logger.info("👤 SAP: Perfil de 'Iniciado' materializado con éxito.")
        except Exception as e:
            session.rollback()
            logger.error(f"❌ SAP: Error al crear perfil inicial: {e}")
        finally:
            session.close()

    def generar_super_key(self, k1: str, k2: str, k3: str) -> str:
        """La 4ta Llave: La Super Key que orquesta el sistema."""
        combined = f"{k1}{k2}{k3}".encode()
        return hashlib.sha512(combined).hexdigest()

    def validar_acceso(self, k2_input: str, k3_input: str) -> bool:
        """Valida las llaves contra la Super Key guardada."""
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            if not user or not user.super_key_hash:
                return False

            test_super_key = self.generar_super_key(user.key_hash_1, k2_input, k3_input)
            return test_super_key == user.super_key_hash
        finally:
            session.close()

# Instancia global del protocolo
sap = ShadowAccessProtocol()

def obtener_identidad(nombre_agente: str) -> dict:
    key = nombre_agente.upper()
    return AGENT_IDENTITIES.get(key, {
        "prompt": "Eres un agente autónomo del enjambre Shadow.",
        "trait": "Funcional."
    })

