import json
from pathlib import Path
from textual.widgets import Static

class TelemetryBar(Static):
    """Barra superior que monitorea RAM y Estado del Sistema."""

    def on_mount(self) -> None:
        self.raiz = Path(__file__).resolve().parents[2]
        self.report_path = self.raiz / "logs" / "survival_report.json"
        # Iniciamos con un estado base para evitar el atributo vacío antes del primer intervalo
        self.update_stats()
        self.set_interval(5.0, self.update_stats)

    def update_stats(self) -> None:
        """Lee el reporte de supervivencia y actualiza la UI."""
        ram = "???"
        status_color = "white"

        if self.report_path.exists():
            try:
                # Usamos una lectura rápida
                data = json.loads(self.report_path.read_text())
                ram = f"{data['stats']['ram']}MB"
                status = data.get("status", "HEALTHY")
                status_color = "green" if status == "HEALTHY" else "red"
            except Exception:
                pass

        # Actualizamos el contenido interno de Static
        self.update(f"[{status_color}]● GRIMORIO STATUS[/] | [cyan]RAM:[/] {ram} | [yellow]DEV MODE[/]")

    # ELIMINADO: render(self) -> str
    # Al eliminarlo, Textual usa automáticamente el contenido de self.update() 
    # evitando el AttributeError de '_content'.

