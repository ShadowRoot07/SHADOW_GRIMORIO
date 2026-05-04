import hashlib
import secrets
from loguru import logger
from src.utils.hardware import generar_huella_hardware
from src.database.manager import db
from src.database.models import Usuario, Rango, Dispositivo
from src.logic.vault import vault

logger.add("debug_bypass.log", rotation="1 MB", level="DEBUG", enqueue=True)

# --- CONSTANTES DE SEGURIDAD ---
# Hash de la K2 de emergencia
K2_EMERGENCY_HASH = "0ed4e837d891cd2c8b3c5566ec2415e5470571f23d95cda456497590131df4a8"
# Hash de la K3 de emergencia
K3_EMERGENCY_HASH = "7a219c38a05c85296772a51920e55a6f7719c70133836bcb2fedd7960bc8a26d"
# Hash de la ByPass Root
ROOT_HASH_TARGET = "52b8882dde93648e680b07eab7929f9d586f4a1bcd5225a13297da32259aa2f3"
# ---------------------------------

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
        Bypass de Emergencia Protegido.
        Requiere la llave maestra de Root O una de las llaves de emergencia (K2/K3).
        """
        llave_limpia = str(input_key).strip()
        # Generamos el hash de lo que acabas de escribir para comparar
        input_hash = hashlib.sha256(llave_limpia.encode('utf-8')).hexdigest()

        # 1. VALIDACIÓN: ¿Lo que metiste es la clave Root, la K2 de emergencia o la K3?
        is_root = input_hash == ROOT_HASH_TARGET
        is_k2 = input_hash == K2_EMERGENCY_HASH
        is_k3 = input_hash == K3_EMERGENCY_HASH

        if is_root or is_k2 or is_k3:
            logger.warning(f"⚠️ [SAP]: Bypass validado mediante {'ROOT' if is_root else 'EMERGENCY_KEY'}.")
            
            session = db.get_session()
            try:
                from src.logic.init_profile import ProfileManager
                ProfileManager.inicializar_catalogo_rangos(session)
                
                rango_coder = session.query(Rango).filter_by(nombre="Shadow_Coder").first()
                user = session.query(Usuario).first()

                # --- PASO C: SINCRONIZACIÓN DE IDENTIDAD ---
                # Si entraste con K2 o K3, usamos ESA llave para re-sellar el vault
                # Si entraste con ROOT, el sistema usará las llaves que ya existan o pedirá Wizard
                if is_k2:
                    vault.store_secret("K2_MENTE", llave_limpia)
                    logger.info("🔒 K2 sincronizada desde emergencia.")
                elif is_k3:
                    vault.store_secret("K3_ACCION", llave_limpia)
                    logger.info("🔒 K3 sincronizada desde emergencia.")

                # Recuperamos lo que haya en el vault para reconstruir el Master Hash
                k2_actual = vault.get_secret("K2_MENTE")
                k3_actual = vault.get_secret("K3_ACCION")

                if not k2_actual or not k3_actual:
                    logger.error("❌ [SAP]: Vault incompleto. No se puede generar Master Hash.")
                    return False

                llave_maestra_ritual = f"{k2_actual}{k3_actual}"

                # --- PASO D: MATERIALIZACIÓN ---
                if not user:
                    logger.info("🆕 [SAP]: Creando cuenta desde Bypass...")
                    user = Usuario(
                        alias="ShadowRoot07",
                        rango_rel=rango_coder,
                        pruebas_completadas=True,
                        progreso_trials="COMPLETO",
                        master_key_hash=self.generar_master_hash(llave_maestra_ritual)
                    )
                    session.add(user)
                else:
                    # Sincronizamos el hash de la DB con lo que tenemos en el Vault
                    user.rango_rel = rango_coder
                    user.master_key_hash = self.generar_master_hash(llave_maestra_ritual)
                    user.pruebas_completadas = True
                    user.progreso_trials = "COMPLETO"

                session.commit()
                self.root_bypass_active = True
                logger.success("✅ [SAP]: Acceso nivel Arquitecto concedido.")
                return True

            except Exception as e:
                session.rollback()
                logger.error(f"❌ [SAP]: Error en operación de bypass: {e}")
                return False
            finally:
                session.close()
        
        logger.error("🚫 [SAP]: Hash de entrada no reconocido.")
        return False

    def recuperar_llaves_vault(self) -> dict:
        return {
            "K2": vault.get_secret("K2_MENTE") or "ERROR_GEN",
            "K3": vault.get_secret("K3_ACCION") or "ERROR_GEN"
        }

    def tiene_acceso_total(self) -> bool:
        if self.root_bypass_active:
            return True

        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            if not user: return False

            # Si NO ha terminado pruebas, acceso_total es siempre False
            if not user.pruebas_completadas:
                return False

            # Si YA terminó pruebas y es Shadow_Coder, 
            # solo devolvemos True si el bypass (login) está activo.
            if user.rango_rel and user.rango_rel.nombre == "Shadow_Coder":
                return self.root_bypass_active
                
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
        # Forzamos limpieza absoluta: sin espacios, todo minúsculas
        llave_final = str(key_input).replace(" ", "").strip().lower()
        huella = generar_huella_hardware().strip()
        
        combined = f"{llave_final}{huella}".encode('utf-8')
        return hashlib.sha512(combined).hexdigest()


    def validar_acceso(self, k2: str, k3: str) -> bool:
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            if not user or not user.master_key_hash:
                logger.error("❌ [SAP]: No hay usuario o hash en la DB.")
                return False

            llave_combinada = f"{k2.strip()}{k3.strip()}"
            hash_intento = self.generar_master_hash(llave_combinada)

            # --- NUEVOS LOGS DE RASTREO PROFUNDO ---
            logger.debug(f"🧪 [TRACE] Llave Combinada: {llave_combinada[:4]}...{llave_combinada[-4:]}")
            logger.debug(f"🧪 [TRACE] Hash Generado: {hash_intento[:10]}...")
            logger.debug(f"🧪 [TRACE] Hash en DB:    {user.master_key_hash[:10]}...")
            # ---------------------------------------

            if hash_intento == user.master_key_hash:
                self.root_bypass_active = True
                logger.success(f"✅ [SAP]: Ritual exitoso.")
                return True

            logger.error(f"❌ [SAP]: Hash mismatch.")
            return False
        finally:
            session.close()


sap = ShadowAccessProtocol()

def obtener_identidad(nombre_agente: str) -> dict:
    return AGENT_IDENTITIES.get(nombre_agente.upper(), {"prompt": "Agente funcional.", "trait": "Funcional."})
