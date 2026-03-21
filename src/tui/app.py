from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Label
from textual.containers import Center, Middle
from src.utils.ascii_loader import ASCIILoader
from src.logic.init_profile import ProfileManager
from src.tui.init_wizard import InitWizard
from src.utils.hardware_bridge import hw  # <--- IMPORTAMOS EL PUENTE DE C++
import asyncio

class SplashScreen(Static):
    """Widget para la animación de entrada (Calavera)."""
    def on_mount(self) -> None:
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
        if ProfileManager.es_primera_vez():
            self.push_screen(InitWizard())
        else:
            await self.animacion_inicio()

    async def animacion_inicio(self) -> None:
        """Secuencia de arranque usando datos REALES del hardware."""
        status = self.query_one("#status")

        await asyncio.sleep(1.0)
        status.update("[bold cyan]ESCANEANDO HARDWARE NATIVO...[/bold cyan]")
        
        # INVOCACIÓN AL NÚCLEO C++
        specs = hw.obtener_specs()
        await asyncio.sleep(1.2)
        
        if specs['status'] == "online":
            status.update(f"[bold green]DETECTADO: {specs['ram_mb']}MB RAM | {specs['cores']} NÚCLEOS[/bold green]")
        else:
            status.update("[bold red]ERROR: NÚCLEO NATIVO FUERA DE LÍNEA[/bold red]")

        await asyncio.sleep(1.5)
        status.update("[bold green]VÍNCULO ESTABLECIDO: ShadowRoot07[/bold green]")

        await asyncio.sleep(1.0)
        status.update("[green]SISTEMA LISTO PARA OPERAR.[/green]")
        # Aquí es donde podrías hacer: self.push_screen(ChatScreen())

if __name__ == "__main__":
    app = ShadowGrimorio()
    app.run()

