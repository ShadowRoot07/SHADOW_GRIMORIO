import os
import sys
from pathlib import Path

# --- Ajuste de Path ---
raiz = Path(__file__).resolve().parents[2]
sys.path.append(str(raiz))

from src.database.manager import db
from src.database.models import Secreto
from src.logic.ghost_shell import init_ghost, ghost
from src.logic.config import config
from loguru import logger

def revelar_todo():
    """Extrae y descifra todos los secretos de la bóveda."""
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # Asegurarnos de estar en la raíz para cargar config correctamente
    os.chdir(raiz)
    init_ghost(config.encryption_key)
    
    print("\n" + "█" * 60)
    print("  🔓 SHADOW_GRIMORIO - REVELACIÓN (SCRIPTS/DB)")
    print("█" * 60)

    session = db.get_session()
    try:
        secretos = session.query(Secreto).all()
        if not secretos:
            print("\n[!] Bóveda vacía.")
        else:
            for s in secretos:
                valor_plano = ghost.reveal_data(s.valor_cifrado)
                print(f" > 🆔 {s.nombre:.<15}: {valor_plano}")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        session.close()
        print("\n" + "█" * 60 + "\n")

if __name__ == "__main__":
    revelar_todo()

