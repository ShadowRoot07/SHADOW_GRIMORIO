import json
from pathlib import Path
from textual.widgets import Static

class TelemetryBar(Static):
    """Barra superior que monitorea Salud del Sistema (CPU/RAM) y Estado."""

    def on_mount(self) -> None:
        self.raiz = Path(__file__).resolve().parents[2]
        self.report_path = self.raiz / "logs" / "survival_report.json"
        self.update_stats()
        # Mantenemos 2.0s para no estresar el procesador del móvil
        self.set_interval(2.0, self.update_stats)

    def update_stats(self) -> None:
        """Lee el reporte de supervivencia basado en carga de recursos."""
        ram_pct, cpu_load = "??", "??"
        status_color = "white"
        status_icon = "●"

        if self.report_path.exists():
            try:
                # Lectura del reporte generado por el Protocolo Survival
                data = json.loads(self.report_path.read_text())
                stats = data.get('stats', {})
                
                # Nuevas métricas universales
                ram_pct = f"{stats.get('ram_free', 0)}%"
                cpu_load = f"{stats.get('cpu', 0)}%"
                
                status = data.get("status", "NORMAL")
                
                # Lógica visual neón
                if status == "NORMAL":
                    status_color = "green"
                    status_icon = "●"
                elif status == "LOW_RESOURCE":
                    status_color = "yellow"
                    status_icon = "⚠️"
                else:
                    status_color = "red"
                    status_icon = "💀"
            except Exception:
                pass

        # Renderizado de la barra con enfoque en optimización de recursos
        self.update(
            f"[{status_color}]{status_icon} {status}[/] | "
            f"[cyan]CPU:[/] {cpu_load} | "
            f"[magenta]RAM FREE:[/] {ram_pct} | "
            f"[yellow]SHADOW_GRIMORIO[/]"
        )

