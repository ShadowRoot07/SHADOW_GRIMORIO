import os
import shutil
from pathlib import Path

def ejecutar_purga():
    """Borra archivos sensibles y base de datos local inmediatamente."""
    rutas_criticas = [
        "data/shadow_local.db",
        ".env",
        "config.yaml",
        "logs/"
    ]
    for ruta in rutas_criticas:
        p = Path(ruta)
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
        elif p.exists():
            os.remove(p)
    print("\033[91m[!] PROTOCOLO CÓDIGO ROJO: Datos locales eliminados.\033[0m")

