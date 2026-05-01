import os
import hashlib
import ctypes
from pathlib import Path
from loguru import logger

# Intentamos cargar el puente de C++ para mayor seguridad
try:
    lib_path = Path(__file__).resolve().parents[1] / "utils" / "libhardware.so"
    hardware_lib = ctypes.CDLL(str(lib_path))
    hardware_lib.get_total_ram.restype = ctypes.c_long
    hardware_lib.get_cpu_cores.restype = ctypes.c_int
except Exception:
    hardware_lib = None

_HUELLA_CACHE = None

def generar_huella_hardware():
    """Genera un hash único basado en el ADN del ZTE con cacheo de sesión."""
    global _HUELLA_CACHE
    if _HUELLA_CACHE:
        return _HUELLA_CACHE

    try:
        # Simplificamos para evitar variaciones por procesos externos
        # Usamos variables de entorno de Termux que son constantes
        termux_id = os.environ.get("TERMUX_VERSION", "0.118")
        android_id = os.environ.get("ANDROID_ROOT", "/system")
        
        # CPU Info: Solo features fijas
        cpu_fix = ""
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo", "r") as f:
                # Solo buscamos la arquitectura, que no cambia
                for line in f:
                    if "Architecture" in line or "Processor" in line:
                        cpu_fix += line.strip()
                        break

        seed = f"{cpu_fix}{termux_id}{android_id}".encode()
        _HUELLA_CACHE = hashlib.sha256(seed).hexdigest()
        return _HUELLA_CACHE
    except Exception as e:
        logger.error(f"Fallo en lectura de ADN hardware: {e}")
        return "STABLE_FALLBACK_ZTE_A54"

def obtener_bateria_real():
    try:
        with open("/sys/class/power_supply/battery/capacity", "r") as f:
            return int(f.read().strip())
    except: return 100

def obtener_ram_termux():
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()
            total = int(lines[0].split()[1])
            available = int(lines[2].split()[1])
            usada = ((total - available) / total) * 100
            return round(usada, 1)
    except: return 0.0

