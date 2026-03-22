from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Log, Footer
from textual.containers import Container
from src.tui.widgets import TelemetryBar
from src.api.groq_client import oraculo

class ChatScreen(Screen):
    CSS = """
    ChatScreen { background: #000800; }
    #chat_container {
        border: tall #00ff00;
        margin: 0 1;
        height: 1fr;
    }
    #chat_log { height: 1fr; color: #00ff00; border: none; }
    #chat_input { dock: bottom; border: double #00ffff; margin: 1 0; }
    """

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        with Container(id="chat_container") as c:
            c.border_title = "CONEXIÓN CON EL ORÁCULO"
            yield Log(id="chat_log")
            yield Input(placeholder="Escribe y presiona Enter...", id="chat_input")
        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Se activa al dar Enter en el teclado del ZTE."""
        texto = event.value.strip()
        if not texto:
            return

        log = self.query_one("#chat_log", Log)
        input_widget = self.query_one("#chat_input", Input)

        # 1. Limpiar input y mostrar mensaje del usuario
        input_widget.value = ""
        log.write(f"\n[USER]: {texto}")

        # 2. Consultar al Oráculo
        log.write("[SISTEMA]: Consultando a la matriz...")
        try:
            # Usamos run_in_executor o simplemente await si oraculo.consultar es async
            respuesta = await oraculo.consultar(texto)
            log.write(f"\n[ORÁCULO]: {respuesta}\n")
        except Exception as e:
            log.write(f"\n[ERROR]: {str(e)}")
