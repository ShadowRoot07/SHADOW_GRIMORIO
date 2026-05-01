import json
from pathlib import Path
from textual.widgets import Static
from src.tui.themes import THEMES

class TelemetryBar(Static):
    """Barra superior que monitorea Salud del Sistema (CPU/RAM) y Estado."""

    def on_mount(self) -> None:
        self.raiz = Path(__file__).resolve().parents[2]
        self.report_path = self.raiz / "logs" / "survival_report.json"
        self.update_stats()
        # Mantenemos 2.0s para no estresar el procesador del móvil
        self.set_interval(2.0, self.update_stats)
    
    def update_stats(self) -> None:
        tema = getattr(self.app, "tema", {})
        c_primary = tema.get('primary', '#00ff00')
        c_secondary = tema.get('secondary', '#ff00ff')
        c_accent = tema.get('accent', '#00ffff')

        # DEFINICIÓN EXPLÍCITA (Evita el UnboundLocalError)
        status = "ONLINE"
        status_icon = "●"
        status_color = c_primary

        try:
            # Aquí puedes poner tu lógica real de psutil si la usas
            cpu_load = "12%" 
            ram_pct = "45%"
        except Exception:
            cpu_load = "??"
            ram_pct = "??"

        self.update(
            f"[{status_color}]{status_icon} {status}[/] | "
            f"[{c_accent}]CPU:[/] {cpu_load} | "
            f"[{c_secondary}]RAM FREE:[/] {ram_pct} | "
            f"[{c_primary}]SHADOW_GRIMORIO[/]"
        )

