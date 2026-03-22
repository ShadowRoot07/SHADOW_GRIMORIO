from textual.widgets import Static
from src.logic.hardware_bridge import bridge          

class TelemetryBar(Static):
    """Barra superior con datos del ZTE en tiempo real."""
    
    def on_mount(self) -> None:
        # Actualización constante cada 2 segundos
        self.set_interval(2.0, self.update_stats)

    def update_stats(self) -> None:
        # Extraemos datos reales del hardware_bridge
        ram = bridge.obtener_ram_libre()
        bat = bridge.obtener_bateria()

        # Lógica de colores basada en el estado de la RAM
        color = "green" if ram > 500 else "yellow" if ram > 200 else "red"
        status_text = "OK" if ram > 200 else "CRITICAL"

        self.update(
            f"[bold {color}]🧠 RAM: {ram}MB[/] | "
            f"[bold cyan]🔋 BAT: {bat}%[/] | "
            f"[bold {color}]🛰️ STATUS: {status_text}[/]"
        )
        
        # Alerta visual en el fondo si la RAM es crítica
        if ram < 200:
            self.styles.background = "#440000"
        else:
            self.styles.background = "transparent"

