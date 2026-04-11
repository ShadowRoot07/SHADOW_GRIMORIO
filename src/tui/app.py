import json
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, Label
from textual.containers import Container, Vertical, Center

# Lógica y Configuración
from src.logic.config import config
from src.tui.themes import THEMES
from src.utils.ascii_loader import ASCIILoader
from src.tui.widgets import TelemetryBar

# Importación de Pantallas de Flujo
from src.tui.main_menu import MainMenuScreen
from src.tui.init_wizard import InitWizard

# Importación centralizada de Modales de Agentes
from src.tui.modals import (
    WatchdogErrorModal, JanitorAuditModal,
    GhostWritingModal, BrumaSyncModal,
    ExplorerModal, VoidHunterModal
)

class ShadowGrimorio(App):
    """
    Núcleo Central del Shadow_Grimorio.
    Gestiona el ciclo de vida de los agentes y la bifurcación de seguridad.
    """
    
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

        # --- Mapeo de Reportes de Agentes ---
        self.reports = {
            "void": self.raiz_proyecto / "logs" / "void_hunter_report.json",
            "explorer": self.raiz_proyecto / "logs" / "explorer_report.json",
            "bruma": self.raiz_proyecto / "logs" / "bruma_report.json",
            "watchdog": self.raiz_proyecto / "logs" / "watchdog_report.json",
            "janitor": self.raiz_proyecto / "logs" / "janitor_report.json",
            "ghost": self.raiz_proyecto / "logs" / "ghost_report.json",
            "survival": self.raiz_proyecto / "logs" / "survival_report.json"
        }

        # --- Estado de Timestamps para evitar bucles de modales ---
        self.last_timestamps = {k: "" for k in self.reports.keys()}
        self.modal_abierto = False

    def on_mount(self) -> None:
        self.title = "SHADOW_GRIMORIO"
        self.aplicar_estilos_tema()
        
        # --- BIFURCACIÓN DE SEGURIDAD ---
        if self.es_primera_vez:
            # Si el sistema detectó que no hay perfil, lanza el Sellado
            self.push_screen(InitWizard())
        else:
            # Si ya existe, lanza el menú principal (que pedirá el Ritual)
            self.push_screen(MainMenuScreen())

        # Escaneo de pulso del sistema cada 2 segundos
        self.set_interval(2.0, self.global_observer)

    def global_observer(self) -> None:
        """Monitorea reportes de agentes y dispara modales por prioridad."""
        if self.modal_abierto:
            return

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

                    t = str(data.get("timestamp",
                           data.get("last_check",
                           data.get("last_purge", ""))))

                    if t and t != self.last_timestamps[key]:
                        self.last_timestamps[key] = t
                        self.modal_abierto = True
                        self.push_screen(modal_cls(data), callback=self.on_modal_close)
                        return 
                except Exception:
                    continue

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

    # --- Acciones de Navegación ---

    def action_chat(self) -> None:
        from src.tui.chat import ChatScreen
        self.push_screen(ChatScreen())

    def action_agentes(self) -> None:
        from src.tui.agents_menu import AgentsMenu
        self.push_screen(AgentsMenu())

    def action_main_menu(self) -> None:
        # Si ya estamos en el MainMenuScreen a través del stack, no lo duplicamos
        self.push_screen(MainMenuScreen())

    def action_back(self) -> None:
        if len(self.screen_stack) > 1:
            self.pop_screen()
            self.modal_abierto = False

    async def action_quit(self) -> None:
        self.exit()

if __name__ == "__main__":
    # Fallback para desarrollo, asume retorno de usuario
    app = ShadowGrimorio(es_primera_vez=False)
    app.run()

