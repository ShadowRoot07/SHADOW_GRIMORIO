from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, Label
from textual.containers import Container, Vertical, Center
from src.utils.ascii_loader import ASCIILoader
from src.logic.config import config
from src.tui.themes import THEMES
from src.tui.widgets import TelemetryBar, WatchdogObserver
from src.tui.modals import WatchdogErrorModal

class ShadowGrimorio(App):
    BINDINGS = [
        ("q", "quit", "Salir"),
        ("g", "agentes", "Agentes"),
        ("c", "chat", "Oráculo"),
        ("t", "next_theme", "Tema"),
        ("m", "main_menu", "Matriz"),
        ("escape", "back", "Volver")
    ]

    def __init__(self):
        super().__init__()
        self.nombre_tema = config.shadow_theme
        self.tema = THEMES.get(self.nombre_tema, THEMES["CYBERPUNK"])
        self.last_oraculo_response = ""

    def on_mount(self) -> None:
        self.title = "SHADOW_GRIMORIO"
        self.aplicar_estilos_tema()

    def aplicar_estilos_tema(self) -> None:
        t = self.tema
        self.screen.styles.background = t['bg']

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        # IMPORTANTE: Asignamos ID para que el manejador de eventos lo reconozca
        yield WatchdogObserver(id="watchdog_observer") 
        
        with Container(id="main_layout"):
            with Vertical():
                with Center():
                    yield Static(ASCIILoader.get_art('splash'), id="logo")
                yield Label("[ NÚCLEO ONLINE ]", id="status")
        yield Footer()

    # --- MANEJO DE EVENTOS DEL WATCHDOG ---
    # El nombre debe coincidir con: on + id_del_widget + nombre_del_mensaje
    def on_watchdog_observer_syntax_error_detected(self, event: WatchdogObserver.SyntaxErrorDetected) -> None:
        """Captura el error del observador y lanza el modal rojo."""
        self.push_screen(WatchdogErrorModal(event.data))

    def action_back(self) -> None:
        if len(self.screen_stack) > 1:
            self.pop_screen()

    def action_chat(self) -> None:
        from src.tui.chat import ChatScreen
        self.push_screen(ChatScreen())

    def action_main_menu(self) -> None:
        from src.tui.main_menu import MainMenuScreen
        self.push_screen(MainMenuScreen())

    def action_agentes(self) -> None:
        from src.tui.agents_menu import AgentsMenu
        self.push_screen(AgentsMenu())

    async def action_quit(self) -> None:
        self.exit()

