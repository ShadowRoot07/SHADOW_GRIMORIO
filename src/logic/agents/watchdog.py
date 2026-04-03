import time
import sys
import json
import py_compile
import tempfile
import os
from pathlib import Path

# --- ANCLAJE DINÁMICO ---
def buscar_raiz():
    actual = Path(__file__).resolve()
    for padre in actual.parents:
        if (padre / "src").exists():
            return padre
    # Fallback: si no encuentra 'src', sube 3 niveles
    return actual.parents[3]

base_path = buscar_raiz()
sys.path.append(str(base_path))
report_file = base_path / "logs" / "watchdog_report.json"

def notificar(mensaje, es_error=False, data=None):
    """Notifica al TTY y actualiza el reporte JSON."""
    color = "\x1b[1;31m" if es_error else "\x1b[1;34m"
    try:
        with open('/dev/tty', 'w') as tty:
            tty.write(f"\n{color}[WATCHDOG]:\x1b[0m {mensaje}\n")
    except:
        print(f"\n[WATCHDOG]: {mensaje}")

    if es_error and data:
        try:
            report = {
                "last_check": time.ctime(),
                "status": "syntax_error",
                "file": data.get("file"),
                "error": data.get("error"),
                "line": data.get("line")
            }
            with tempfile.NamedTemporaryFile('w', dir=report_file.parent, delete=False) as tf:
                json.dump(report, tf, indent=2)
                temp_name = tf.name
            Path(temp_name).replace(report_file)
        except: pass

def run():
    # Asegurar que existan los logs
    log_dir = base_path / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    notificar(f"INICIANDO VIGILANCIA EN: {base_path.name}")
    print(f"[DEBUG] Ruta base: {base_path}")

    # Estado inicial
    with open(report_file, "w") as f:
        json.dump({"status": "OK", "last_check": time.ctime()}, f)

    mtimes = {}

    try:
        while True:
            status_update = {"status": "OK", "last_check": time.ctime()}
            archivos_vistos = 0

            # os.walk es el método más fiable en el sistema de archivos de Android
            for raiz, carpetas, archivos in os.walk(str(base_path)):
                # FILTRO CORREGIDO: Eliminamos "data" porque tu ruta de Termux lo contiene
                if any(x in raiz for x in ["__pycache__", ".git", "venv", "logs"]):
                    continue
                
                # Opcional: print(f"📁 Escaneando: {raiz}") # Descomenta si quieres ver las carpetas

                for nombre_archivo in archivos:
                    if not nombre_archivo.endswith(".py"):
                        continue
                    
                    py_file = Path(raiz) / nombre_archivo
                    archivos_vistos += 1
                    
                    # Verificación de cambios y sintaxis
                    try:
                        current_mtime = py_file.stat().st_mtime
                        ruta_str = str(py_file)
                        
                        if mtimes.get(ruta_str) != current_mtime:
                            mtimes[ruta_str] = current_mtime
                            # py_compile.compile es la forma más rápida de chequear sintaxis
                            py_compile.compile(ruta_str, doraise=True)
                            print(f"  ✅ Check: {nombre_archivo}") 
                    
                    except py_compile.PyCompileError as e:
                        error_lines = str(e).split('\n')
                        msg = error_lines[-2] if len(error_lines) > 1 else "Error de sintaxis."
                        
                        data_err = {
                            "file": str(py_file.relative_to(base_path)),
                            "error": msg,
                            "line": error_lines[1].strip() if len(error_lines) > 1 else "?"
                        }
                        notificar(f"¡SINTAXIS ROTA! -> {nombre_archivo}", es_error=True, data=data_err)
                        status_update = {"status": "syntax_error", **data_err}
                    except Exception:
                        continue

            # Guardar reporte de ciclo
            with open(report_file, "w") as f:
                json.dump(status_update, f, indent=2)

            print(f"[OK] Ciclo completado. Archivos revisados: {archivos_vistos} ({time.strftime('%H:%M:%S')})")
            time.sleep(10)

    except KeyboardInterrupt:
        notificar("Watchdog desactivado por ShadowRoot07.")
        sys.exit(0)

if __name__ == "__main__":
    run()

