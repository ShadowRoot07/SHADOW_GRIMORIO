from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import ListItem, ListView, Label, Footer, Switch, Button
from textual.containers import Horizontal, Vertical
from src.tui.widgets import TelemetryBar
import asyncio

class MenuOption(ListItem):
    """Fila genérica para el Dashboard de Matriz con IDs normalizados."""
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
    """Dashboard de Control de Infraestructura (Letra M)."""

    # CSS corregido: Eliminadas propiedades 'font-size' y 'opacity'
    CSS = """
    #menu_container {
        margin: 1 1;
        height: 1fr;
    }
    #menu_title_main {
        width: 100%;
        text-align: center;
        text-style: bold italic;
        padding: 1;
    }
    MenuOption {
        height: 5;
        margin: 0 1;
    }
    .menu_row { align: center middle; width: 100%; height: 100%; }
    .menu_icon { width: 6; margin-left: 1; }
    .menu_text { width: 1fr; margin-left: 1; }
    .menu_title { text-style: bold; }
    .menu_desc { text-style: italic; }

    Button { min-width: 14; height: 3; margin-right: 1; border: none; }
    Switch { dock: right; margin-right: 2; }
    """

    def on_mount(self) -> None:
        """Sincronización con el sistema de temas."""
        t = self.app.tema
        self.styles.background = t['bg']

        # Estilo del contenedor principal
        cont = self.query_one("#menu_container")
        cont.styles.border = ("tall", t['primary'])

        # Estilo del título
        titulo = self.query_one("#menu_title_main")
        titulo.styles.color = t['accent']
        titulo.styles.background = t['surface']

        # Aplicar colores dinámicos a las filas
        for row in self.query(MenuOption):
            row.styles.background = t['surface']
            row.styles.border_bottom = ("solid", t['secondary'])
            row.query_one(".menu_title").styles.color = t['primary']
            row.query_one(".menu_desc").styles.color = t['text']
            
            try:
                btn = row.query_one(Button)
                btn.styles.background = t['primary']
                btn.styles.color = t['bg']
            except:
                pass

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

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id

        if btn_id == "btn_protocolo_lazaro":
            self.notify("🧟 Iniciando resurrección...")
            try:
                from src.logic.lazaro_protocol import lazaro
                await lazaro.ejecutar()
                self.notify("✅ Proceso Lázaro finalizado.")
            except Exception as e:
                self.notify(f"❌ Error en Lázaro: {e}", severity="error")

        elif btn_id == "btn_janitor_protocol":
            self.notify("🧹 Consultando al conserje...")
            try:
                from src.logic.janitor import janitor
                resumen = await janitor.ejecutar_limpieza_profunda()
                self.notify(f"✨ {resumen}", title="LIMPIEZA")
            except Exception as e:
                self.notify(f"❌ Error Janitor: {e}", severity="error")

        elif btn_id == "btn_purga_total":
            self.notify("⚠️ Usa la CLI: python shadow purge", severity="error")

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if event.switch.id == "sw_auto_sync":
            estado = "ACTIVO" if event.value else "INACTIVO"
            self.notify(f"Auto-Sync: {estado}", title="MATRIZ")

    def action_quit(self) -> None:
        self.app.pop_screen()

