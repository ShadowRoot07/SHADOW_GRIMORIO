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
                # Limpiamos posibles líneas vacías al inicio y final
                art = f.read().strip("\n")
                return art
        except Exception as e:
            logger.error(f"Fallo al invocar {name}: {e}")
            return "[ DATA_CORRUPTION ]"

