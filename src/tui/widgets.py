from textual.widgets import Static
from src.logic.hardware_bridge import bridge

class TelemetryBar(Static):
    """Barra superior optimizada para bajo consumo de CPU."""

    def on_mount(self) -> None:
        # Aumentamos a 5s para evitar glitches por repintado constante
        self.set_interval(5.0, self.update_stats)

    def update_stats(self) -> None:
        ram = bridge.obtener_ram_libre()
        bat = bridge.obtener_bateria()

        color = "green" if ram > 500 else "yellow" if ram > 200 else "red"
        status_text = "OK" if ram > 200 else "LOW"

        # Actualización de texto simple
        self.update(
            f"RAM: [bold {color}]{ram}MB[/] | "
            f"BAT: [bold cyan]{bat}%[/] | "
            f"SYS: [bold {color}]{status_text}[/]"
        )

        # Solo cambiamos el fondo si es realmente crítico
        if ram < 150:
            self.styles.background = "#330000"
        else:
            self.styles.background = "transparent"

