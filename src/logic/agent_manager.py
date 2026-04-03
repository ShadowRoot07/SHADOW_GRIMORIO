import os
import sys
import json
import signal
import subprocess
import atexit
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
        
        # Registrar limpieza automática al salir del script principal
        atexit.register(self.matar_todo)

    def descubrir_agentes(self) -> None:
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
        if nombre not in self.agentes_activos: return False

        # Si ya existe un PID registrado, lo matamos antes de duplicar
        info_actual = self.agentes_activos[nombre]
        if info_actual["pid"]:
            self.apagar_agente(nombre)

        script_path = self.plugins_path / f"{nombre}.py"
        log_path = self.logs_dir / f"daemon_{nombre}.log"

        try:
            # Abrir log en modo append y asegurar que se cierre tras Popen
            log_file = open(log_path, "a", encoding="utf-8")
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=log_file, stderr=log_file,
                start_new_session=True, 
                cwd=str(self.project_root)
            )
            log_file.close() # Popen mantiene el file descriptor abierto internamente

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
        
        pid = info["pid"]
        try:
            # Intentar cierre elegante
            os.kill(pid, signal.SIGTERM)
            # Pequeña espera para que el proceso limpie
            self.agentes_activos[nombre] = {"pid": None, "status": "off"}
            self._guardar_estado()
            return True
        except ProcessLookupError:
            self.agentes_activos[nombre] = {"pid": None, "status": "off"}
            self._guardar_estado()
            return True
        except Exception as e:
            # Forzar cierre (SIGKILL) si lo anterior falla
            try:
                os.kill(pid, signal.SIGKILL)
                self.agentes_activos[nombre] = {"pid": None, "status": "off"}
                self._guardar_estado()
                return True
            except: return False

    def matar_todo(self) -> None:
        """Purga total de agentes. Se ejecuta al salir o por emergencia."""
        activos = [n for n, i in self.agentes_activos.items() if i["pid"]]
        if activos:
            logger.warning(f"💀 Ejecutando limpieza de agentes: {', '.join(activos)}")
            for nombre in activos:
                self.apagar_agente(nombre)

    def __del__(self):
        """Asegura que el manager intente matar hijos si el objeto es destruido."""
        self.matar_todo()

    def listar_agentes(self) -> Dict[str, str]:
        return {name: info["status"] for name, info in self.agentes_activos.items()}

    def ejecutar_plano_arquitecto(self, respuesta_ia: str) -> Dict[str, Any]:
        if not architect: return {"status": "error", "message": "Arquitecto offline."}
        try:
            return architect.procesar_instruccion(respuesta_ia, cwd_usuario=os.getcwd())
        except Exception as e:
            return {"status": "error", "message": str(e)}

manager = AgentManager()

