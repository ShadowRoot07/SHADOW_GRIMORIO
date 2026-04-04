from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static
from textual.containers import Grid, Vertical, ScrollableContainer

class ConfirmBuildModal(ModalScreen[bool]):
    """Ventana de confirmación para el Arquitecto."""

    def __init__(self, resumen: str):
        super().__init__()
        self.resumen = resumen

    def compose(self) -> ComposeResult:
        with Vertical(id="modal_container"):
            yield Label("🏗️ ESTRUCTURA DETECTADA", id="modal_title")
            yield Static(self.resumen, id="modal_body")
            with Grid(id="modal_buttons"):
                yield Button("MATERIALIZAR", variant="success", id="confirm")
                yield Button("ABORTAR", variant="error", id="cancel")

    def on_mount(self) -> None:
        t = self.app.tema
        container = self.query_one("#modal_container")
        container.styles.border = ("thick", t['primary'])
        container.styles.background = t['surface']
        self.query_one("#modal_title").styles.color = t['accent']

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.dismiss(True)
        else:
            self.dismiss(False)

    CSS = """
    #modal_container {
        width: 80%;
        height: auto;
        max-height: 20;
        align: center middle;
        padding: 1;
    }
    #modal_title { text-align: center; text-style: bold; margin-bottom: 1; }
    #modal_body { margin: 1 0; height: 1fr; border: solid #333; padding: 1; }
    #modal_buttons { grid-size: 2; grid-gutter: 2; height: 3; }
    """

class WatchdogErrorModal(ModalScreen):
    """Ventana de alerta roja para errores de sintaxis detectados por Watchdog."""

    def __init__(self, error_data: dict):
        super().__init__()
        self.error_data = error_data

    def compose(self) -> ComposeResult:
        file = self.error_data.get("file", "Desconocido")
        line = self.error_data.get("line", "?")
        error_msg = self.error_data.get("error", "Error de sintaxis no especificado.")

        with Vertical(id="watchdog_modal"):
            yield Label("⚠️ SINTAXIS DETECTADA ROTA", id="wd_title")
            yield Label(f"ARCHIVO: [bold white]{file}[/] | LÍNEA: [bold cyan]{line}[/]", id="wd_subtitle")
            
            with ScrollableContainer(id="wd_scroll"):
                yield Static(error_msg, id="wd_body")
            
            with Grid(id="wd_footer"):
                yield Button("ENTENDIDO (CERRAR)", variant="error", id="close_wd")

    def on_mount(self) -> None:
        container = self.query_one("#watchdog_modal")
        container.styles.border = ("thick", "#FF0000")
        container.styles.background = "#1a0000"
        self.query_one("#wd_title").styles.color = "#FF3131"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close_wd":
            self.app.pop_screen()

    CSS = """
    #watchdog_modal {
        width: 85%;
        height: 60%;
        align: center middle;
        padding: 1;
        border: thick #FF0000;
    }
    #wd_title { text-align: center; text-style: bold; margin-bottom: 0; }
    #wd_subtitle { text-align: center; background: #330000; margin: 1 0; padding: 0 1; }
    #wd_scroll { 
        height: 1fr; 
        border: solid #550000; 
        padding: 1; 
        background: #000;
        scrollbar-gutter: stable;
    }
    #wd_body { color: #FF9999; }
    #wd_footer { grid-size: 1; height: 3; margin-top: 1; }
    #close_wd { width: 100%; border: none; }
    """

