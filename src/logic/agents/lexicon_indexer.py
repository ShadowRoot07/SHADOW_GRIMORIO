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
    
    print(f"[DEBUG LEXICON]: Escaneando desde {base_path}")
    
    # Buscamos todos los archivos .py
    archivos_totales = list(base_path.rglob("*.py"))
    print(f"[DEBUG LEXICON]: {len(archivos_totales)} archivos encontrados.")

    for py_file in archivos_totales:
        try:
            # Obtenemos la ruta relativa respecto a SHADOW_GRIMORIO
            ruta_relativa = str(py_file.relative_to(base_path))
            
            # FILTRO ULTRA-ESPECÍFICO: Solo ignoramos carpetas críticas de sistema/git
            # NO USAR "data" ni "logs" de forma genérica aquí
            if any(x in ruta_relativa for x in [".git/", "__pycache__", "venv/"]):
                continue

            items = []
            with open(py_file, "r", encoding="utf-8") as f:
                contenido = f.read()
                if contenido.strip():
                    tree = ast.parse(contenido)
                    for node in tree.body:
                        if isinstance(node, ast.ClassDef):
                            items.append(f"Clase: {node.name}")
                        elif isinstance(node, ast.FunctionDef):
                            if not node.name.startswith("__"):
                                items.append(f"Func: {node.name}")
            
            # Guardamos siempre, aunque esté vacío
            index[ruta_relativa] = items
            
        except Exception:
            continue

    # Si por alguna razón el índice sigue en 0, no sobreescribimos con basura
    if len(index) == 0:
        print("[ALERTA]: El índice resultó vacío. Revisa las rutas.")
        return

    # ESCRITURA ATÓMICA
    with tempfile.NamedTemporaryFile('w', dir=index_file.parent, delete=False) as tf:
        json.dump(index, tf, indent=2)
        temp_name = tf.name
    Path(temp_name).replace(index_file)
    print(f"[LEXICON]: Índice actualizado con {len(index)} archivos.")

def run():
    print("\n\x1b[1;36m[LEXICON]:\x1b[0m Iniciando escaneo profundo...")
    while True:
        try:
            indexar_proyecto()
            time.sleep(300)
        except Exception as e:
            print(f"Error en Lexicon: {e}")
            time.sleep(60)

if __name__ == "__main__":
    run()

