import sys
from pathlib import Path

# Permitir que el agente vea el core del proyecto
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

def run():
    print("\033[91m[VOID_HUNTER]\033[0m: Escaneando el vacío en busca de fallos...")
    # Aquí irá la lógica de auditoría automática más adelante

if __name__ == "__main__":
    run()

