from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import ListItem, ListView, Label, Footer, Switch, Button
from textual.containers import Horizontal, Vertical
from src.tui.widgets import TelemetryBar
from src.tui.ritual import ShadowRitualModal
from src.logic.identity_matrix import sap # Importamos SAP

class MenuOption(ListItem):
    def __init__(self, icon: str, title: str, description: str, widget_type: str = "button", locked: bool = False):
        super().__init__()
        self.icon = icon
        self.title = title
        self.description = description
        self.widget_type = widget_type
        self.locked = locked
        self.safe_id = title.lower().replace(" ", "_")

    def compose(self) -> ComposeResult:
        with Horizontal(classes="menu_row"):
            yield Label(self.icon if not self.locked else "🔒", classes="menu_icon")
            with Vertical(classes="menu_text"):
                yield Label(self.title, classes="menu_title")
                yield Label(self.description, classes="menu_desc")

            if self.widget_type == "switch":
                yield Switch(id=f"sw_{self.safe_id}", disabled=self.locked)
            else:
                # Si está bloqueado, el botón cambia visualmente
                yield Button("EJECUTAR" if not self.locked else "BLOQUEADO",
                             id=f"btn_{self.safe_id}",
                             variant="primary" if not self.locked else "error",
                             disabled=self.locked)

class MainMenuScreen(Screen):
    def compose(self) -> ComposeResult:
        # Consultamos el estado real del protocolo SAP
        is_root = sap.tiene_acceso_total()
        
        yield TelemetryBar()
        with Vertical(id="menu_container"):
            yield Label(" [ MATRIZ DE INFRAESTRUCTURA ] ", id="menu_title_main")
            with ListView(id="main_menu_list", initial_index=None):
                # Si ya es root, el ritual no es necesario (bloqueado por éxito)
                yield MenuOption("🔓", "INICIAR RITUAL", "Validar llaves de acceso", "button", locked=is_root)
                
                # Protocolos operativos: desbloqueados si es root
                yield MenuOption("🧟", "PROTOCOLO LAZARO", "Recuperar botín desde GitHub", "button", locked=not is_root)
                yield MenuOption("🧹", "JANITOR PROTOCOL", "Limpieza de logs y temporales", "button", locked=not is_root)
                yield MenuOption("💀", "PURGA TOTAL", "Eliminar datos locales sensibles", "button", locked=not is_root)
        yield Footer()

    def on_mount(self) -> None:
        self.set_timer(0.1, self.focus_list)

    def focus_list(self):
        try:
            lista = self.query_one("#main_menu_list", ListView)
            lista.index = 0
            lista.focus()
        except: pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_iniciar_ritual":
            self.app.push_screen(ShadowRitualModal(), self.finalizar_ritual)

    def finalizar_ritual(self, resultado: bool) -> None:
        if resultado:
            # Forzamos al SAP a reconocer el acceso si el ritual fue exitoso
            sap.root_bypass_active = True 
            self.app.switch_screen(MainMenuScreen())

    CSS = """
    #menu_container { margin: 1 1; height: 1fr; border: tall #00FF00; }
    #menu_title_main { width: 100%; text-align: center; text-style: bold; padding: 1; background: #111111; color: #BB00FF; }
    MenuOption { height: 5; margin: 0 1; border-bottom: solid #333333; background: #050505; }
    .menu_row { align: center middle; width: 100%; height: 100%; }
    .menu_icon { width: 6; margin-left: 1; }
    .menu_text { width: 1fr; margin-left: 1; }
    .menu_title { text-style: bold; color: #00FF00; }
    .menu_desc { text-style: italic; color: #AAAAAA; }
    """

