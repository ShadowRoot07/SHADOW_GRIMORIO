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

# Importación centralizada de Modales
from src.tui.modals import (
    WatchdogErrorModal, JanitorAuditModal,
    GhostWritingModal, BrumaSyncModal,
    ExplorerModal, VoidHunterModal
)

class ShadowGrimorio(App):
    """
    Núcleo Central del Shadow_Grimorio.
    Gestiona el ciclo de vida de los agentes y la interfaz principal.
    """
    
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
        # Escaneo de pulso del sistema cada 2 segundos
        self.set_interval(2.0, self.global_observer)

    def global_observer(self) -> None:
        """
        Observador de Oráculo: Monitorea cambios en los archivos JSON de los agentes
        y dispara los modales correspondientes por orden de prioridad.
        """
        if self.modal_abierto:
            return

        # Definición de prioridad y mapeo a modales
        # (Ruta, Clave interna del JSON, Clase del Modal)
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
                    
                    # Intentar obtener un timestamp válido del JSON
                    t = str(data.get("timestamp", 
                           data.get("last_check", 
                           data.get("last_purge", ""))))

                    if t and t != self.last_timestamps[key]:
                        self.last_timestamps[key] = t
                        self.modal_abierto = True
                        self.push_screen(modal_cls(data), callback=self.on_modal_close)
                        return # Solo procesar un evento por ciclo
                except Exception:
                    continue

    def on_modal_close(self, _=None) -> None:
        """Libera el bloqueo de modales al cerrar una ventana."""
        self.modal_abierto = False

    def aplicar_estilos_tema(self) -> None:
        """Sincroniza el fondo de la pantalla con el tema actual."""
        self.screen.styles.background = self.tema['bg']

    def compose(self) -> ComposeResult:
        """Construye la arquitectura visual base."""
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
        from src.tui.main_menu import MainMenuScreen
        self.push_screen(MainMenuScreen())

    def action_back(self) -> None:
        if len(self.screen_stack) > 1:
            self.pop_screen()
            self.modal_abierto = False

    async def action_quit(self) -> None:
        self.exit()

if __name__ == "__main__":
    # Punto de entrada para ejecución directa
    app = ShadowGrimorio()
    app.run()

