import json
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Static, Label
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
from src.tui.bypass_modal import BypassRootModal

from src.tui.modals import (
    WatchdogErrorModal, JanitorAuditModal,
    GhostWritingModal, BrumaSyncModal,
    ExplorerModal, VoidHunterModal
)

class ShadowGrimorio(App):
    """Núcleo Central del Shadow_Grimorio."""

    BINDINGS = [
        ("q", "quit", "Salir"),
        ("f1", "bypass_root", "Bypass"),
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
        
        # Protocolo de inicio seguro: 300ms para estabilizar el renderizado en móvil
        self.set_timer(0.3, self.verificar_acceso_shadow)
        self.set_interval(2.0, self.global_observer)

    def watch_screen(self, screen) -> None:
        self.aplicar_estilos_tema()

    def action_bypass_root(self) -> None:
        def check_bypass(success: bool):
            if success:
                self.notify("🔄 RECONECTANDO MATRIZ...", severity="information")
                self.set_timer(0.2, self.verificar_acceso_shadow)

        self.push_screen(BypassRootModal(), callback=check_bypass)

    def esta_bloqueado(self) -> bool:
        return not sap.tiene_acceso_total()

    def verificar_acceso_shadow(self) -> None:
        """Sincroniza el estado de la DB con la UI de forma protegida."""
        try:
            if not self._running:
                return

            if sap.tiene_acceso_total():
                if not isinstance(self.screen, MainMenuScreen):
                    # Usamos push_screen para mantener la estabilidad de la pila
                    self.push_screen(MainMenuScreen())
                return

            if not sap.verificar_perfil_existente():
                if self.es_primera_vez:
                    sap.inicializar_usuario_debug()
                if not isinstance(self.screen, InitWizard):
                    self.push_screen(InitWizard())
                return

            self.sincronizar_estado_trials()
        except Exception:
            # Silenciamos errores de renderizado asíncrono durante el boot
            pass

    def sincronizar_estado_trials(self) -> None:
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            if user and not user.pruebas_completadas:
                rango_nombre = user.rango_rel.nombre if user.rango_rel else "Iniciado"
                if rango_nombre == "Iniciado" or rango_nombre.startswith("F1_S"):
                    from src.tui.trial_screen import TrialScreen
                    if not isinstance(self.screen, TrialScreen):
                        self.push_screen(TrialScreen())
                elif rango_nombre == "F1_COMPLETADA" or rango_nombre.startswith("F2_"):
                    from src.tui.trial_screen_v2 import TrialScreenV2
                    if not isinstance(self.screen, TrialScreenV2):
                        self.push_screen(TrialScreenV2())
        finally:
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
        if hasattr(self, 'screen') and self.screen:
            self.screen.styles.background = self.tema.get('bg', "#000000")

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        with Container(id="main_layout"):
            with Vertical():
                with Center():
                    yield Static(ASCIILoader.get_art('splash'), id="logo")
                yield Label("[ NÚCLEO ONLINE ]", id="status")
        # ELIMINADO: yield Footer() aquí causaba el ScreenStackError.
        # Ahora cada pantalla renderiza su propio Footer localmente.

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
        if not isinstance(self.screen, MainMenuScreen):
            self.push_screen(MainMenuScreen())

    def action_back(self) -> None:
        if self.esta_bloqueado(): return
        if len(self.screen_stack) > 1:
            self.pop_screen()
            self.modal_abierto = False

    async def action_quit(self) -> None:
        self.app.notify("Desconectando de la Matriz...", severity="warning")
        self.exit()

