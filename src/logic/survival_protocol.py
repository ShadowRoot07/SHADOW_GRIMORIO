import ctypes
import json
from pathlib import Path

class SurvivalProtocol:
    def __init__(self):
        self.raiz = Path(__file__).resolve().parents[2]
        self.lib = ctypes.CDLL(str(self.raiz / "src/utils/libhardware.so"))
        self.obj = self.lib.Bridge_new()
        self.report_path = self.raiz / "logs/survival_report.json"

    def monitorear(self):
        ram_free_pct = self.lib.Bridge_get_ram_pct(self.obj)
        cpu_load = self.lib.Bridge_get_cpu_load(self.obj)

        # Lógica de Ahorro
        mode = "NORMAL"
        if ram_free_pct < 20 or cpu_load > 80:
            mode = "LOW_RESOURCE" # Aquí la app desactivará animaciones o procesos pesados

        report = {
            "status": mode,
            "stats": {"ram_free": ram_free_pct, "cpu": cpu_load}
        }
        
        with open(self.report_path, "w") as f:
            json.dump(report, f)

survival = SurvivalProtocol()

