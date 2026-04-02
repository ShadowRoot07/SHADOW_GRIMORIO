from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import ListItem, ListView, Label, Footer, Switch, Button
from textual.containers import Horizontal, Vertical
from src.tui.widgets import TelemetryBar

class MenuOption(ListItem):
    def __init__(self, icon: str, title: str, description: str, widget_type: str = "button"):
        super().__init__()
        self.icon = icon
        self.title = title
        self.description = description
        self.widget_type = widget_type
        self.safe_id = title.lower().replace(" ", "_")

    def compose(self) -> ComposeResult:
        with Horizontal(classes="menu_row"):
            yield Label(self.icon, classes="menu_icon")
            with Vertical(classes="menu_text"):
                yield Label(self.title, classes="menu_title")
                yield Label(self.description, classes="menu_desc")
            if self.widget_type == "switch":
                yield Switch(id=f"sw_{self.safe_id}")
            else:
                yield Button("EJECUTAR", id=f"btn_{self.safe_id}")

class MainMenuScreen(Screen):
    # CSS Totalmente Hardcoded para evitar errores de referencia en el ZTE
    CSS = """
    #menu_container { margin: 1 1; height: 1fr; border: tall #00FF00; }
    #menu_title_main { width: 100%; text-align: center; text-style: bold; padding: 1; background: #111111; color: #BB00FF; }
    MenuOption { height: 5; margin: 0 1; border-bottom: solid #333333; background: #050505; }
    .menu_row { align: center middle; width: 100%; height: 100%; }
    .menu_icon { width: 6; margin-left: 1; }
    .menu_text { width: 1fr; margin-left: 1; }
    .menu_title { text-style: bold; color: #00FF00; }
    .menu_desc { text-style: italic; color: #AAAAAA; }
    Button { min-width: 14; height: 3; margin-right: 1; background: #00FF00; color: #000000; border: none; }
    Switch { dock: right; margin-right: 2; }
    """

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        with Vertical(id="menu_container"):
            yield Label(" [ MATRIZ DE INFRAESTRUCTURA ] ", id="menu_title_main")
            with ListView(id="main_menu_list"):
                yield MenuOption("🧟", "PROTOCOLO LAZARO", "Recuperar botín desde GitHub", "button")
                yield MenuOption("🔄", "AUTO SYNC", "Respaldo automático al salir", "switch")
                yield MenuOption("🧹", "JANITOR PROTOCOL", "Limpieza de logs y temporales", "button")
                yield MenuOption("💀", "PURGA TOTAL", "Eliminar datos locales sensibles", "button")
        yield Footer()

