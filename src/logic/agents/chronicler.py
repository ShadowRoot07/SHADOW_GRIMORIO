import sys
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Anclaje al núcleo (usando tu método de buscar_raiz)
def buscar_raiz():
    actual = Path(__file__).resolve()
    for padre in actual.parents:
        if (padre / "src").exists(): return padre
    return actual.parents[3]

raiz = buscar_raiz()
sys.path.append(str(raiz))

from src.database.manager import db
from src.database.models import Proyecto, HitoHistorial

class ChroniclerAgent:
    def __init__(self):
        self.root = raiz

    def ejecutar_git(self, comando: list):
        try:
            res = subprocess.run(
                ["git"] + comando,
                cwd=self.root,
                capture_output=True,
                text=True,
                env={"LANG": "en_US.UTF-8"}
            )
            return res.stdout.strip()
        except Exception as e:
            return f"Error Git: {e}"

    def registrar_hito(self, prompt, respuesta, contexto_ia):
        """Crea un commit y guarda el registro en la DB."""
        # 1. Asegurar que el proyecto existe en la DB
        session = db.get_session()
        nombre_repo = self.root.name
        proyecto = session.query(Proyecto).filter_by(nombre=nombre_repo).first()
        
        if not proyecto:
            proyecto = Proyecto(nombre=nombre_repo, path_local=str(self.root))
            session.add(proyecto)
            session.commit()

        # 2. Operación Git: Add y Commit
        self.ejecutar_git(["add", "."])
        # Usamos el primer enunciado del prompt para el mensaje del commit
        msg = f"Oráculo: {prompt[:50]}..."
        self.ejecutar_git(["commit", "-m", msg])
        
        commit_hash = self.ejecutar_git(["rev-parse", "HEAD"])
        rama = self.ejecutar_git(["rev-parse", "--abbrev-ref", "HEAD"])

        # 3. Guardar Hito en DB
        nuevo_hito = HitoHistorial(
            proyecto_id=proyecto.id,
            commit_hash=commit_hash,
            mensaje_commit=msg,
            prompt_usuario=prompt,
            respuesta_ia=respuesta,
            contexto_tecnico=json.dumps(contexto_ia)
        )
        proyecto.rama_actual = rama
        session.add(nuevo_hito)
        session.commit()
        session.close()
        return commit_hash

    def obtener_arbol_visual(self):
        """Genera el gráfico ASCII que verás en la TUI."""
        return self.ejecutar_git(["log", "--graph", "--oneline", "--all", "-n", "15"])

if __name__ == "__main__":
    # El agente puede usarse como daemon o mediante triggers
    print(f"[CHRONICLER] Nodo de Memoria Activo en {raiz.name}")

