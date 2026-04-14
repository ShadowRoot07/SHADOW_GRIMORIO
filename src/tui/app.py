import json
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, Label
from textual.containers import Container, Vertical, Center

from src.logic.config import config
from src.tui.themes import THEMES
from src.utils.ascii_loader import ASCIILoader
from src.tui.widgets import TelemetryBar
from src.database.manager import db
from src.database.models import Usuario

from src.tui.main_menu import MainMenuScreen
from src.tui.init_wizard import InitWizard
from src.logic.identity_matrix import sap

from src.tui.modals import (
    WatchdogErrorModal, JanitorAuditModal,
    GhostWritingModal, BrumaSyncModal,
    ExplorerModal, VoidHunterModal
)

class ShadowGrimorio(App):
    """Núcleo Central del Shadow_Grimorio."""

    BINDINGS = [
        ("q", "quit", "Salir"),
        ("g", "agentes", "Agentes"),
        ("c", "chat", "Oráculo"),
        ("t", "next_theme", "Tema"),
        ("m", "main_menu", "Matriz"),
        ("escape", "back", "Volver")
    ]

    def __init__(self, es_primera_vez: bool = False):
        super().__init__()
        self.es_primera_vez = es_primera_vez
        self.nombre_tema = config.shadow_theme
        self.tema = THEMES.get(self.nombre_tema, THEMES["CYBERPUNK"])
        self.raiz_proyecto = Path(__file__).resolve().parents[2]

        self.reports = {
            "void": self.raiz_proyecto / "logs" / "void_hunter_report.json",
            "explorer": self.raiz_proyecto / "logs" / "explorer_report.json",
            "bruma": self.raiz_proyecto / "logs" / "bruma_report.json",
            "watchdog": self.raiz_proyecto / "logs" / "watchdog_report.json",
            "janitor": self.raiz_proyecto / "logs" / "janitor_report.json",
            "ghost": self.raiz_proyecto / "logs" / "ghost_report.json",
            "survival": self.raiz_proyecto / "logs" / "survival_report.json"
        }

        self.last_timestamps = {k: "" for k in self.reports.keys()}
        self.modal_abierto = False

    def on_mount(self) -> None:
        self.title = "SHADOW_GRIMORIO"
        self.aplicar_estilos_tema()
        self.verificar_acceso_shadow()
        self.set_interval(2.0, self.global_observer)

    def esta_bloqueado(self) -> bool:
        """Verifica si el acceso está restringido por pruebas pendientes."""
        session = db.get_session()
        user = session.query(Usuario).first()
        # Si no hay usuario o las pruebas no están marcadas como completadas
        bloqueado = user is None or not user.pruebas_completadas
        session.close()
        return bloqueado

    def verificar_acceso_shadow(self) -> None:
        if not sap.verificar_perfil_existente():
            sap.inicializar_usuario_debug()
            self.push_screen(InitWizard())
            return

        session = db.get_session()
        user = session.query(Usuario).first()

        # Si no hay usuario o las pruebas globales no están en True
        if user and not user.pruebas_completadas:
            try:
                # Caso A: Recién iniciado o en medio de Fase 1
                if user.rango == "Iniciado" or user.rango.startswith("F1_S"):
                    from src.tui.trial_screen import TrialScreen
                    self.push_screen(TrialScreen())
                
                # Caso B: Fase 1 lista, saltar a Fase 2 (Aquí estaba el bug)
                elif user.rango == "F1_COMPLETADA" or user.rango.startswith("F2_"):
                    from src.tui.trial_screen_v2 import TrialScreenV2
                    self.push_screen(TrialScreenV2())
                
                # Caso C: Fallback
                else:
                    from src.tui.trial_screen import TrialScreen
                    self.push_screen(TrialScreen())
            except ImportError as e:
                self.notify(f"Error crítico de módulos: {e}", severity="error")
        else:
            # Solo entramos aquí si pruebas_completadas == True
            self.push_screen(MainMenuScreen())

        session.close()

    def global_observer(self) -> None:
        if self.modal_abierto or self.esta_bloqueado(): return

        prioridad_agentes = [
            (self.reports["void"], "void", VoidHunterModal),
            (self.reports["watchdog"], "watchdog", WatchdogErrorModal),
            (self.reports["explorer"], "explorer", ExplorerModal),
            (self.reports["bruma"], "bruma", BrumaSyncModal),
            (self.reports["janitor"], "janitor", JanitorAuditModal),
            (self.reports["ghost"], "ghost", GhostWritingModal),
        ]

        for path, key, modal_cls in prioridad_agentes:
            if path.exists():
                try:
                    with open(path, "r") as f:
                        data = json.load(f)
                    t = str(data.get("timestamp", data.get("last_check", data.get("last_purge", ""))))
                    if t and t != self.last_timestamps[key]:
                        self.last_timestamps[key] = t
                        self.modal_abierto = True
                        self.push_screen(modal_cls(data), callback=self.on_modal_close)
                        return
                except Exception: continue

    def on_modal_close(self, _=None) -> None:
        self.modal_abierto = False

    def aplicar_estilos_tema(self) -> None:
        self.screen.styles.background = self.tema['bg']

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        with Container(id="main_layout"):
            with Vertical():
                with Center():
                    yield Static(ASCIILoader.get_art('splash'), id="logo")
                yield Label("[ NÚCLEO ONLINE ]", id="status")
        yield Footer()

    def action_chat(self) -> None:
        if self.esta_bloqueado(): return
        from src.tui.chat import ChatScreen
        self.push_screen(ChatScreen())

    def action_agentes(self) -> None:
        if self.esta_bloqueado(): return
        from src.tui.agents_menu import AgentsMenu
        self.push_screen(AgentsMenu())

    def action_main_menu(self) -> None:
        if self.esta_bloqueado(): return
        self.push_screen(MainMenuScreen())

    def action_back(self) -> None:
        if self.esta_bloqueado(): return
        if len(self.screen_stack) > 1:
            self.pop_screen()
            self.modal_abierto = False

    async def action_quit(self) -> None:
        self.exit()

