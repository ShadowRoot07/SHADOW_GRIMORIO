import subprocess
import os
import sys
import pkgutil
import importlib
import json
from loguru import logger

class AgentManager:
    """Maneja agentes como Daemons con persistencia de estado."""

    def __init__(self):
        self.agentes_activos = {}
        self.plugins_package = "src.logic.agents"
        self.plugins_path = os.path.join("src", "logic", "agents")
        self.state_file = "logs/agents_state.json" # Memoria de PIDs
        
        self.descubrir_agentes()
        self._cargar_estado_previo()

    def descubrir_agentes(self):
        try:
            package = importlib.import_module(self.plugins_package)
            for _, name, _ in pkgutil.iter_modules(package.__path__):
                self.agentes_activos[name] = {"status": "off", "pid": None}
        except Exception as e:
            logger.error(f"❌ Error al escanear: {e}")

    def _guardar_estado(self):
        """Guarda los PIDs actuales para no perder el rastro al cerrar la TUI."""
        with open(self.state_file, "w") as f:
            json.dump(self.agentes_activos, f)

    def _cargar_estado_previo(self):
        """Recupera los PIDs si la TUI se reinicia pero los procesos siguen vivos."""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r") as f:
                    saved = json.load(f)
                    for name, data in saved.items():
                        if name in self.agentes_activos:
                            # Verificar si el proceso sigue vivo realmente
                            if data["pid"]:
                                try:
                                    os.kill(data["pid"], 0) # Señal 0 no mata, solo verifica
                                    self.agentes_activos[name] = data
                                except OSError:
                                    pass # El proceso ya murió
            except Exception:
                pass

    def encender_agente(self, nombre: str):
        if nombre in self.agentes_activos:
            script_path = os.path.join(self.plugins_path, f"{nombre}.py")
            try:
                log_file = open(f"logs/daemon_{nombre}.log", "a")
                process = subprocess.Popen(
                    [sys.executable, script_path],
                    stdout=log_file, stderr=log_file,
                    start_new_session=True
                )
                self.agentes_activos[nombre] = {"pid": process.pid, "status": "on"}
                self._guardar_estado()
                logger.success(f"🚀 [AGENTE]: {nombre.upper()} en vuelo (PID: {process.pid}).")
                return True
            except Exception as e:
                logger.error(f"❌ Error al lanzar: {e}")
        return False

    def apagar_agente(self, nombre: str):
        if nombre in self.agentes_activos and self.agentes_activos[nombre]["pid"]:
            pid = self.agentes_activos[nombre]["pid"]
            try:
                os.kill(pid, 9)
                logger.warning(f"🛑 [MANAGER]: {nombre.upper()} aniquilado.")
            except: pass
            self.agentes_activos[nombre] = {"status": "off", "pid": None}
            self._guardar_estado()
            return True
        return False

    def matar_todo(self):
        """EL BOTÓN ROJO: Limpia todos los procesos del enjambre de golpe."""
        logger.critical("🔥 [MANAGER]: Iniciando protocolo de aniquilación total...")
        for nombre in list(self.agentes_activos.keys()):
            self.apagar_agente(nombre)
        
        if os.path.exists(self.state_file):
            os.remove(self.state_file)
        logger.success("💀 [MANAGER]: El enjambre ha sido purgado.")

    def listar_agentes(self):
        return {name: info["status"] for name, info in self.agentes_activos.items()}

manager = AgentManager()

