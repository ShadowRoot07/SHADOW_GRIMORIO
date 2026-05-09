import os
import sys
import json
import signal
import subprocess
import atexit
from pathlib import Path
from typing import Dict, Optional, Any
from loguru import logger

class AgentManager:
    def __init__(self) -> None:
        self.agentes_activos: Dict[str, Dict[str, Any]] = {}
        # Ruta absoluta garantizada
        self.project_root = Path(__file__).resolve().parents[2]
        self.plugins_path = self.project_root / "src" / "logic" / "agents"
        self.state_file = self.project_root / "logs" / "agents_state.json"
        self.logs_dir = self.project_root / "logs"

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.descubrir_agentes()
        self._cargar_estado_previo()

        # Solo matamos agentes cuando la APP principal se cierra de verdad
        atexit.register(self.matar_todo)

    def descubrir_agentes(self) -> None:
        # No reiniciamos el status si ya están encendidos
        for file in self.plugins_path.glob("*.py"):
            if file.name != "__init__.py" and file.stem not in self.agentes_activos:
                self.agentes_activos[file.stem] = {"pid": None, "status": "off"}

    def _guardar_estado(self) -> None:
        try:
            with self.state_file.open("w", encoding="utf-8") as f:
                json.dump(self.agentes_activos, f, indent=2)
        except: pass

    def _cargar_estado_previo(self) -> None:
        if not self.state_file.exists(): return
        try:
            with self.state_file.open("r", encoding="utf-8") as f:
                datos = json.load(f)
            for nombre, info in datos.items():
                if nombre in self.agentes_activos and info.get("pid"):
                    try:
                        os.kill(info["pid"], 0)
                        self.agentes_activos[nombre] = info
                    except (ProcessLookupError, OSError):
                        self.agentes_activos[nombre] = {"pid": None, "status": "off"}
            self._guardar_estado()
        except: pass

    def encender_agente(self, nombre: str) -> bool:
        if nombre not in self.agentes_activos: 
            self.descubrir_agentes() # Re-escanear por si es un plugin nuevo
            if nombre not in self.agentes_activos: return False

        script_path = self.plugins_path / f"{nombre}.py"
        log_path = self.logs_dir / f"daemon_{nombre}.log"

        try:
            # Abrir en modo append sin bloqueo
            with open(log_path, "a", encoding="utf-8") as log_file:
                process = subprocess.Popen(
                    [sys.executable, str(script_path)],
                    stdout=log_file,
                    stderr=log_file,
                    start_new_session=True,
                    cwd=str(self.project_root),
                    env={**os.environ, "PYTHONPATH": str(self.project_root)}
                )

            if process.pid:
                self.agentes_activos[nombre] = {"pid": process.pid, "status": "on"}
                self._guardar_estado()
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
        except:
            try: os.kill(info["pid"], signal.SIGKILL)
            except: pass
        
        self.agentes_activos[nombre] = {"pid": None, "status": "off"}
        self._guardar_estado()
        return True

    def matar_todo(self) -> None:
        """Limpieza real solo al apagar la App."""
        for nombre in list(self.agentes_activos.keys()):
            self.apagar_agente(nombre)

    def listar_agentes(self) -> Dict[str, str]:
        self._cargar_estado_previo() # Verificación en tiempo real
        return {name: info["status"] for name, info in self.agentes_activos.items()}

manager = AgentManager()

