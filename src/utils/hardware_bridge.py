import ctypes
import pathlib
from loguru import logger

class HardwareBridge:
    """Carga el binario de C++ para obtener datos reales del ZTE."""
    
    def __init__(self):
        # Localizamos el archivo .so que acabas de compilar
        self.lib_path = pathlib.Path(__file__).parent / "libhardware.so"
        
        try:
            self.lib = ctypes.CDLL(str(self.lib_path))
            # Configuramos los tipos de respuesta de las funciones de C++
            self.lib.get_total_ram.restype = ctypes.c_long
            self.lib.get_cpu_cores.restype = ctypes.c_int
            logger.info("📡 Enlace con el núcleo C++ establecido correctamente.")
        except Exception as e:
            logger.error(f"Fallo al cargar el núcleo nativo (.so): {e}")
            self.lib = None

    def obtener_specs(self):
        """Retorna un diccionario con la potencia real del dispositivo."""
        if not self.lib:
            return {"ram_mb": 0, "cores": 0, "status": "offline"}
        
        return {
            "ram_mb": self.lib.get_total_ram(),
            "cores": self.lib.get_cpu_cores(),
            "status": "online"
        }

# Instancia lista para ser importada
hw = HardwareBridge()

