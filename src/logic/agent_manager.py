import os
import sys
import json
import subprocess
import pkgutil
import importlib
from pathlib import Path
from typing import Dict, Optional

from loguru import logger


class AgentManager:
    """
    Maneja agentes como Daemons con persistencia de estado.

    Cada agente se representa con:
        - pid: int | None
        - status: "on" | "off"
        - log_file: file handle (solo en memoria)
    """

    def __init__(self) -> None:
        self.agentes_activos: Dict[str, Dict[str, Optional[int | str]]] = {}
        self.log_files: Dict[str, Path] = {}  # nombre → Path del archivo de log

        self.plugins_package = "src.logic.agents"
        self.plugins_path = Path("src", "logic", "agents")
        self.state_file = Path("logs", "agents_state.json")

        # Crear directorios necesarios
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        Path("logs").mkdir(parents=True, exist_ok=True)

        self.descubrir_agentes()
        self._cargar_estado_previo()

    # ------------------------------------------------------------------ #
    #  Descubrimiento y persistencia
    # ------------------------------------------------------------------ #
    def descubrir_agentes(self) -> None:
        """Carga la lista de módulos disponibles en src.logic.agents."""
        try:
            package = importlib.import_module(self.plugins_package)
            for _, name, _ in pkgutil.iter_modules(package.__path__):
                self.agentes_activos.setdefault(name, {"pid": None, "status": "off"})
        except Exception as e:
            logger.error(f"❌ Error al escanear agentes: {e}")

    def _guardar_estado(self) -> None:
        """Guarda el estado (PID y estado) de los agentes en disco."""
        try:
            with self.state_file.open("w", encoding="utf-8") as f:
                json.dump(self.agentes_activos, f, indent=2)
        except Exception as e:
            logger.error(f"❌ No se pudo guardar el estado: {e}")

    def _cargar_estado_previo(self) -> None:
        """Recupera los PIDs de agentes que siguen vivos tras reiniciar la TUI."""
        if not self.state_file.exists():
            return

        try:
            with self.state_file.open("r", encoding="utf-8") as f:
                datos = json.load(f)
            for nombre, info in datos.items():
                if nombre in self.agentes_activos and info.get("pid"):
                    pid = info["pid"]
                    try:
                        os.kill(pid, 0)  # Señal 0: solo verifica existencia
                        self.agentes_activos[nombre] = info
                    except OSError:
                        # El proceso ya no está vivo
                        self.agentes_activos[nombre] = {"pid": None, "status": "off"}
        except Exception as e:
            logger.error(f"❌ Error al cargar estado previo: {e}")

    # ------------------------------------------------------------------ #
    #  Operaciones con agentes
    # ------------------------------------------------------------------ #
    def encender_agente(self, nombre: str) -> bool:
        """Inicia un agente y asegura el flujo de logs."""
        if nombre not in self.agentes_activos:
            logger.error(f"❌ Agente '{nombre}' no registrado en el sistema.")
            return False

        script_path = self.plugins_path / f"{nombre}.py"
        log_path = Path("logs") / f"daemon_{nombre}.log"

        try:
            # Usamos un context manager manual para asegurar que el archivo se asocia al proceso
            log_file = open(log_path, "a", encoding="utf-8")
            
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=log_file,
                stderr=log_file,
                start_new_session=True
            )

            if process.pid:
                self.agentes_activos[nombre] = {"pid": process.pid, "status": "on"}
                self._guardar_estado()
                logger.success(f"🚀 [SHADOW_DAEMON]: {nombre.upper()} activado (PID: {process.pid}).")
                # Cerramos el handle en el padre, el hijo mantiene el descriptor
                log_file.close()
                return True
            
            log_file.close()
            return False

        except Exception as e:
            logger.error(f"❌ Error al instanciar {nombre}: {e}")
            return False

    def apagar_agente(self, nombre: str) -> bool:
        """Termina un proceso y limpia rastros (evita zombies)."""
        info = self.agentes_activos.get(nombre)
        if not info or not info["pid"]:
            return False

        pid = info["pid"]
        try:
            # Protocolo de terminación
            os.kill(pid, 15) # SIGTERM (Cierre elegante)
            
            # Esperar un momento a que cierre, si no, SIGKILL
            try:
                os.waitpid(pid, os.WNOHANG) 
            except ChildProcessError:
                pass # Ya se cerró

            logger.warning(f"🛑 [MANAGER]: Agente {nombre.upper()} neutralizado.")
        except ProcessLookupError:
            logger.info(f"ℹ️ El agente {nombre} ya no estaba en ejecución.")
        except Exception as e:
            logger.error(f"❌ Error al apagar {nombre}: {e}")

        self.agentes_activos[nombre] = {"pid": None, "status": "off"}
        self._guardar_estado()
        return True

    def matar_todo(self) -> None:
        """Protocolo de purga total del enjambre."""
        logger.critical("🔥 [MANAGER]: Iniciando aniquilación total de agentes...")
        for nombre in list(self.agentes_activos.keys()):
            self.apagar_agente(nombre)

        if self.state_file.exists():
            self.state_file.unlink()
        logger.success("💀 [MANAGER]: El enjambre ha sido purgado del sistema.")

    def listar_agentes(self) -> Dict[str, str]:
        """Retorna el estado actual de la legión."""
        return {name: str(info["status"]) for name, info in self.agentes_activos.items()}

# Instancia global única
manager = AgentManager()

