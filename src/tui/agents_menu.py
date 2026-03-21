from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Switch, ListItem, ListView, Label, Static
from textual.containers import Container, Horizontal
from src.logic.agent_manager import manager
from loguru import logger

class AgentRow(ListItem):
    """Una fila que representa a un agente con su interruptor."""
    def __init__(self, agent_name: str, status: str):
        super().__init__()
        self.agent_name = agent_name
        self.initial_status = (status == "on")

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(f"📡 AGENTE: {self.agent_name.upper()}", id="name_label")
            yield Static(expand=True) # Espaciador
            yield Switch(value=self.initial_status, id=f"switch_{self.agent_name}")

class AgentsMenu(Screen):
    """Consola Maestra para el encendido/apagado de Agentes."""

    CSS = """
    AgentsMenu {
        background: #000800;
    }
    #menu_container {
        border: tall #00ff00 "SALA DE CONTROL DE AGENTES";
        margin: 2 4;
        padding: 1;
        background: #000500;
    }
    ListItem {
        height: 3;
        padding: 1 2;
        background: #001100;
        border-bottom: thin #003300;
    }
    #name_label {
        color: #00ffff;
        content-align: left middle;
    }
    Switch {
        margin-left: 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="menu_container"):
            yield Label("[ SELECCIONA UN AGENTE PARA ALTERAR SU ESTADO ]", id="hint")
            self.list_view = ListView(id="agents_list")
            yield self.list_view
        yield Footer()

    def on_mount(self) -> None:
        """Puebla la lista con los agentes detectados por el Manager."""
        agentes = manager.listar_agentes()
        for name, status in agentes.items():
            self.list_view.append(AgentRow(name, status))

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Maneja el encendido/apagado real desde el UI."""
        agent_name = event.switch.id.replace("switch_", "")
        
        if event.value: # Si el switch está ON
            exito = manager.encender_agente(agent_name)
            logger.info(f"UI: Intentando despertar a {agent_name}...")
        else: # Si el switch está OFF
            exito = manager.apagar_agente(agent_name)
            logger.info(f"UI: Durmiendo a {agent_name}...")

    def action_quit(self) -> None:
        self.app.pop_screen()

