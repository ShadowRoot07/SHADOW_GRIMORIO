from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input
from textual.containers import Vertical, Horizontal
from src.logic.identity_matrix import sap

class ShadowRitualModal(ModalScreen[bool]):
    def compose(self) -> ComposeResult:
        with Vertical(id="ritual_container"):
            yield Label("⚡ RITUAL DE SINCRONIZACIÓN ⚡", id="ritual_title")
            yield Label("INGRESE LLAVE DE MENTE (K2):", classes="ritual_label")
            yield Input(placeholder="••••••••", password=True, id="k2_input")
            yield Label("INGRESE LLAVE DE ACCIÓN (K3):", classes="ritual_label")
            yield Input(placeholder="••••••••", password=True, id="k3_input")
            with Horizontal(id="ritual_actions"):
                # IDs unificados para evitar entropía
                yield Button("DESPERTAR", variant="success", id="ritual_confirm")
                yield Button("ABORTAR", variant="error", id="ritual_cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ritual_confirm":
            k2 = str(self.query_one("#k2_input").value)
            k3 = str(self.query_one("#k3_input").value)
            if sap.validar_acceso(k2, k3):
                self.app.notify("ACCESO CONCEDIDO", severity="success")
                self.dismiss(True)
            else:
                self.app.notify("RITUAL FALLIDO", severity="error")
        elif event.button.id == "ritual_cancel":
            self.dismiss(False)

    CSS = """
    #ritual_container { width: 60; height: auto; border: thick #BB00FF; background: #050505; padding: 1 2; align: center middle; }
    #ritual_title { text-align: center; color: #BB00FF; text-style: bold; margin-bottom: 1; }
    .ritual_label { color: #00FF00; margin-top: 1; }
    Input { background: #111; border: tall #333; color: #00FF00; margin-bottom: 1; }
    #ritual_actions { height: 3; margin-top: 1; align: center middle; }
    #ritual_confirm, #ritual_cancel { margin: 0 1; } 
    """

