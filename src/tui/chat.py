from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Log, Footer
from textual.containers import Container
from src.tui.widgets import TelemetryBar
from src.api.groq_client import oraculo

class ChatScreen(Screen):
    def on_mount(self) -> None:
        """Aplica los colores del tema global al entrar."""
        t = self.app.tema
        self.styles.background = t['bg']
        container = self.query_one("#chat_container")
        container.styles.border = ("tall", t['primary'])
        
        chat_log = self.query_one("#chat_log")
        chat_log.styles.color = t['primary']
        
        chat_input = self.query_one("#chat_input")
        chat_input.styles.border = ("double", t['accent'])
        chat_input.styles.color = t['text']

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        with Container(id="chat_container") as c:
            c.border_title = "CONEXIÓN CON EL ORÁCULO"
            # Ajustamos el Log para que sea scrolleable y limpio
            yield Log(id="chat_log", highlight=True)
            yield Input(placeholder="Escribe al Oráculo...", id="chat_input")
        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        texto = event.value.strip()
        if not texto:
            return

        log = self.query_one("#chat_log", Log)
        input_widget = self.query_one("#chat_input", Input)

        input_widget.value = ""
        log.write(f"\n[USER]: {texto}")
        log.write(" >> [SISTEMA]: Consultando a la matriz...")

        try:
            # Pasamos el agente_id como None para el chat general
            respuesta = await oraculo.consultar(texto)
            log.write(f"\n[ORÁCULO]: {respuesta}\n")
        except Exception as e:
            log.write(f"\n[ERROR CRÍTICO]: {str(e)}")
        
        log.scroll_end()

