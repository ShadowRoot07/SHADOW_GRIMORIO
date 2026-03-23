from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static
from textual.containers import Grid, Vertical

class ConfirmBuildModal(ModalScreen[bool]):
    """Ventana de confirmación para el Arquitecto."""
    
    def __init__(self, resumen: str):
        super().__init__()
        self.resumen = resumen

    def compose(self) -> ComposeResult:
        t = self.app.tema
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
        border: thick $primary;
    }
    #modal_title { text-align: center; text-style: bold; margin-bottom: 1; }
    #modal_body { margin: 1 0; height: 1fr; border: solid #333; padding: 1; }
    #modal_buttons { grid-size: 2; grid-gutter: 2; height: 3; }
    """

