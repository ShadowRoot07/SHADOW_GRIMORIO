import asyncio
from pathlib import Path
from textual.screen import Screen
from textual.widgets import Input, RichLog, Header, Footer, Label
from textual.containers import Container
from textual.app import ComposeResult

class ChatScreen(Screen):
    """El Oráculo: Centro de Comando e Inteligencia Operativa."""

    CSS = """
    ChatScreen { background: #050505; }
    #chat_container { padding: 1; height: 1fr; border: double #00FF00; }
    #console_log {
        background: #000;
        border: solid #111;
        height: 1fr;
        color: #00FF00;
        scrollbar-gutter: stable;
    }
    #chat_input { border: tall #BB00FF; background: #0a0a0a; margin-top: 1; }
    .cmd_hint { color: #555; margin-left: 2; font-size: 80%; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="chat_container"):
            yield Label("[SISTEMA OPERATIVO DE SOMBRAS - ORÁCULO V1.1]", id="chat_header")
            yield RichLog(id="console_log", highlight=True, markup=True)
            yield Input(placeholder="Escribe al Oráculo o usa /comando...", id="chat_input")
            yield Label("Comandos: /scan | /clean | /map | /sync | /clear", classes="cmd_hint")
        yield Footer()

    def on_mount(self) -> None:
        self.raiz = Path(__file__).resolve().parents[2]
        self.log = self.query_one("#console_log")
        self.log.write("[bold purple]NEXO ESTABLECIDO.[/] Oráculo escuchando en el puerto del ZTE...")
        self.query_one("#chat_input").focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text: return

        self.log.write(f"\n[bold cyan]ShadowRoot07:[/] {text}")
        self.query_one("#chat_input").value = ""

        if text.startswith("/"):
            await self.procesar_comando(text[1:])
        else:
            self.log.write("[italic yellow]El Oráculo analiza la semántica...[/]")
            # Simulación de respuesta asíncrona
            await asyncio.sleep(0.4)
            self.log.write("[bold purple]Oráculo:[/] Enlace cognitivo limitado. Usa comandos [green]/[/] para control directo.")

    async def ejecutar_agente_async(self, script_path: str, nombre_agente: str):
        """Ejecuta un script de agente sin bloquear el hilo principal."""
        full_path = self.raiz / script_path
        if not full_path.exists():
            self.log.write(f"[red]Error:[/] No existe: {script_path}")
            return

        self.log.write(f"[bold yellow]>>>[/] Desplegando [bold]{nombre_agente}[/]...")

        try:
            # Ejecución en background total
            await asyncio.create_subprocess_exec(
                "python", str(full_path),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            self.log.write(f"[dim]Agente {nombre_agente} operando en las sombras.[/]")
        except Exception as e:
            self.log.write(f"[red]Fallo crítico:[/] {e}")

    async def procesar_comando(self, cmd_input: str):
        """Manejador de comandos del sistema."""
        parts = cmd_input.lower().split()
        cmd = parts[0]

        if cmd == "scan":
            await self.ejecutar_agente_async("src/logic/agents/void_hunter.py", "Void_Hunter")
        elif cmd == "clean":
            await self.ejecutar_agente_async("src/logic/agents/janitor.py", "Janitor")
        elif cmd == "map":
            await self.ejecutar_agente_async("src/logic/agents/explorer.py", "Explorer")
        elif cmd == "sync":
            await self.ejecutar_agente_async("src/logic/agents/bruma_sync.py", "Bruma_Sync")
        elif cmd == "clear":
            self.log.clear()
            self.log.write("[dim]Buffer de consola purgado.[/]")
        else:
            self.log.write(f"[red]Error:[/] '{cmd}' no es un comando reconocido.")

