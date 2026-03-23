import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any
from loguru import logger

# --- NUEVA IMPORTACIÓN PARA EL ARQUITECTO ---
try:
    from src.logic.architect_core.architect import architect
except ImportError:
    # Fallback por si la ruta de carpetas varía ligeramente
    try:
        from src.logic.architect_core import architect
    except ImportError as e:
        logger.error(f"❌ No se pudo encontrar architect_core: {e}")
        architect = None

class AgentManager:
    def __init__(self) -> None:
        self.agentes_activos: Dict[str, Dict[str, Optional[int | str]]] = {}

        # --- ANCLAJE DE RUTAS ABSOLUTAS ---
        current_file = Path(__file__).resolve()
        self.project_root = current_file.parents[2] 

        self.plugins_path = self.project_root / "src" / "logic" / "agents"
        self.state_file = self.project_root / "logs" / "agents_state.json"
        self.logs_dir = self.project_root / "logs"

        # Asegurar existencia de directorios
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.plugins_path.mkdir(parents=True, exist_ok=True)

        self.descubrir_agentes()
        self._cargar_estado_previo()

    # --- NUEVA FUNCIÓN: EL PUENTE CON EL ARQUITECTO ---
    def ejecutar_plano_arquitecto(self, respuesta_ia: str) -> Dict[str, Any]:
        """
        Toma el JSON (o texto con JSON) de la IA y lo materializa.
        No rompe la gestión de agentes, solo añade capacidad de construcción.
        """
        if not architect:
            return {"status": "error", "message": "Arquitecto no inicializado."}
            
        logger.info("🏗️  Iniciando materialización de archivos desde el Manager...")
        try:
            # architect.procesar_instruccion es quien realmente escribe en disco
            resultado = architect.procesar_instruccion(respuesta_ia)
            return resultado
        except Exception as e:
            logger.error(f"❌ Error en el puente del Arquitecto: {e}")
            return {"status": "error", "message": str(e)}

    # --- MÉTODOS DE GESTIÓN DE DAEMONS (MANTENIDOS SIN CAMBIOS) ---
    def descubrir_agentes(self) -> None:
        """Escaneo físico de la carpeta agents/."""
        try:
            self.agentes_activos = {}
            for file in self.plugins_path.glob("*.py"):
                if file.name != "__init__.py":
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
                        os.kill(pid, 0) 
                        self.agentes_activos[nombre] = info
                    except OSError:
                        self.agentes_activos[nombre] = {"pid": None, "status": "off"}
        except Exception: pass

    def encender_agente(self, nombre: str) -> bool:
        if nombre not in self.agentes_activos: return False
        script_path = self.plugins_path / f"{nombre}.py"
        log_path = self.logs_dir / f"daemon_{nombre}.log"

        try:
            log_file = open(log_path, "a", encoding="utf-8")
            process = subprocess.Popen(
                [sys.executable, str(script_path)],
                stdout=log_file,
                stderr=log_file,
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
        except Exception:
            try:
                os.kill(info["pid"], 9)
                self.agentes_activos[nombre] = {"pid": None, "status": "off"}
                self._guardar_estado()
                return True
            except: return False

    def listar_agentes(self) -> Dict[str, str]:
        return {name: info["status"] for name, info in self.agentes_activos.items()}

manager = AgentManager()

