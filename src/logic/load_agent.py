from src.utils.hardware_bridge import hw
from src.database.manager import db
from src.database.models import Conocimiento
import platform
import os
from loguru import logger

class LoadOrchestrator:
    """Agente encargado de decidir el destino de la ejecución (Local vs Cloud)."""

    def __init__(self):
        self.specs = hw.obtener_specs()
        self.dispositivo = "ZTE Blade A54" # Identificador de tu modelo
        self.umbral_ram = 1500  # MB: Si la tarea requiere más, va a la nube
        self.apps_instaladas = self._escanear_entorno()

    def _escanear_entorno(self):
        """Historial de herramientas disponibles en Termux."""
        herramientas = ["clang", "make", "python", "node", "git", "docker"]
        instaladas = []
        for tool in herramientas:
            if os.system(f"command -v {tool} > /dev/null 2>&1") == 0:
                instaladas.append(tool)
        return instaladas

    def analizar_tarea(self, tipo_tarea: str, complejidad: str):
        """
        Decide si se ejecuta localmente o vía Workflow.
        complejidad: 'baja', 'media', 'alta'
        """
        decision_local = True
        razon = "Capacidad local suficiente."

        # Lógica de decisión basada en hardware y software
        if self.specs['ram_mb'] < self.umbral_ram and complejidad == 'alta':
            decision_local = False
            razon = f"RAM insuficiente en {self.dispositivo} para tarea pesada."
        
        if "clang" not in self.apps_instaladas and tipo_tarea == "compilacion_cpp":
            decision_local = False
            razon = "Compilador C++ no detectado en el entorno local."

        return {
            "local": decision_local,
            "destino": "TERMUX" if decision_local else "GITHUB_ACTIONS",
            "razon": razon,
            "modelo_dispositivo": self.dispositivo
        }

    def notificar_estado(self, fase: str, archivo: str = ""):
        """Notifica cuando se crea o termina un proceso del agente."""
        if fase == "inicio_workflow":
            logger.warning(f"⚠️ [ORQUESTADOR]: Creando manifiesto YAML para {archivo}...")
        elif fase == "fin_compilacion":
            logger.success(f"✨ [ORQUESTADOR]: Tarea finalizada en el destino.")

# Instancia del Agente
load_agent = LoadOrchestrator()

