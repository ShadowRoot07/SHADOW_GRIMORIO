from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Log, Header, Footer
from textual.containers import Container
from src.api.groq_client import oraculo
from src.logic.init_profile import ProfileManager # Para obtener el alias real
from loguru import logger

class ChatScreen(Screen):
    """Interfaz de comunicación sagrada con el Oráculo del Grimorio."""

    # Estilos CSS específicos para la terminal del ZTE (Cyberpunk Dark)
    CSS = """
    ChatScreen {
        background: #000800;
    }
    #chat_container {
        height: 1fr;
        margin: 1 2;
        border: tall #00ff00;
        background: #000500;
    }
    #chat_log {
        height: 1fr;
        border: none;
        color: #00ff00;
    }
    #chat_input {
        dock: bottom;
        margin: 1;
        border: double #00ffff;
        background: #001100;
        color: #ffffff;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="chat_container"):
            yield Log(id="chat_log", highlight=True)
            yield Input(placeholder="Escribe tu consulta al Oráculo...", id="chat_input")
        yield Footer()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        chat_log = self.query_one("#chat_log")
        chat_input = self.query_one("#chat_input")
        user_input = event.value.strip()
        
        if not user_input:
            return

        # 1. Limpiar el campo y mostrar mensaje del usuario
        chat_input.value = ""
        # Podríamos sacar el alias dinámicamente de la DB luego
        chat_log.write(f"\n[ShadowRoot07]: {user_input}\n", scroll_end=True)
        
        # 2. Estado de espera
        chat_log.write("[SISTEMA]: Consultando las hebras del Oráculo...", scroll_end=True)
        
        try:
            # 3. Llamada al Oráculo (IA) con el filtrado de modelos que ya programamos
            # Nota: Mañana integraremos aquí el ContextInjector para que use tu DB
            respuesta = await oraculo.consultar(user_input)
            
            # 4. Mostrar respuesta de la IA
            chat_log.write(f"\n[SHADOW_GRIMORIO]: {respuesta}\n", scroll_end=True)
            
        except Exception as e:
            logger.error(f"Fallo en la conexión del chat: {e}")
            chat_log.write("\n[ERROR]: El vínculo con el Oráculo se ha fragmentado.\n")

    def action_quit(self) -> None:
        """Permite volver a la pantalla anterior con 'q'."""
        self.app.pop_screen()

