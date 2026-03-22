from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Switch, ListItem, ListView, Label, Static, Footer
from textual.containers import Container, Horizontal
from src.logic.agent_manager import manager
from src.tui.widgets import TelemetryBar

class AgentRow(ListItem):
    def __init__(self, agent_name: str, status: str):
        super().__init__()
        self.agent_name = agent_name
        self.initial_status = (status == "on")

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(f"📡 {self.agent_name.upper()}", id="name_label")
            yield Static(expand=True)
            # FIX: Quitamos la doble 'ff'
            yield Switch(value=self.initial_status, id=f"switch_{self.agent_name}")

class AgentsMenu(Screen):
    CSS = """
    AgentsMenu { background: #000800; }
    #menu_container { border: tall #00ff00; margin: 1 2; height: 1fr; }
    ListItem { height: 3; padding: 1 2; background: #001100; border-bottom: solid #003300; }
    #name_label { color: #00ffff; content-align: left middle; }
    """

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        with Container(id="menu_container") as c:
            c.border_title = "SALA DE AGENTES"
            # Importante: el ListView debe estar aquí
            yield ListView(id="agents_list")
        yield Footer()

    def on_mount(self) -> None:
        """Poblar la lista al entrar."""
        self.actualizar_lista()

    def actualizar_lista(self) -> None:
        try:
            lista = self.query_one("#agents_list", ListView)
            lista.clear() # Limpiar antes de llenar
            
            agentes = manager.listar_agentes()
            if not agentes:
                # Si no hay agentes, mostrar un aviso
                self.notify("No se detectaron glifos de agentes.", severity="warning")
                return

            for name, status in agentes.items():
                lista.append(AgentRow(name, status))
        except Exception as e:
            self.notify(f"Error al cargar enjambre: {e}", severity="error")

    def on_switch_changed(self, event: Switch.Changed) -> None:
        agent_name = event.switch.id.replace("switch_", "")
        if event.value:
            manager.encender_agente(agent_name)
        else:
            manager.apagar_agente(agent_name)

    def action_quit(self) -> None:
        self.app.pop_screen()

