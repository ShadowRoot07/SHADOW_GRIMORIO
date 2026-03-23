from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Switch, ListItem, ListView, Label, Footer
from textual.containers import Horizontal, Vertical
from src.logic.agent_manager import manager
from src.tui.widgets import TelemetryBar

class AgentRow(ListItem):
    """Fila de agente optimizada para visibilidad en ZTE."""
    def __init__(self, agent_name: str, status: str):
        super().__init__()
        self.agent_name = agent_name
        self.is_on = (status == "on")

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Label(f" 📡 {self.agent_name.upper()}", classes="name_tag")
            # ID generado correctamente como f-string
            yield Switch(value=self.is_on, id=f"sw_{self.agent_name}")

class AgentsMenu(Screen):
    # CSS Refinado: Se eliminaron ambigüedades en align y se usaron variables de tema
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
        background: $surface;
        text-style: bold;
    }
    AgentRow {
        height: 3;
        margin: 0 1;
        border-bottom: solid $secondary;
        background: $surface;
    }
    AgentRow > Horizontal {
        align: center middle;
        width: 100%;
        height: 100%;
    }
    .name_tag {
        width: 1fr;
        color: $accent;
        text-style: bold;
        margin-left: 1;
    }
    Switch {
        dock: right;
        margin-right: 1;
    }
    """

    def on_mount(self) -> None:
        """Sincroniza el fondo con el tema actual al entrar."""
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
        """Puebla la lista basándose en el sistema de archivos real."""
        try:
            lista = self.query_one("#agents_list", ListView)
            lista.clear()
            
            manager.descubrir_agentes()
            agentes = manager.listar_agentes()

            if not agentes:
                self.notify("Matriz vacía: Sin scripts en /agents", severity="error")
                return

            for name, status in agentes.items():
                lista.append(AgentRow(name, status))
        except Exception as e:
            self.notify(f"Error de escaneo: {e}", severity="error")

    def on_switch_changed(self, event: Switch.Changed) -> None:
        """Controlador de energía con prevención de bucles."""
        # Evitamos procesar IDs que no nos pertenecen
        if not event.switch.id or not event.switch.id.startswith("sw_"):
            return

        agent_name = event.switch.id.replace("sw_", "")
        
        if event.value:
            # Intentar encender
            exito = manager.encender_agente(agent_name)
            if exito:
                self.notify(f"AGENTE {agent_name} ONLINE", title="SISTEMA")
            else:
                self.notify(f"FALLO AL DESPERTAR {agent_name}", severity="error")
                # Bloqueamos el evento para evitar recursión al resetear
                event.stop()
                event.switch.value = False 
        else:
            # Intentar apagar
            if manager.apagar_agente(agent_name):
                self.notify(f"AGENTE {agent_name} EN SLEEP", title="SISTEMA")

    def action_quit(self) -> None:
        """Vuelve a la pantalla principal."""
        self.app.pop_screen()

