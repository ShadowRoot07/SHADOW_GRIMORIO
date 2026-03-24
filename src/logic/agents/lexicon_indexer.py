import ast
import json
import time
import sys
import os
from pathlib import Path

# --- ANCLAJE DE RUTA ---
current_path = Path(__file__).resolve()
# Subimos 4 niveles: src/logic/agents/file.py -> agents -> logic -> src -> SHADOW_GRIMORIO
base_path = current_path.parents[3]
sys.path.append(str(base_path))

index_file = base_path / "logs" / "lexicon_index.json"

def indexar_proyecto():
    index = {}
    # Aseguramos que la carpeta logs existe
    index_file.parent.mkdir(parents=True, exist_ok=True)

    # Escaneamos archivos .py
    for py_file in base_path.rglob("*.py"):
        # Ignorar basura y el propio índice
        if any(x in str(py_file) for x in ["__pycache__", "tests", "venv", ".git"]):
            continue
        
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
                
            items = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    items.append(f"Clase: {node.name}")
                elif isinstance(node, ast.FunctionDef):
                    # Ignorar funciones privadas/ocultas si deseas
                    if not node.name.startswith("__"):
                        items.append(f"Func: {node.name}")
            
            if items:
                # Guardar ruta relativa para que el Oráculo la entienda fácil
                ruta_relativa = str(py_file.relative_to(base_path))
                index[ruta_relativa] = items
        except Exception:
            continue
        
    # Escritura atómica: escribimos y luego renombramos (opcional) o simple write
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)

def run():
    # Notificación al TTY para que sepas que Bruma está leyendo
    try:
        with open('/dev/tty', 'w') as tty:
            tty.write("\n\x1b[1;36m[LEXICON]:\x1b[0m Indexando base de conocimientos...\n")
    except: pass

    while True:
        try:
            indexar_proyecto()
            time.sleep(300) # Re-indexa cada 5 minutos
        except Exception:
            time.sleep(60)

if __name__ == "__main__":
    run()

