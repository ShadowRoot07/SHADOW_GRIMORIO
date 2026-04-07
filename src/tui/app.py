import json
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, Label
from textual.containers import Container, Vertical, Center
from src.utils.ascii_loader import ASCIILoader
from src.logic.config import config
from src.tui.themes import THEMES
from src.tui.widgets import TelemetryBar
from src.tui.modals import WatchdogErrorModal, JanitorAuditModal, GhostWritingModal, , BrumaSyncModal

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
        self.raiz_proyecto = Path(__file__).resolve().parents[2]

        # Rutas de Reportes
        self.wd_report = self.raiz_proyecto / "logs" / "watchdog_report.json"
        self.jn_report = self.raiz_proyecto / "logs" / "janitor_report.json"
        self.gh_report = self.raiz_proyecto / "logs" / "ghost_report.json"
        self.br_report = self.raiz_proyecto / "logs" / "bruma_report.json"

        # Timestamps para evitar bucles
        self.last_wd_time = ""
        self.last_jn_time = ""
        self.last_gh_time = ""

        self.modal_abierto = False

    def on_mount(self) -> None:
        self.title = "SHADOW_GRIMORIO"
        self.aplicar_estilos_tema()
        self.set_interval(2.0, self.global_observer)

    def global_observer(self) -> None:
        """Vigilancia centralizada de reportes de agentes."""
        if self.modal_abierto: return

        # 1. Chequeo Watchdog (Rojo)
        if self.wd_report.exists():
            try:
                with open(self.wd_report, "r") as f: 
                    data = json.load(f)
                if data.get("status") == "syntax_error":
                    t = str(data.get("last_check", ""))
                    if t != self.last_wd_time:
                        self.last_wd_time = t
                        self.modal_abierto = True
                        self.push_screen(WatchdogErrorModal(data), callback=self.on_modal_close)
                        return # Evitar múltiples modales a la vez
            except: pass

        # 2. Chequeo Janitor (Púrpura)
        if self.jn_report.exists():
            try:
                with open(self.jn_report, "r") as f: 
                    data = json.load(f)
                t = str(data.get("last_purge", ""))
                if t != self.last_jn_time:
                    self.last_jn_time = t
                    self.modal_abierto = True
                    self.push_screen(JanitorAuditModal(data), callback=self.on_modal_close)
                    return
            except: pass

        # 3. Chequeo Ghost_Coder (Cian)
        if self.gh_report.exists():
            try:
                with open(self.gh_report, "r") as f: 
                    data = json.load(f)
                # Convertimos a string el timestamp numérico del JSON
                t = str(data.get("timestamp", ""))
                if t != self.last_gh_time:
                    self.last_gh_time = t
                    self.modal_abierto = True
                    self.push_screen(GhostWritingModal(data), callback=self.on_modal_close)
            except: pass

        if self.br_report.exists():
            try:
                with open(self.br_report, "r") as f: data = json.load(f)
                t = str(data.get("timestamp", ""))
                if t != self.last_br_time:
                    self.last_br_time = t
                    self.modal_abierto = True
                    self.push_screen(BrumaSyncModal(data), callback=self.on_modal_close)
                    return
            except: pass

    def on_modal_close(self, _=None):
        self.modal_abierto = False

    def aplicar_estilos_tema(self) -> None:
        self.screen.styles.background = self.tema['bg']

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        with Container(id="main_layout"):
            with Vertical():
                with Center(): yield Static(ASCIILoader.get_art('splash'), id="logo")
                yield Label("[ NÚCLEO ONLINE ]", id="status")
        yield Footer()

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

