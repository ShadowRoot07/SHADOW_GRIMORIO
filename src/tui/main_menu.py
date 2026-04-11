from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import ListItem, ListView, Label, Footer, Switch, Button
from textual.containers import Horizontal, Vertical
from src.tui.widgets import TelemetryBar
from src.tui.ritual import ShadowRitualModal

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
                yield Button("EJECUTAR" if not self.locked else "BLOQUEADO", 
                             id=f"btn_{self.safe_id}", 
                             variant="primary" if not self.locked else "error",
                             disabled=self.locked)

class MainMenuScreen(Screen):
    authenticated = False

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        with Vertical(id="menu_container"):
            yield Label(" [ MATRIZ DE INFRAESTRUCTURA ] ", id="menu_title_main")
            with ListView(id="main_menu_list"):
                # Solo el Ritual está disponible al inicio si no está autenticado
                yield MenuOption("🔓", "INICIAR RITUAL", "Validar llaves de acceso", "button")
                
                # Estas opciones estarán bloqueadas inicialmente
                yield MenuOption("🧟", "PROTOCOLO LAZARO", "Recuperar botín desde GitHub", "button", locked=not self.authenticated)
                yield MenuOption("🧹", "JANITOR PROTOCOL", "Limpieza de logs y temporales", "button", locked=not self.authenticated)
                yield MenuOption("💀", "PURGA TOTAL", "Eliminar datos locales sensibles", "button", locked=not self.authenticated)
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_iniciar_ritual":
            self.app.push_screen(ShadowRitualModal(), self.finalizar_ritual)

    def finalizar_ritual(self, resultado: bool) -> None:
        if resultado:
            self.authenticated = True
            self.refresh_menu()

    def refresh_menu(self):
        # Re-compone o actualiza los estados de los botones
        self.app.pop_screen()
        self.app.push_screen(MainMenuScreen())

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

