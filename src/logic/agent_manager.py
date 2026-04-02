import os
import sys
import json
import signal
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any
from loguru import logger

try:
    from src.logic.architect_core import architect
except ImportError:
    architect = None

class AgentManager:
    def __init__(self) -> None:
        self.agentes_activos: Dict[str, Dict[str, Any]] = {}
        current_file = Path(__file__).resolve()
        self.project_root = current_file.parents[2]

        self.plugins_path = self.project_root / "src" / "logic" / "agents"
        self.state_file = self.project_root / "logs" / "agents_state.json"
        self.logs_dir = self.project_root / "logs"

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.descubrir_agentes()
        self._cargar_estado_previo()

    def descubrir_agentes(self) -> None:
        """Escanea el directorio de agentes para identificar scripts disponibles."""
        self.agentes_activos = {}
        for file in self.plugins_path.glob("*.py"):
            if file.name != "__init__.py":
                self.agentes_activos[file.stem] = {"pid": None, "status": "off"}

    def _guardar_estado(self) -> None:
        try:
            with self.state_file.open("w", encoding="utf-8") as f:
                json.dump(self.agentes_activos, f, indent=2)
        except: pass

    def _cargar_estado_previo(self) -> None:
        """Verifica si los agentes que estaban 'on' siguen vivos en el sistema."""
        if not self.state_file.exists(): return
        try:
            with self.state_file.open("r", encoding="utf-8") as f:
                datos = json.load(f)
            for nombre, info in datos.items():
                if nombre in self.agentes_activos and info.get("pid"):
                    try:
                        # Signal 0 no mata, solo verifica si el proceso existe
                        os.kill(info["pid"], 0)
                        self.agentes_activos[nombre] = info
                    except (ProcessLookupError, OSError):
                        self.agentes_activos[nombre] = {"pid": None, "status": "off"}
            self._guardar_estado()
        except: pass

    def encender_agente(self, nombre: str) -> bool:
        """Lanza un agente en segundo plano con redirección de logs."""
        if nombre not in self.agentes_activos: return False
        
        # Evitar duplicados
        if self.agentes_activos[nombre]["status"] == "on":
            self.apagar_agente(nombre)

        script_path = self.plugins_path / f"{nombre}.py"
        log_path = self.logs_dir / f"daemon_{nombre}.log"
        
        try:
            log_file = open(log_path, "a", encoding="utf-8")
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=log_file, stderr=log_file,
                start_new_session=True, # Lo independiza de la TUI
                cwd=str(self.project_root)
            )
            if process.pid:
                self.agentes_activos[nombre] = {"pid": process.pid, "status": "on"}
                self._guardar_estado()
                logger.info(f"🛰️ Agente {nombre} iniciado (PID: {process.pid})")
                return True
            return False
        except Exception as e:
            logger.error(f"Error al iniciar {nombre}: {e}")
            return False

    def apagar_agente(self, nombre: str) -> bool:
        info = self.agentes_activos.get(nombre)
        if not info or not info["pid"]: return False
        try:
            os.kill(info["pid"], signal.SIGTERM)
            self.agentes_activos[nombre] = {"pid": None, "status": "off"}
            self._guardar_estado()
            return True
        except:
            # Forzar cierre si no responde a SIGTERM
            try:
                os.kill(info["pid"], signal.SIGKILL)
                self.agentes_activos[nombre] = {"pid": None, "status": "off"}
                self._guardar_estado()
                return True
            except: return False

    def matar_todo(self) -> None:
        """Purga total de agentes. Útil para protocolos de supervivencia."""
        for nombre in list(self.agentes_activos.keys()):
            self.apagar_agente(nombre)
        logger.warning("💀 PURGA TOTAL: Todos los agentes han sido desactivados.")

    def listar_agentes(self) -> Dict[str, str]:
        return {name: info["status"] for name, info in self.agentes_activos.items()}

    def ejecutar_plano_arquitecto(self, respuesta_ia: str) -> Dict[str, Any]:
        if not architect: return {"status": "error", "message": "Arquitecto offline."}
        try:
            return architect.procesar_instruccion(respuesta_ia, cwd_usuario=os.getcwd())
        except Exception as e:
            return {"status": "error", "message": str(e)}

manager = AgentManager()

