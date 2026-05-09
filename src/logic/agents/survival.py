import time
import sys
import json
import os
from pathlib import Path

# --- UNIFICACIÓN DE RUTA ---
def buscar_raiz():
    return Path("/data/data/com.termux/files/home/BIG-Projects/SHADOW_GRIMORIO")

raiz = buscar_raiz()
report_file = raiz / "logs" / "survival_report.json"

class SurvivalAgent:
    def __init__(self):
        print("\033[1;32m[SURVIVAL]\033[0m: Monitor de hardware nativo (Linux-Kernel Mode) activo.")

    def leer_archivo_seguro(self, ruta):
        """Intenta leer un archivo de sistema sin crashear."""
        if os.path.exists(ruta):
            try:
                with open(ruta, "r") as f:
                    return f.read().strip()
            except:
                return None
        return None

    def obtener_stats_termux(self):
        """Busca datos directamente en /proc y /sys."""
        stats = {"ram": 0, "bat": 0, "temp": 0}

        # 1. RAM (Lectura directa de Memoria Disponible)
        try:
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    if "MemAvailable" in line:
                        stats["ram"] = int(line.split()[1]) // 1024
                        break
        except: pass

        # 2. BATERÍA (Bypass de Termux:API -> Acceso directo a Power Supply)
        rutas_bat = [
            "/sys/class/power_supply/battery/capacity",
            "/sys/class/power_supply/bms/capacity",
            "/sys/class/power_supply/main/capacity"
        ]
        for r in rutas_bat:
            val = self.leer_archivo_seguro(r)
            if val is not None:
                stats["bat"] = int(val)
                break

        # 3. TEMPERATURA (Bypass de Thermal Zones)
        rutas_temp = [
            "/sys/class/thermal/thermal_zone0/temp",
            "/sys/class/power_supply/battery/temp",
            "/sys/class/thermal/thermal_zone1/temp"
        ]
        for r in rutas_temp:
            val = self.leer_archivo_seguro(r)
            if val is not None:
                t = int(val)
                # Conversión estándar de miligrados a grados
                stats["temp"] = t // 1000 if t > 1000 else t // 10
                break
        
        return stats

    def gestionar_emergencia(self, ram_libre):
        """Crea un flag para detener procesos pesados si la RAM peligra."""
        pause_flag = raiz / "logs" / "EXTREME_LOW_RAM.flag"
        if ram_libre < 300:
            if not pause_flag.exists():
                with open(pause_flag, "w") as f:
                    f.write("STOP")
                print("\033[1;31m[SURVIVAL]: RAM CRÍTICA (<300MB). Flag de pausa creado.\033[0m")
        else:
            if pause_flag.exists():
                pause_flag.unlink()

    def ejecutar_protocolos(self, stats):
        status = "HEALTHY"
        alerts = []

        # Solo alertamos si el valor es real (mayor a 0)
        if 0 < stats["bat"] < 15:
            status = "CRITICAL"
            alerts.append(f"ENERGÍA BAJA: {stats['bat']}%")

        if stats["ram"] < 400:
            status = "WARNING"
            alerts.append(f"RAM LIMITADA: {stats['ram']}MB")
            self.gestionar_emergencia(stats["ram"])

        report = {
            "status": status,
            "stats": stats,
            "alerts": alerts,
            "timestamp": time.time()
        }

        # Escritura segura del reporte
        try:
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, "w") as f:
                json.dump(report, f, indent=2)
        except Exception as e:
            print(f"Error escribiendo reporte: {e}")

    def run(self):
        while True:
            try:
                stats = self.obtener_stats_termux()
                self.ejecutar_protocolos(stats)
            except Exception as e:
                print(f"Error en el ciclo de supervivencia: {e}")
            
            time.sleep(15)

if __name__ == "__main__":
    SurvivalAgent().run()

