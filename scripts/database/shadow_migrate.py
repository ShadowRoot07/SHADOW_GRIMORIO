import os
import sys
from pathlib import Path

# --- Ajuste de Path para encontrar 'src' ---
raiz = Path(__file__).resolve().parents[2]
sys.path.append(str(raiz))

from src.database.manager import db
from src.logic.config import config
from src.logic.ghost_shell import init_ghost
from loguru import logger

def migrar_todo_el_env():
    print("--- 🔐 MIGRACIÓN UNIVERSAL (SCRIPTS/DB) ---")
    
    # Asegurarnos de estar en la raíz para leer el .env
    os.chdir(raiz)
    
    init_ghost(config.encryption_key)

    env_path = ".env"
    if not os.path.exists(env_path):
        logger.error(f"No se encontró el archivo .env en {raiz}")
        return

    with open(env_path, "r") as f:
        lineas = f.readlines()

    for linea in lineas:
        linea = linea.strip()
        if not linea or linea.startswith("#") or "ENCRYPTION_KEY" in linea:
            continue
        
        if "=" in linea:
            key, value = linea.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'").strip('"')

            if value:
                db.save_secret(key, value)
                logger.success(f"Variable '{key}' cifrada en la bóveda.")

    print("\n✅ MIGRACIÓN COMPLETADA DESDE DIRECTORIO DE SCRIPTS.")

if __name__ == "__main__":
    migrar_todo_el_env()

