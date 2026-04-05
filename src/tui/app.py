import json
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, Label
from textual.containers import Container, Vertical, Center
from src.utils.ascii_loader import ASCIILoader
from src.logic.config import config
from src.tui.themes import THEMES
from src.tui.widgets import TelemetryBar
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
        
        # Ruta absoluta calculada desde la raíz
        self.raiz_proyecto = Path(__file__).resolve().parents[2]
        self.report_path = self.raiz_proyecto / "logs" / "watchdog_report.json"
        self.last_check_time = ""
        self.modal_abierto = False

    def on_mount(self) -> None:
        self.title = "SHADOW_GRIMORIO"
        self.aplicar_estilos_tema()
        # Escaneo constante cada 2 segundos
        self.set_interval(2.0, self.check_watchdog)

    def aplicar_estilos_tema(self) -> None:
        self.screen.styles.background = self.tema['bg']

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        with Container(id="main_layout"):
            with Vertical():
                with Center(): yield Static(ASCIILoader.get_art('splash'), id="logo")
                yield Label("[ NÚCLEO ONLINE ]", id="status")
        yield Footer()

    def check_watchdog(self) -> None:
        if not self.report_path.exists() or self.modal_abierto:
            return

        try:
            with open(self.report_path, "r") as f:
                data = json.load(f)
            
            if data.get("status") == "syntax_error":
                timestamp = data.get("last_check")
                if timestamp != self.last_check_time:
                    self.last_check_time = timestamp
                    self.modal_abierto = True
                    self.push_screen(WatchdogErrorModal(data), callback=self.on_modal_close)
            elif data.get("status") == "OK":
                self.last_check_time = ""
        except: pass

    def on_modal_close(self, _=None):
        self.modal_abierto = False

    # Acciones de navegación...
    def action_chat(self) -> None:
        from src.tui.chat import ChatScreen
        self.push_screen(ChatScreen())

    def action_agentes(self) -> None:
        from src.tui.agents_menu import AgentsMenu
        self.push_screen(AgentsMenu())

    def action_back(self) -> None:
        if len(self.screen_stack) > 1: self.pop_screen()

    async def action_quit(self) -> None:
        self.exit()

