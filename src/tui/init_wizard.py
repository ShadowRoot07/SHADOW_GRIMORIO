from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, Input, RadioSet, RadioButton
from textual.containers import Vertical, Horizontal
from src.logic.config import config
from src.database.manager import db
from loguru import logger

class InitWizard(Screen):
    """Wizard inicial para el sellado del Grimorio y creación de identidad."""


    def compose(self) -> ComposeResult:
        with Vertical(id="wizard_container"):
            yield Label("⚡ INICIALIZACIÓN DEL GRIMORIO ⚡", id="wiz_title")
            yield Label("LLAVE DE MENTE (K2):", classes="wiz_label")
            yield Input(placeholder="Tu frase secreta...", password=True, id="wiz_k2")
            yield Label("LLAVE DE ACCIÓN (K3):", classes="wiz_label")
            yield Input(placeholder="Tu palabra de poder...", password=True, id="wiz_k3")
            yield Label("GROQ API KEY (Opcional):", classes="wiz_label")
            yield Input(placeholder="gsk_...", password=True, id="wiz_groq")
            yield Label("SELECCIONE MATRIZ VISUAL:", classes="wiz_label")
            with RadioSet(id="wiz_theme"):
                yield RadioButton("CYBERPUNK", value=True, id="theme_cyber")
                yield RadioButton("MATRIX", id="theme_matrix")
                yield RadioButton("VOID", id="theme_void")
            with Horizontal(id="wiz_buttons"):
                yield Button("SELLAR DESTINO", variant="success", id="btn_finish")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_finish":
            # LIMPIEZA INMEDIATA
            k2 = str(self.query_one("#wiz_k2").value).strip()
            k3 = str(self.query_one("#wiz_k3").value).strip()
            
            # Aseguramos que solo caracteres imprimibles pasen
            k2 = "".join(c for c in k2 if c.isprintable())
            k3 = "".join(c for c in k3 if c.isprintable())
            
            if not k2 or not k3:
                self.app.notify("K2 y K3 son requeridas.", severity="error")
                return

# src/tui/init_wizard.py - REFACTORIZADO (Bloque de salida)
            try:
                from src.logic.init_profile import ProfileManager
                
                # 1. Guardar configuración visual
                config.shadow_theme = tema_elegido
                config.save_to_yaml()
                
                # 2. Registrar identidad en DB
                ProfileManager.registrar_usuario(
                    alias="ShadowRoot07",
                    raw_master_key=f"{k2}{k3}" # Ahora ya vienen limpios
                )
                self.app.notify(f"MATRIZ {tema_elegido} SELLADA", severity="success")

                # Salida limpia: Notifica al callback en app.py que puede re-verificar acceso
                self.dismiss(True)

            except Exception as e:
                logger.error(f"Fallo en Wizard: {e}")
                self.app.notify("Error crítico al materializar perfil.", severity="error")

    # Eliminamos el pop_screen del on_mount para evitar el ScreenStackError
    def on_mount(self) -> None:
        self.query_one("#wiz_k2").focus()


    CSS = """
    #wizard_container { padding: 2; background: #050505; border: double #00FF00; align: center middle; }
    #wiz_title { text-align: center; color: #00FF00; text-style: bold; margin-bottom: 1; }
    .wiz_label { color: #BB00FF; margin-top: 1; }
    Input { margin-bottom: 1; border: tall #333; color: #00FF00; }
    #wiz_buttons { margin-top: 2; align: center middle; }
    RadioSet { background: transparent; border: none; }
    RadioButton { color: #00FF00; }
    """

