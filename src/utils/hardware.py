import os

def obtener_bateria_real():
    """Lee la capacidad directamente del kernel de Android."""
    try:
        # Ruta estándar en la mayoría de dispositivos Android
        with open("/sys/class/power_supply/battery/capacity", "r") as f:
            return int(f.read().strip())
    except FileNotFoundError:
        return 100 # Valor por defecto si el kernel oculta la ruta

def obtener_ram_termux():
    """Lee la memoria disponible desde /proc/meminfo."""
    try:
        with open("/proc/meminfo", "r") as f:
            lines = f.readlines()
            total = int(lines[0].split()[1])
            free = int(lines[1].split()[1])
            usada = ((total - free) / total) * 100
            return round(usada, 1)
    except Exception:
        return 0.0

