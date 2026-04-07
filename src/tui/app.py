import json
import os
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, Label
from textual.containers import Container, Vertical, Center
from src.utils.ascii_loader import ASCIILoader
from src.logic.config import config
from src.tui.themes import THEMES
from src.tui.widgets import TelemetryBar
from src.tui.modals import WatchdogErrorModal, JanitorAuditModal, GhostWritingModal, BrumaSyncModal

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

        # Timestamps
        self.last_wd_time = ""
        self.last_jn_time = ""
        self.last_gh_time = ""
        self.last_br_time = ""

        self.modal_abierto = False

    def on_mount(self) -> None:
        self.title = "SHADOW_GRIMORIO"
        self.aplicar_estilos_tema()
        self.set_interval(2.0, self.global_observer)

    def global_observer(self) -> None:
        """Vigilancia centralizada de reportes."""
        if self.modal_abierto: 
            return

        # 4. Chequeo Bruma_Sync (Prioridad en este debug)
        if self.br_report.exists():
            try:
                with open(self.br_report, "r") as f:
                    data = json.load(f)
                t = str(data.get("timestamp", ""))
                
                if t != self.last_br_time:
                    self.last_br_time = t
                    self.modal_abierto = True
                    # Empujamos la pantalla y forzamos el callback de cierre
                    self.push_screen(BrumaSyncModal(data), callback=self.on_modal_close)
                    return
            except Exception:
                pass

        # 1, 2, 3 (Otros agentes permanecen igual pero con la seguridad de modal_abierto)
        for report, last_time, modal_cls in [
            (self.wd_report, "last_wd_time", WatchdogErrorModal),
            (self.jn_report, "last_jn_time", JanitorAuditModal),
            (self.gh_report, "last_gh_time", GhostWritingModal),
        ]:
            if report.exists():
                try:
                    with open(report, "r") as f: data = json.load(f)
                    # Lógica simplificada para el debug
                    timestamp_key = "last_check" if "last_check" in data else ("last_purge" if "last_purge" in data else "timestamp")
                    t = str(data.get(timestamp_key, ""))
                    
                    if t != getattr(self, last_time):
                        setattr(self, last_time, t)
                        self.modal_abierto = True
                        self.push_screen(modal_cls(data), callback=self.on_modal_close)
                        return
                except: pass

    def on_modal_close(self, _=None) -> None:
        """Callback agresivo para asegurar que el observer siga trabajando."""
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
        if len(self.screen_stack) > 1: 
            self.pop_screen()
            self.modal_abierto = False # Reset preventivo

    async def action_quit(self) -> None:
        self.exit()

