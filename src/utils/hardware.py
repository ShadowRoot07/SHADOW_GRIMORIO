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

def generar_huella_hardware():
    """Genera un hash único e inmutable basado en el ADN del ZTE."""
    try:
        # 1. Info de CPU (Serial real del silicio)
        cpu_info = ""
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo", "r") as f:
                cpu_info = "".join([l for l in f.readlines() if "Serial" in l or "Features" in l])

        # 2. Modelo de Android
        device_model = os.popen("getprop ro.product.model").read().strip()
        
        # 3. Datos físicos (Bridge C++ o Fallback)
        if hardware_lib:
            ram = hardware_lib.get_total_ram()
            cores = hardware_lib.get_cpu_cores()
            fisico = f"RAM:{ram}-CORES:{cores}"
        else:
            fisico = "LEGACY_PHYSICAL"

        # Sellado SHA-256
        seed = f"{cpu_info}{device_model}{fisico}".encode()
        return hashlib.sha256(seed).hexdigest()
    except Exception as e:
        logger.error(f"Fallo en lectura de ADN hardware: {e}")
        return "ERROR_IDENTIDAD_HARDWARE"

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

