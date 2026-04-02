from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Switch, ListItem, ListView, Label, Footer
from textual.containers import Horizontal, Vertical
from src.logic.agent_manager import manager
from src.tui.widgets import TelemetryBar

class AgentRow(ListItem):
    def __init__(self, agent_name: str, status: str):
        super().__init__()
        self.agent_name = agent_name
        self.is_on = (status == "on")

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(f" 📡 {self.agent_name.upper()}", classes="name_tag")
            yield Switch(value=self.is_on, id=f"sw_{self.agent_name}")

class AgentsMenu(Screen):
    # CSS Obligatorio para que no se vea desordenado en el ZTE
    CSS = """
    #menu_container {
        border: tall $primary;
        margin: 1 1;
        height: 1fr;
    }
    #title {
        width: 100%;
        text-align: center;
        color: $accent;
        padding: 1;
    }
    AgentRow {
        height: 3;
        border-bottom: solid $secondary;
    }
    .name_tag {
        width: 1fr;
        margin-top: 1;
        margin-left: 1;
    }
    Switch {
        margin-right: 1;
    }
    """

    BINDINGS = [
        ("escape", "app.pop_screen", "Volver"),
        ("q", "quit", "Salir")
    ]

    def on_mount(self) -> None:
        t = self.app.tema
        self.styles.background = t['bg']
        self.actualizar_lista()

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        with Vertical(id="menu_container"):
            yield Label(" [ ENJAMBRE DE AGENTES ]", id="title")
            yield ListView(id="agents_list")
        yield Footer()

    def actualizar_lista(self) -> None:
        try:
            lista = self.query_one("#agents_list", ListView)
            lista.clear()
            manager.descubrir_agentes()
            agentes = manager.listar_agentes()
            for name, status in agentes.items():
                lista.append(AgentRow(name, status))
        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    def on_switch_changed(self, event: Switch.Changed) -> None:
        if not event.switch.id or not event.switch.id.startswith("sw_"):
            return
        agent_name = event.switch.id.replace("sw_", "")
        if event.value:
            if not manager.encender_agente(agent_name):
                event.switch.value = False
            else:
                self.notify(f"AGENTE {agent_name} ONLINE")
        else:
            manager.apagar_agente(agent_name)
            self.notify(f"AGENTE {agent_name} EN SLEEP")

