import os
from loguru import logger

class HardwareBridge:
    """Lee telemetría real del hardware del dispositivo (Android/Termux)."""

    @staticmethod
    def obtener_bateria() -> int:
        try:
            with open("/sys/class/power_supply/battery/capacity", "r") as f:
                return int(f.read().strip())
        except:
            return 100 # Default si no puede leer

    @staticmethod
    def obtener_ram_libre() -> int:
        """Retorna RAM libre en MB."""
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemAvailable" in line:
                        return int(line.split()[1]) // 1024
        except:
            return 1024
        return 0

bridge = HardwareBridge()

