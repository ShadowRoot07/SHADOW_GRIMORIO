import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any
from loguru import logger

# --- IMPORTACIÓN DEL ARQUITECTO ---
try:
    # Ahora que 'architect' existe al final de architect_core.py, esto funcionará
    from src.logic.architect_core import architect
except ImportError as e:
    logger.error(f"❌ Error de vinculación: {e}")
    architect = None

class AgentManager:
    def __init__(self) -> None:
        self.agentes_activos: Dict[str, Dict[str, Optional[int | str]]] = {}
        current_file = Path(__file__).resolve()
        self.project_root = current_file.parents[2]

        self.plugins_path = self.project_root / "src" / "logic" / "agents"
        self.state_file = self.project_root / "logs" / "agents_state.json"
        self.logs_dir = self.project_root / "logs"

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.plugins_path.mkdir(parents=True, exist_ok=True)

        self.descubrir_agentes()
        self._cargar_estado_previo()

    def ejecutar_plano_arquitecto(self, respuesta_ia: str) -> Dict[str, Any]:
        if not architect:
            return {"status": "error", "message": "Arquitecto no inicializado."}

        # Captura el contexto de ubicación del usuario
        cwd_usuario = os.getcwd()
        logger.info(f"🏗️  Invocando Arquitecto en: {cwd_usuario}")

        try:
            return architect.procesar_instruccion(respuesta_ia, cwd_usuario=cwd_usuario)
        except Exception as e:
            logger.error(f"❌ Error en puente: {e}")
            return {"status": "error", "message": str(e)}

    # --- RESTO DE TU LÓGICA (MANTENIDA) ---
    def descubrir_agentes(self) -> None:
        try:
            self.agentes_activos = {}
            for file in self.plugins_path.glob("*.py"):
                if file.name != "__init__.py":
                    self.agentes_activos[file.stem] = {"pid": None, "status": "off"}
        except Exception as e:
            logger.error(f"⚠️ Error escaneo: {e}")

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
                    except:
                        self.agentes_activos[nombre] = {"pid": None, "status": "off"}
        except: pass

    def encender_agente(self, nombre: str) -> bool:
        if nombre not in self.agentes_activos: return False
        script_path = self.plugins_path / f"{nombre}.py"
        log_path = self.logs_dir / f"daemon_{nombre}.log"
        try:
            with open(log_path, "a", encoding="utf-8") as log_file:
                process = subprocess.Popen(
                    [sys.executable, str(script_path)],
                    stdout=log_file, stderr=log_file,
                    start_new_session=True,
                    cwd=str(self.project_root)
                )
                if process.pid:
                    self.agentes_activos[nombre] = {"pid": process.pid, "status": "on"}
                    self._guardar_estado()
                    return True
            return False
        except Exception as e:
            logger.error(f"❌ Error al encender {nombre}: {e}")
            return False

    def apagar_agente(self, nombre: str) -> bool:
        info = self.agentes_activos.get(nombre)
        if not info or not info["pid"]: return False
        try:
            os.kill(info["pid"], 15)
            self.agentes_activos[nombre] = {"pid": None, "status": "off"}
            self._guardar_estado()
            return True
        except: return False

    def listar_agentes(self) -> Dict[str, str]:
        return {name: info["status"] for name, info in self.agentes_activos.items()}

manager = AgentManager()

