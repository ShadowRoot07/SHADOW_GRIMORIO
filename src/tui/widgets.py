import json
from pathlib import Path
from textual.widgets import Static
from src.logic.hardware_bridge import bridge

class TelemetryBar(Static):
    """Barra superior optimizada para bajo consumo de CPU."""

    def on_mount(self) -> None:
        # Actualización cada 5 segundos para ahorrar batería en el ZTE
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

