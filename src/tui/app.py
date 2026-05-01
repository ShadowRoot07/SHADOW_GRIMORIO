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
from src.logic.config import config
from src.tui.themes import THEMES, get_theme
from loguru import logger

from src.tui.modals import (
    WatchdogErrorModal, JanitorAuditModal,
    GhostWritingModal, BrumaSyncModal,
    ExplorerModal, VoidHunterModal
)

class ShadowGrimorio(App):
    """Núcleo Central del Shadow_Grimorio."""

    BINDINGS = [
        ("q", "quit", "Salir"),
        ("t", "next_theme", "Cambiar Tema"), # 1. Registro de la tecla
        ("f1", "bypass_root", "Bypass"),
        ("g", "agentes", "Agentes"),
        ("c", "chat", "Oráculo"),
        ("m", "show_map", "Mapa"),
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

    def safe_navigate(self, target_screen) -> None:
        """Navegación blindada contra el ScreenStackError."""
        # Si el stack tiene 1 o menos pantallas, NO USAMOS switch_screen.
        # Usamos push para asegurar que siempre haya algo debajo.
        if len(self.screen_stack) <= 1:
            self.push_screen(target_screen)
        else:
            # Si hay varias pantallas, podemos intercambiar la de arriba
            self.switch_screen(target_screen)

    def verificar_acceso_shadow(self) -> None:
        session = db.get_session()
        try:
            # 1. Prioridad: ¿Tenemos bypass activo en esta sesión?
            if sap.root_bypass_active:
                from src.tui.main_menu import MainMenuScreen
                self.safe_navigate(MainMenuScreen())
                return

            session.expire_all()
            user = session.query(Usuario).first()

            if not user:
                from src.tui.init_wizard import InitWizard
                self.push_screen(InitWizard(), callback=lambda _: self.verificar_acceso_shadow())
                return

            # 2. Si no hay bypass, verificamos el rango del usuario en DB
            # Si el usuario es Shadow_Coder (Root), pero root_bypass_active es False,
            # significa que necesita pasar por el Ritual (Login)
            if user.rango_rel and user.rango_rel.nombre == "Shadow_Coder":
                if not sap.root_bypass_active:
                    from src.tui.ritual import ShadowRitualModal
                    self.safe_navigate(ShadowRitualModal())
                    return

            # 3. Solo si NO es root y NO ha terminado, va a los Trials
            if user.pruebas_completadas is False:
                self.sincronizar_estado_trials()
                return

            # 4. Caso general: Ritual de acceso
            from src.tui.ritual import ShadowRitualModal
            self.safe_navigate(ShadowRitualModal())

        except Exception as e:
            logger.error(f"Error en guardián: {e}")
        finally:
            session.close()

    def sincronizar_estado_trials(self) -> None:
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            progreso = user.progreso_trials or ""
            
            # Decidir qué pantalla cargar
            if "F2" in progreso or "F1_COMPLETADA" in progreso:
                from src.tui.trial_screen_v2 import TrialScreenV2
                target = TrialScreenV2()
            else:
                from src.tui.trial_screen import TrialScreen
                target = TrialScreen()

            # Transición segura
            if len(self.screen_stack) > 1:
                self.switch_screen(target)
            else:
                self.push_screen(target)
        finally:
            session.close()

    def global_observer(self) -> None:
        """Observador unificado. Solo dispara si el usuario ya está logueado."""
        # Evitamos interrupciones si no hay acceso total o hay un modal activo
        if self.modal_abierto or not sap.tiene_acceso_total():
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
                    # Detectar cambios reales por timestamp
                    t = str(data.get("timestamp", data.get("last_check", "")))
                    if t and t != self.last_timestamps[key]:
                        self.last_timestamps[key] = t
                        self.modal_abierto = True
                        self.push_screen(modal_cls(data), callback=self.on_modal_close)
                        return # Solo mostramos uno por ciclo
                except Exception:
                    continue


    def action_show_map(self) -> None:
        """Carga y muestra el mapa manualmente."""
        path = self.reports["explorer"]
        if path.exists():
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                self.push_screen(ExplorerModal(data))
            except Exception as e:
                self.notify(f"Error al leer mapa: {e}", severity="error")
        else:
            self.notify("El mapa aún no ha sido trazado por Explorer.", severity="warning")

    def action_next_theme(self) -> None:
        """Cicla entre los temas disponibles y persiste la elección."""
        nombres_temas = list(THEMES.keys())
        try:
            indice_actual = nombres_temas.index(self.nombre_tema)
            siguiente_indice = (indice_actual + 1) % len(nombres_temas)
        except ValueError:
            siguiente_indice = 0

        # 2. Actualizar estado en memoria
        self.nombre_tema = nombres_temas[siguiente_indice]
        self.tema = THEMES[self.nombre_tema]
        
        # 3. Persistir en config.yaml
        config.shadow_theme = self.nombre_tema
        config.save_to_yaml()

        # 4. Notificar y refrescar visualmente
        self.aplicar_estilos_tema()
        self.notify(f"MATRIZ RECONFIGURADA: {self.nombre_tema}", severity="information")
        
        # Forzar refresco de toda la interfaz
        self.refresh()

    def aplicar_estilos_tema(self) -> None:
        """Inyecta los colores del tema actual en la pantalla activa."""
        if hasattr(self, 'screen') and self.screen:
            # Aplicar fondo global
            self.screen.styles.background = self.tema.get('bg', "#000000")
            # Podemos forzar colores de texto base si es necesario
            self.screen.styles.color = self.tema.get('text', "#ffffff")

    def on_mount(self) -> None:
        self.title = "SHADOW_GRIMORIO"
        self.aplicar_estilos_tema()
        
        # Protocolo de inicio seguro: 300ms para estabilizar el renderizado en móvil
        self.set_timer(1.2, self.verificar_acceso_shadow)
        self.set_interval(2.0, self.global_observer)

    def watch_screen(self, screen) -> None:
        self.aplicar_estilos_tema()

    def action_bypass_root(self) -> None:
        def check_bypass(success: bool):
            if success:
                # El usuario ya vio sus llaves, ahora refrescamos al MainMenu
                self.notify("🔄 SINCRONIZANDO RANGO: ROOT", severity="information")
                # Forzamos que sap.tiene_acceso_total() devuelva True
                sap.root_bypass_active = True
                # PEQUEÑO AJUSTE: Retardo de 0.5s para estabilizar el stack en móvil
                self.set_timer(0.5, self.verificar_acceso_shadow)

        self.push_screen(BypassRootModal(), callback=check_bypass)

    def esta_bloqueado(self) -> bool:
        return not sap.tiene_acceso_total()

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
        # MODIFICACIÓN: Verificamos que haya más de 1 pantalla para no vaciar el stack
        if len(self.screen_stack) > 1:
            # Si la pantalla actual es un modal, reseteamos el flag
            self.modal_abierto = False
            self.pop_screen()

    async def action_quit(self) -> None:
        self.app.notify("Desconectando de la Matriz...", severity="warning")
        self.exit()

