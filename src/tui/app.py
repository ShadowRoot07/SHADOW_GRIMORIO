from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Label
from textual.containers import Center, Middle
from src.utils.ascii_loader import ASCIILoader
from src.logic.init_profile import ProfileManager
from src.tui.init_wizard import InitWizard
from src.tui.agents_menu import AgentsMenu
from src.utils.hardware_bridge import hw
import asyncio

class SplashScreen(Static):
    def on_mount(self) -> None:
        self.update(f"[bold green]{ASCIILoader.get_art('splash')}[/bold green]")

class ShadowGrimorio(App):
    """Orquestador persistente."""
    CSS = """
    Screen { background: #000800; align: center middle; }
    #status { margin-top: 1; text-align: center; width: 100%; }
    """

    BINDINGS = [
        ("q", "quit", "Desconectar TUI"), # Solo cierra la interfaz
        ("g", "agentes", "Gestionar Agentes"),
        ("a", "ajustes", "Ajustes")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Middle():
                yield SplashScreen(id="logo")
                yield Label("[ INICIALIZANDO PROTOCOLO... ]", id="status")
        yield Footer()

    async def on_mount(self) -> None:
        if ProfileManager.es_primera_vez():
            self.push_screen(InitWizard())
        else:
            await self.animacion_inicio()

    async def animacion_inicio(self) -> None:
        status = self.query_one("#status")
        await asyncio.sleep(0.5)
        specs = hw.obtener_specs()
        status.update(f"[bold green]NÚCLEO ONLINE: {specs['cores']} CORES ACTIVOS[/bold green]")
        await asyncio.sleep(0.5)
        status.update("[bold cyan]TUI LISTA. LOS AGENTES OPERAN EN LAS SOMBRAS.[/bold cyan]")

    def action_agentes(self) -> None:
        self.push_screen(AgentsMenu())

    def action_quit(self) -> None:
        """Cierra la interfaz pero no mata a los agentes daemonizados."""
        self.exit()

if __name__ == "__main__":
    app = ShadowGrimorio()
    app.run()

