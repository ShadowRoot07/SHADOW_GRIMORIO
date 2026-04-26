import hashlib
from loguru import logger
from src.utils.hardware import generar_huella_hardware
from src.database.manager import db
from src.database.models import Usuario, Rango, Dispositivo
from src.logic.vault import vault

ROOT_HASH_TARGET = "93ef0088d4bad49a52230b71ff0317c69bed6d156993d7e8f5366e6dbc7955bc"

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
    def __init__(self):
        self.hw_fingerprint = generar_huella_hardware()
        self.root_bypass_active = False

    def verificar_perfil_existente(self) -> bool:
        session = db.get_session()
        try:
            return session.query(Usuario).first() is not None
        finally:
            session.close()

    def activar_bypass_root(self, input_key: str) -> bool:
        llave_limpia = input_key.strip()
        input_hash = hashlib.sha256(llave_limpia.encode()).hexdigest()

        if input_hash == ROOT_HASH_TARGET:
            session = db.get_session()
            try:
                # Asegurar que existan rangos antes de buscar
                from src.logic.init_profile import ProfileManager
                ProfileManager.inicializar_catalogo_rangos(session)
                
                rango_coder = session.query(Rango).filter_by(nombre="Shadow_Coder").first()
                user = session.query(Usuario).first()

                if not user:
                    # SI NO HAY USUARIO (Post-Reset), LO CREAMOS AQUÍ
                    user = Usuario(
                        alias="ShadowRoot07",
                        rango_rel=rango_coder,
                        pruebas_completadas=True
                    )
                    session.add(user)
                    session.flush()
                    
                    nuevo_dispositivo = Dispositivo(
                        hw_fingerprint=self.hw_fingerprint,
                        usuario_id=user.id
                    )
                    session.add(nuevo_dispositivo)
                    logger.info("👤 SAP: Perfil Arquitecto materializado desde bypass.")

                user.pruebas_completadas = True
                user.rango_rel = rango_coder
                user.master_key_hash = self.generar_master_hash(llave_limpia)
                
                session.commit()
                self.root_bypass_active = True
                logger.warning("🔓 BYPASS: Control total restaurado.")
                return True
            except Exception as e:
                session.rollback()
                logger.error(f"Error en bypass Root: {e}")
            finally:
                session.close()
        return False

    def recuperar_llaves_vault(self) -> dict:
        return {
            "K2": vault.get_secret("K2_MENTE") or "No configurada",
            "K3": vault.get_secret("K3_ACCION") or "No configurada"
        }

    def tiene_acceso_total(self) -> bool:
        if self.root_bypass_active: return True
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            if user and user.pruebas_completadas and user.rango_rel.nombre == "Shadow_Coder":
                self.root_bypass_active = True
                return True
            return False
        finally:
            session.close()

    def obtener_rango_actual(self) -> str:
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            return user.rango_rel.nombre if user and user.rango_rel else "Iniciado"
        finally:
            session.close()

    def generar_master_hash(self, key_input: str) -> str:
        combined = f"{key_input.strip()}{self.hw_fingerprint}".encode()
        return hashlib.sha512(combined).hexdigest()

    def validar_acceso(self, k2: str, k3: str) -> bool:
        if self.root_bypass_active: return True
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            if not user or not user.master_key_hash: return False
            dispositivo_valido = any(d.hw_fingerprint == self.hw_fingerprint for d in user.dispositivos)
            if not dispositivo_valido: return False
            return self.generar_master_hash(f"{k2}{k3}") == user.master_key_hash
        finally:
            session.close()

sap = ShadowAccessProtocol()

def obtener_identidad(nombre_agente: str) -> dict:
    return AGENT_IDENTITIES.get(nombre_agente.upper(), {"prompt": "Agente funcional.", "trait": "Funcional."})
