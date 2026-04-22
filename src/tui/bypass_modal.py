from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input
from textual.containers import Vertical, Center
from src.logic.identity_matrix import sap

class BypassRootModal(ModalScreen[bool]):
    """Ventana secreta para forzar el acceso administrativo."""

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="bypass_container"):
                yield Label("💀 [ ACCESO ARQUITECTO ]", id="bypass_title")
                yield Label("Introduce la llave de bypass para saltar protocolos:")
                yield Input(placeholder="••••••••••••", password=True, id="bypass_input")
                with Center():
                    yield Button("FORZAR ENTRADA", variant="error", id="btn_bypass")

    def on_mount(self) -> None:
        self.query_one("#bypass_input").focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.ejecutar_bypass()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.ejecutar_bypass()

    def ejecutar_bypass(self):
        llave = self.query_one("#bypass_input").value
        if sap.activar_bypass_root(llave):
            self.app.notify("ACCESO ARQUITECTO CONFIRMADO", severity="success")
            # Devolvemos True para que el callback en app.py ejecute verificar_acceso_shadow()
            self.dismiss(True)
        else:
            self.app.notify("ERROR: Llave de bypass inválida.", severity="error")
            self.dismiss(False)

    CSS = """
    #bypass_container {
        width: 60%;
        height: auto;
        border: thick #FF3131;
        background: #0a0000;
        padding: 1 2;
    }
    #bypass_title {
        text-align: center;
        color: #FF3131;
        text-style: bold;
        margin-bottom: 1;
    }
    #bypass_input {
        margin: 1 0;
        border: solid #FF3131;
        color: #FF3131;
        background: #1a0000;
    }
    #btn_bypass {
        margin-top: 1;
        width: 100%;
    }
    """

