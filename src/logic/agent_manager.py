import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional
from loguru import logger

class AgentManager:
    def __init__(self) -> None:
        self.agentes_activos: Dict[str, Dict[str, Optional[int | str]]] = {}
        
        # --- ANCLAJE DE RUTAS ABSOLUTAS ---
        # Determinamos la raíz del proyecto buscando el archivo 'main.py' o basándonos en 'src'
        current_file = Path(__file__).resolve()
        self.project_root = current_file.parents[2] # De src/logic/manager.py -> src/ -> raíz/
        
        self.plugins_path = self.project_root / "src" / "logic" / "agents"
        self.state_file = self.project_root / "logs" / "agents_state.json"
        self.logs_dir = self.project_root / "logs"
        
        # Asegurar existencia de directorios
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.plugins_path.mkdir(parents=True, exist_ok=True)

        self.descubrir_agentes()
        self._cargar_estado_previo()

    def descubrir_agentes(self) -> None:
        """Escaneo físico de la carpeta agents/."""
        try:
            # Limpiamos para evitar duplicados en refrescos
            self.agentes_activos = {}
            for file in self.plugins_path.glob("*.py"):
                if file.name != "__init__.py":
                    # Cargamos el nombre del agente (ej: void_hunter)
                    self.agentes_activos[file.stem] = {"pid": None, "status": "off"}
            
            if not self.agentes_activos:
                logger.warning(f"🕵️ No se encontraron agentes en {self.plugins_path}")
        except Exception as e:
            logger.error(f"⚠️ Error en escaneo de agentes: {e}")

    def _guardar_estado(self) -> None:
        try:
            with self.state_file.open("w", encoding="utf-8") as f:
                json.dump(self.agentes_activos, f, indent=2)
        except Exception as e:
            logger.error(f"❌ No se pudo guardar el estado: {e}")

    def _cargar_estado_previo(self) -> None:
        if not self.state_file.exists(): return
        try:
            with self.state_file.open("r", encoding="utf-8") as f:
                datos = json.load(f)
            for nombre, info in datos.items():
                if nombre in self.agentes_activos and info.get("pid"):
                    pid = info["pid"]
                    try:
                        os.kill(pid, 0) # Verifica si el proceso sigue vivo
                        self.agentes_activos[nombre] = info
                    except OSError:
                        self.agentes_activos[nombre] = {"pid": None, "status": "off"}
        except Exception: pass

    def encender_agente(self, nombre: str) -> bool:
        if nombre not in self.agentes_activos: return False
        script_path = self.plugins_path / f"{nombre}.py"
        log_path = self.logs_dir / f"daemon_{nombre}.log"
        
        try:
            # Abrimos el log en modo append
            log_file = open(log_path, "a", encoding="utf-8")
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=log_file, 
                stderr=log_file,
                start_new_session=True,
                cwd=str(self.project_root) # Ejecutar desde la raíz para que los imports funcionen
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
            os.kill(info["pid"], 15) # SIGTERM
            self.agentes_activos[nombre] = {"pid": None, "status": "off"}
            self._guardar_estado()
            return True
        except Exception:
            # Si falla el kill suave, intentamos forzar
            try:
                os.kill(info["pid"], 9)
                self.agentes_activos[nombre] = {"pid": None, "status": "off"}
                self._guardar_estado()
                return True
            except: return False

    def listar_agentes(self) -> Dict[str, str]:
        return {name: info["status"] for name, info in self.agentes_activos.items()}

manager = AgentManager()

