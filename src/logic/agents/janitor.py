import os
import shutil
import sys
from pathlib import Path

# Añadimos el root al path para que el agente encuentre sus módulos si es necesario
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

def notificar(mensaje):
    """Escribe directamente en la terminal activa del usuario."""
    try:
        with open('/dev/tty', 'w') as tty:
            tty.write(f"\n\x1b[1;32m[SHADOW_GRIMORIO]:\x1b[0m {mensaje}\n")
    except:
        # Si no hay TTY (terminal cerrada totalmente), el mensaje se queda en el log del manager
        pass

class JanitorAgent:
    def __init__(self):
        self.root = Path(__file__).parent.parent.parent.parent
        self.targets = ["**/__pycache__", "**/*.pyc", "logs/*.log"]

    def run(self):
        borrados = 0
        for pattern in self.targets:
            for path in self.root.glob(pattern):
                try:
                    if path.is_dir(): shutil.rmtree(path)
                    else: path.unlink()
                    borrados += 1
                except: pass
        
        notificar(f"Purga completada por el Agente Janitor. {borrados} elementos eliminados.")

if __name__ == "__main__":
    # El manager ejecutará este archivo directamente
    agent = JanitorAgent()
    agent.run()

