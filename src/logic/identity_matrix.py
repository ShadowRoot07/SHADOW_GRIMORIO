import hashlib
import secrets
from loguru import logger
from src.utils.hardware import generar_huella_hardware
from src.database.manager import db
from src.database.models import Usuario, Rango, Dispositivo
from src.logic.vault import vault

logger.add("debug_bypass.log", rotation="1 MB", level="DEBUG", enqueue=True)


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
        """
        Protocolo de Bypass de Emergencia (Nivel Arquitecto).
        Valida contra el hash SHA-256 pre-calculado.
        """
        # 1. Normalización y Limpieza de entrada
        # Convertimos a string y aplicamos strip para eliminar saltos de línea invisibles
        llave_limpia = str(input_key).strip()
        
        # 2. Generación del hash de comparación (Forzamos UTF-8 para consistencia total)
        # El hash debe ser idéntico al del script check_hash.py
        input_hash = hashlib.sha256(llave_limpia.encode('utf-8')).hexdigest()

        # 3. Validación contra el Objetivo (ROOT_HASH_TARGET)
        if input_hash == ROOT_HASH_TARGET:
            logger.warning(f"⚠️ [SAP]: Bypass activado. Hash validado para: {llave_limpia[:4]}...")
            
            session = db.get_session()
            try:
                # Importación diferida para evitar colisiones de dependencias
                from src.logic.init_profile import ProfileManager
                
                # Paso A: Asegurar integridad de Catálogo de Rangos
                ProfileManager.inicializar_catalogo_rangos(session)
                session.commit()

                # Paso B: Recuperar Rango y Usuario
                rango_coder = session.query(Rango).filter_by(nombre="Shadow_Coder").first()
                user = session.query(Usuario).first()

                # Paso C: Gestión del Vault (K2/K3)
                # Si el vault está vacío, generamos llaves persistentes de 16 caracteres hex
                if not vault.get_secret("K2_MENTE"):
                    vault.store_secret("K2_MENTE", secrets.token_hex(8).upper())
                if not vault.get_secret("K3_ACCION"):
                    vault.store_secret("K3_ACCION", secrets.token_hex(8).upper())

                # Paso D: Materialización de Identidad
                if not user:
                    # Caso: Base de datos virgen
                    user = Usuario(
                        alias="ShadowRoot07",
                        rango_rel=rango_coder,
                        pruebas_completadas=True
                    )
                    session.add(user)
                    session.flush() # Para obtener el ID del usuario antes de añadir dispositivo
                    
                    # Asociar el hardware actual como dispositivo autorizado
                    nuevo_dispositivo = Dispositivo(
                        hw_fingerprint=self.hw_fingerprint,
                        usuario_id=user.id
                    )
                    session.add(nuevo_dispositivo)
                else:
                    # Caso: Usuario existente, forzar ascenso de privilegios
                    user.rango_rel = rango_coder
                    user.pruebas_completadas = True

                # Paso E: Sincronizar Master Key (Persistencia SHA-512)
                # IMPORTANTE: Se usa generar_master_hash que mezcla llave + HW_Fingerprint
                user.master_key_hash = self.generar_master_hash(llave_limpia)

                session.commit()
                
                # Paso F: Activación de estado en memoria
                self.root_bypass_active = True
                logger.success("✅ [SAP]: Acceso nivel Arquitecto concedido. Sesión activa.")
                return True

            except Exception as e:
                session.rollback()
                logger.error(f"❌ [SAP]: Fallo en la persistencia del bypass: {e}")
                return False
            finally:
                session.close()
        
        # Si no hay coincidencia de hash, cerramos la puerta sin procesar DB
        else:
            logger.error(f"🚫 [SAP]: Intento de bypass fallido. Hash no reconocido.")
            return False

    def recuperar_llaves_vault(self) -> dict:
        return {
            "K2": vault.get_secret("K2_MENTE") or "ERROR_GEN",
            "K3": vault.get_secret("K3_ACCION") or "ERROR_GEN"
        }

    def tiene_acceso_total(self) -> bool:
        # Si ya activamos el bypass en esta sesión de memoria, no preguntes a la DB
        if self.root_bypass_active: 
            return True
            
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            if user and user.pruebas_completadas and user.rango_rel and user.rango_rel.nombre == "Shadow_Coder":
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
        # Unificamos el formato: llave + huella
        combined = f"{key_input.strip()}{self.hw_fingerprint}".encode('utf-8')
        return hashlib.sha512(combined).hexdigest()

sap = ShadowAccessProtocol()

def obtener_identidad(nombre_agente: str) -> dict:
    return AGENT_IDENTITIES.get(nombre_agente.upper(), {"prompt": "Agente funcional.", "trait": "Funcional."})
