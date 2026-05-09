from textual import events
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input
from textual.containers import Vertical, Horizontal
from src.logic.identity_matrix import sap
from loguru import logger

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
            self.ejecutar_validacion()
        elif event.button.id == "ritual_cancel":
            self.dismiss(False)

    def on_key(self, event: events.Key) -> None:
        if event.key == "enter":
            self.ejecutar_validacion()

    def ejecutar_validacion(self) -> None:
        """Extrae los datos, limpia caracteres invisibles y valida."""
        # Usamos .strip() y aseguramos limpieza de caracteres de control
        raw_k2 = str(self.query_one("#k2_input").value).strip()
        raw_k3 = str(self.query_one("#k3_input").value).strip()
        
        # Eliminamos posibles caracteres de escape o saltos de línea colados
        k2 = "".join(char for char in raw_k2 if char.isprintable())
        k3 = "".join(char for char in raw_k3 if char.isprintable())

        if sap.validar_acceso(k2, k3):
            self.app.notify("ACCESO CONCEDIDO", severity="success")
            self.dismiss(True)
        else:
            # LOG ADICIONAL PARA TI EN CONSOLA
            logger.warning(f"⚠️ [RITUAL]: Intento fallido. Longitud K2:{len(k2)} K3:{len(k3)}")
            self.app.notify("RITUAL FALLIDO", severity="error")
            self.query_one("#k2_input").value = ""
            self.query_one("#k3_input").value = ""
            self.query_one("#k2_input").focus()

    CSS = """
    #ritual_container { width: 60; height: auto; border: thick #BB00FF; background: #050505; padding: 1 2; align: center middle; }
    #ritual_title { text-align: center; color: #BB00FF; text-style: bold; margin-bottom: 1; }
    .ritual_label { color: #00FF00; margin-top: 1; }
    Input { background: #111; border: tall #333; color: #00FF00; margin-bottom: 1; }
    #ritual_actions { height: 3; margin-top: 1; align: center middle; }
    #ritual_confirm, #ritual_cancel { margin: 0 1; } 
    """

