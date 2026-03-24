import subprocess
import time
import sys
from pathlib import Path

base_path = Path(__file__).resolve().parents[3]

def notificar(mensaje):
    try:
        with open('/dev/tty', 'w') as tty:
            tty.write(f"\n\x1b[1;35m[BRUMA_SYNC]:\x1b[0m {mensaje}\n")
    except: pass

def git_cmd(args):
    try:
        subprocess.run(["git"] + args, cwd=base_path, capture_output=True, check=True)
        return True
    except: return False

def run():
    notificar("Bruma se mueve entre las sombras. Auto-save activo.")
    
    while True:
        # Solo hacemos commit si hay cambios reales
        status = subprocess.run(["git", "status", "--porcelain"], cwd=base_path, capture_output=True, text=True).stdout
        
        if status.strip():
            timestamp = time.strftime("%H:%M:%S")
            git_cmd(["add", "."])
            if git_cmd(["commit", "-m", f"[SHADOW_AUTO]: {timestamp} - Preservación de estado"]):
                notificar(f"Estado preservado a las {timestamp}.")
        
        time.sleep(600) # Sincroniza cada 10 minutos

if __name__ == "__main__":
    run()

