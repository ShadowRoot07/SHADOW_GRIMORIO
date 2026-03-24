import time
import sys
import py_compile
from pathlib import Path

# Anclaje de ruta
base_path = Path(__file__).resolve().parents[3]
sys.path.append(str(base_path))

def notificar(mensaje, es_error=False):
    color = "\x1b[1;31m" if es_error else "\x1b[1;34m"
    try:
        with open('/dev/tty', 'w') as tty:
            tty.write(f"\n{color}[WATCHDOG]:\x1b[0m {mensaje}\n")
    except: pass

def run():
    notificar("Ojo avizor activado. Vigilando sintaxis...")
    # Guardamos el estado de modificación de los archivos para no re-escanear
    mtimes = {}

    while True:
        try:
            # Escaneamos archivos .py en el proyecto y CWD
            for py_file in base_path.rglob("*.py"):
                if "__pycache__" in str(py_file): continue
                
                current_mtime = py_file.stat().st_mtime
                if mtimes.get(py_file) != current_mtime:
                    mtimes[py_file] = current_mtime
                    
                    # Intento de compilación silenciosa
                    try:
                        py_compile.compile(str(py_file), doraise=True)
                    except py_compile.PyCompileError as e:
                        error_msg = str(e).split('\n')[-2] # Última línea del error
                        notificar(f"Sintaxis rota en {py_file.name}: {error_msg}", es_error=True)

            time.sleep(5) # Escaneo cada 5 segundos para no drenar el ZTE
        except Exception as e:
            time.sleep(10)

if __name__ == "__main__":
    run()

