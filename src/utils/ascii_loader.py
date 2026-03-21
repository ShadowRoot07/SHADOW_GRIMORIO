import pathlib
from loguru import logger

class ASCIILoader:
    """Módulo para invocar el arte visual del Grimorio."""
    
    BASE_PATH = pathlib.Path("assets/ascii")

    @classmethod
    def get_art(cls, name: str) -> str:
        """Busca un archivo .txt por nombre y retorna su contenido."""
        file_path = cls.BASE_PATH / f"{name}.txt"
        
        try:
            if not file_path.exists():
                logger.warning(f"Glifo visual no encontrado: {name}")
                return f"[ ERROR: {name} NOT FOUND ]"
            
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Fallo al invocar {name}: {e}")
            return "[ DATA_CORRUPTION ]"

# Prueba rápida interna
if __name__ == "__main__":
    print(ASCIILoader.get_art("splash"))

