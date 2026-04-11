from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, Input, RadioSet, RadioButton
from textual.containers import Vertical, Horizontal
from src.logic.identity_matrix import sap
from src.logic.vault import vault
from src.logic.config import config
from loguru import logger

class InitWizard(Screen):
    """Wizard inicial para el sellado del Grimorio."""

    def compose(self) -> ComposeResult:
        with Vertical(id="wizard_container"):
            yield Label("⚡ INICIALIZACIÓN DEL GRIMORIO ⚡", id="wiz_title")
            
            # Sección de Identidad
            yield Label("LLAVE DE MENTE (K2):", classes="wiz_label")
            yield Input(placeholder="Tu frase secreta...", password=True, id="wiz_k2")
            
            yield Label("LLAVE DE ACCIÓN (K3):", classes="wiz_label")
            yield Input(placeholder="Tu palabra de poder...", password=True, id="wiz_k3")

            # Sección de API (Opcional en el inicio)
            yield Label("GROQ API KEY (Opcional):", classes="wiz_label")
            yield Input(placeholder="gsk_...", password=True, id="wiz_groq")

            # Selección de Matriz (Tema)
            yield Label("SELECCIONE MATRIZ VISUAL:", classes="wiz_label")
            with RadioSet(id="wiz_theme"):
                yield RadioButton("CYBERPUNK", value=True)
                yield RadioButton("MATRIX")
                yield RadioButton("VOID")

            with Horizontal(id="wiz_buttons"):
                yield Button("SELLAR DESTINO", variant="success", id="btn_finish")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_finish":
            k2 = self.query_one("#wiz_k2").value
            k3 = self.query_one("#wiz_k3").value
            groq = self.query_one("#wiz_groq").value
            
            if not k2 or not k3:
                self.app.notify("K2 y K3 son obligatorias para el sellado.", severity="error")
                return

            # 1. Generar la K1 (Hardware) automáticamente
            k1 = sap.hw_fingerprint
            
            # 2. Generar y guardar la Super Key (Hash SHA-512)
            super_key = sap.generar_super_key(k1, k2, k3)
            vault.store_secret("SUPER_KEY_HASH", super_key)
            vault.store_secret("K1_HARDWARE", k1)
            
            # 3. Guardar API Key si existe
            if groq:
                vault.store_secret("GROQ_API_KEY", groq)

            # 4. Guardar tema en config.yaml
            radio_set = self.query_one(RadioSet)
            tema = str(radio_set.pressed_button.label)
            config.shadow_theme = tema
            config.save_to_yaml()

            self.app.notify("GRIMORIO SELLADO CON ÉXITO", severity="information")
            self.app.pop_screen()

    CSS = """
    #wizard_container { padding: 2; background: #050505; border: double #00FF00; align: center middle; }
    #wiz_title { text-align: center; color: #00FF00; text-style: bold; margin-bottom: 1; }
    .wiz_label { color: #BB00FF; margin-top: 1; }
    Input { margin-bottom: 1; border: tall #333; }
    #wiz_buttons { margin-top: 2; align: center middle; }
    """

