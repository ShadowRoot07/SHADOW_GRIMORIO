from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Label
from textual.containers import Center, Middle
from src.utils.ascii_loader import ASCIILoader
from src.logic.init_profile import ProfileManager
from src.tui.init_wizard import InitWizard
import asyncio

class SplashScreen(Static):
    """Widget para la animación de entrada (Calavera)."""
    def on_mount(self) -> None:
        # Cargamos tu calavera desde assets
        self.update(f"[bold green]{ASCIILoader.get_art('splash')}[/bold green]")

class ShadowGrimorio(App):
    """El Orquestador Híbrido: SHADOW_GRIMORIO v1.0"""

    CSS = """
    Screen {
        background: #000800;
        align: center middle;
    }
    #logo {
        color: #00ff00;
    }
    #status {
        margin-top: 1;
        text-align: center;
        width: 100%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Desconectar"), 
        ("r", "ritual", "Nuevo Ritual"),
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
        """Punto de entrada lógico del sistema."""
        if ProfileManager.es_primera_vez():
            # Si no hay usuario, lanzamos el Wizard sobre la pantalla actual
            self.push_screen(InitWizard())
        else:
            # Si ya existe, procedemos con la estética de carga
            await self.animacion_inicio()

    async def animacion_inicio(self) -> None:
        """Secuencia estética de arranque."""
        status = self.query_one("#status")
        
        await asyncio.sleep(1.5)
        status.update("[bold cyan]ESCANEANDO HARDWARE...[/bold cyan]")
        
        await asyncio.sleep(1)
        # Aquí es donde el alias viene de la DB real
        status.update("[bold green]VÍNCULO ESTABLECIDO: ShadowRoot07[/bold green]")
        
        await asyncio.sleep(1)
        status.update("[green]SISTEMA LISTO PARA OPERAR.[/green]")
        # Aquí podrías hacer un push_screen hacia la consola principal de chat

if __name__ == "__main__":
    app = ShadowGrimorio()
    app.run()

