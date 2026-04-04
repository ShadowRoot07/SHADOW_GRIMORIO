import json
import os
from pathlib import Path
from textual.widgets import Static
from textual.message import Message
from src.logic.hardware_bridge import bridge

class TelemetryBar(Static):
    """Barra superior optimizada para bajo consumo de CPU."""

    def on_mount(self) -> None:
        self.set_interval(5.0, self.update_stats)

    def update_stats(self) -> None:
        ram = bridge.obtener_ram_libre()
        bat = bridge.obtener_bateria()

        color = "green" if ram > 500 else "yellow" if ram > 200 else "red"
        status_text = "OK" if ram > 200 else "LOW"

        self.update(
            f"RAM: [bold {color}]{ram}MB[/] | "
            f"BAT: [bold cyan]{bat}%[/] | "
            f"SYS: [bold {color}]{status_text}[/]"
        )

        if ram < 150:
            self.styles.background = "#330000"
        else:
            self.styles.background = "transparent"

class WatchdogObserver(Static):
    """Widget invisible que monitorea el reporte del Watchdog."""

    class SyntaxErrorDetected(Message):
        """Evento que se dispara cuando hay un error en el JSON."""
        def __init__(self, data: dict) -> None:
            self.data = data
            super().__init__()

    def on_mount(self) -> None:
        # Calculamos la ruta absoluta real del proyecto para no fallar en Termux
        self.raiz_proyecto = Path(__file__).resolve().parents[2]
        self.report_path = self.raiz_proyecto / "logs" / "watchdog_report.json"
        
        self.last_check_time = ""
        # Verificamos cada 2 segundos para mayor respuesta
        self.set_interval(2.0, self.check_report)

    def check_report(self) -> None:
        if not self.report_path.exists():
            return

        try:
            # Forzamos la lectura fresca del archivo
            with open(self.report_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            current_status = data.get("status")
            current_time = data.get("last_check", "")

            if current_status == "syntax_error":
                if current_time != self.last_check_time:
                    self.last_check_time = current_time
                    self.post_message(self.SyntaxErrorDetected(data))

            elif current_status == "OK":
                # Limpieza de bandera para permitir nuevos errores
                self.last_check_time = ""

        except Exception:
            pass

    def render(self) -> str:
        return "" # Widget invisible

