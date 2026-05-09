from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input, Static
from textual.containers import Vertical, Center
from src.logic.identity_matrix import sap

class BypassRootModal(ModalScreen[bool]):
    """Ventana de bypass con protocolo de recuperación de llaves."""

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="bypass_container"):
                yield Label("💀 [ ACCESO ARQUITECTO ]", id="bypass_title")
                
                # Contenedor dinámico para cambiar entre Login y Revelación
                with Vertical(id="bypass_content"):
                    yield Label("Introduce llave Maestra para recuperar credenciales:")
                    yield Input(placeholder="••••••••••••", password=True, id="bypass_input")
                    yield Button("FORZAR ENTRADA", variant="error", id="btn_bypass")

    def on_mount(self) -> None:
        self.query_one("#bypass_input").focus()

    def ejecutar_bypass(self):
        # Capturamos y limpiamos la entrada inmediatamente
        llave = self.query_one("#bypass_input").value.strip()
        
        if not llave:
            self.app.notify("La llave no puede estar vacía", severity="error")
            return

        if sap.activar_bypass_root(llave):
            self.app.notify("LLAVE MAESTRA ACEPTADA", severity="success")
            self.mostrar_recuperacion()
        else:
            self.app.notify("ERROR: Llave de bypass inválida.", severity="error")
            # No cerramos el modal para permitir reintento
            self.query_one("#bypass_input").value = ""
            self.query_one("#bypass_input").focus()

    def mostrar_recuperacion(self):
        """Cambia la UI para mostrar las llaves K2 y K3."""
        llaves = sap.recuperar_llaves_vault()
        content = self.query_one("#bypass_content")
        
        # Limpiamos el contenido anterior
        content.query("*").remove()
        
        # Inyectamos la información de recuperación
        content.mount(
            Label("[bold green]✅ ACCESO CONCEDIDO[/]\n", classes="msg_success"),
            Label("[cyan]LLAVE DE MENTE (K2):[/]"),
            Static(f" {llaves['K2']} ", classes="key_box"),
            Label("\n[magenta]LLAVE DE ACCIÓN (K3):[/]"),
            Static(f" {llaves['K3']} ", classes="key_box"),
            Label("\n[italic yellow]Memoriza estas llaves para el acceso estándar.[/]"),
            Button("ENTRAR AL NÚCLEO", variant="success", id="btn_confirm_bypass")
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_bypass":
            self.ejecutar_bypass()
        elif event.button.id == "btn_confirm_bypass":
            self.dismiss(True)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.ejecutar_bypass()

    CSS = """
    #bypass_container {
        width: 80%;
        height: auto;
        border: thick #FF3131;
        background: #0a0000;
        padding: 1 2;
    }
    #bypass_title { text-align: center; color: #FF3131; text-style: bold; margin-bottom: 1; }
    #bypass_content { align: center middle; }
    #bypass_input { margin: 1 0; border: solid #FF3131; color: #FF3131; background: #1a0000; }
    .key_box {
        background: #111;
        color: #00FF00;
        border: dashed #333;
        padding: 0 1;
        width: 100%;
        text-align: center;
    }
    .msg_success { width: 100%; text-align: center; }
    #btn_bypass, #btn_confirm_bypass { margin-top: 1; width: 100%; }
    """

