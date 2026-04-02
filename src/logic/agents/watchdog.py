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
        # Notificación directa al TTY para no depender de la UI congelada
        with open('/dev/tty', 'w') as tty:
            tty.write(f"\n{color}[WATCHDOG]:\x1b[0m {mensaje}\n")
    except: pass

def run():
    notificar("Ojo avizor activado. Vigilando sintaxis...")
    mtimes = {}

    # Carpetas críticas para vigilar (evita escanear logs, data, etc.)
    watch_dirs = [base_path / "src", base_path]

    while True:
        try:
            for directory in watch_dirs:
                # Solo buscamos archivos .py en primer y segundo nivel de esas carpetas
                for py_file in directory.rglob("*.py"):
                    if any(x in str(py_file) for x in ["__pycache__", "data", "logs", ".git"]):
                        continue

                    try:
                        current_mtime = py_file.stat().st_mtime
                        if mtimes.get(py_file) != current_mtime:
                            mtimes[py_file] = current_mtime

                            # Verificación de sintaxis
                            py_compile.compile(str(py_file), doraise=True)
                    except py_compile.PyCompileError as e:
                        # Extraer solo la línea del error para brevedad
                        error_lines = str(e).split('\n')
                        msg = error_lines[-2] if len(error_lines) > 1 else "Error de sintaxis."
                        notificar(f"Sintaxis rota en {py_file.name}: {msg}", es_error=True)
                    except: pass

            time.sleep(7) # Un poco más de tiempo para ahorrar batería en el ZTE
        except Exception:
            time.sleep(15)

if __name__ == "__main__":
    run()

