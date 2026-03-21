from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Log, Header, Footer
from textual.containers import Container
from src.api.groq_client import oraculo
from src.database.manager import db
from src.database.models import Usuario
from loguru import logger

class ChatScreen(Screen):
    """Interfaz de comunicación sagrada con el Oráculo del Grimorio."""

    # Estilos CSS optimizados para terminal móvil (Cyberpunk Theme)
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

        # 1. Obtener alias real de la base de datos
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            alias = user.alias if user else "ShadowRoot07"
        except Exception:
            alias = "ShadowRoot07"
        finally:
            session.close()

        # 2. Limpiar el campo y mostrar mensaje del usuario
        chat_input.value = ""
        chat_log.write(f"\n[{alias}]: {user_input}\n", scroll_end=True)

        # 3. Estado de espera visual
        chat_log.write("[SISTEMA]: Consultando las hebras del Oráculo...", scroll_end=True)

        try:
            # 4. Llamada al Oráculo (ya incluye el ContextInjector internamente)
            respuesta = await oraculo.consultar(user_input)

            # 5. Mostrar respuesta de la IA
            chat_log.write(f"\n[SHADOW_GRIMORIO]: {respuesta}\n", scroll_end=True)

        except Exception as e:
            logger.error(f"Fallo en la conexión del chat: {e}")
            chat_log.write("\n[ERROR]: El vínculo con el Oráculo se ha fragmentado.\n")

    def action_quit(self) -> None:
        """Vuelve a la pantalla anterior con 'q'."""
        self.app.pop_screen()

