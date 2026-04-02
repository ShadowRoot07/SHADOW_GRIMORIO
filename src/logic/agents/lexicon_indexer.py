import ast
import json
import time
import sys
import tempfile
from pathlib import Path

# --- ANCLAJE DE RUTA ---
current_path = Path(__file__).resolve()
base_path = current_path.parents[3]
sys.path.append(str(base_path))

index_file = base_path / "logs" / "lexicon_index.json"

def indexar_proyecto():
    index = {}
    index_file.parent.mkdir(parents=True, exist_ok=True)

    for py_file in base_path.rglob("*.py"):
        # Filtro de exclusión mejorado
        if any(x in str(py_file) for x in ["__pycache__", "tests", "venv", ".git", "data", "logs"]):
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())

            items = []
            for node in tree.body: # Solo nivel superior para no saturar el contexto
                if isinstance(node, ast.ClassDef):
                    items.append(f"Clase: {node.name}")
                elif isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("__"):
                        items.append(f"Func: {node.name}")

            if items:
                ruta_relativa = str(py_file.relative_to(base_path))
                index[ruta_relativa] = items
        except Exception:
            continue

    # ESCRITURA ATÓMICA: Evita archivos corruptos en cortes de energía/batería
    with tempfile.NamedTemporaryFile('w', dir=index_file.parent, delete=False) as tf:
        json.dump(index, tf, indent=2)
        temp_name = tf.name
    Path(temp_name).replace(index_file)

def run():
    try:
        with open('/dev/tty', 'w') as tty:
            tty.write("\n\x1b[1;36m[LEXICON]:\x1b[0m Cerebro activo. Indexando base de conocimientos...\n")
    except: pass

    while True:
        try:
            indexar_proyecto()
            time.sleep(300) 
        except Exception:
            time.sleep(60)

if __name__ == "__main__":
    run()

