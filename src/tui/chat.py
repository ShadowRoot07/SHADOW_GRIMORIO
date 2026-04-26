import asyncio
from pathlib import Path
from textual.screen import Screen
from textual.widgets import Input, RichLog, Header, Footer, Label
from textual.containers import Container
from textual.app import ComposeResult

# Importamos el cliente de Groq existente
from src.api.groq_client import oraculo

class ChatScreen(Screen):
    """El Oráculo: Inteligencia Operativa Conversacional."""

    # Memoria de la sesión actual para dar continuidad al chat
    historial_chat = []

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
    .cmd_hint { color: #555; margin-left: 2; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="chat_container"):
            yield Label("[SISTEMA OPERATIVO DE SOMBRAS - ORÁCULO V1.2]", id="chat_header")
            yield RichLog(id="console_log", highlight=True, markup=True)
            yield Input(placeholder="Habla con el Oráculo o usa /comando...", id="chat_input")
            yield Label("Comandos: /scan | /clean | /map | /sync | /clear", classes="cmd_hint")
        yield Footer()

    def on_mount(self) -> None:
        self.raiz = Path(__file__).resolve().parents[2]
        self.console = self.query_one("#console_log")
        self.console.write("[bold purple]NEXO ESTABLECIDO.[/] Oráculo sincronizado.")
        self.query_one("#chat_input").focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text: return

        # Mostrar el mensaje del usuario
        self.console.write(f"\n[bold cyan]ShadowRoot07:[/] {text}")
        self.query_one("#chat_input").value = ""

        if text.startswith("/"):
            await self.procesar_comando(text[1:])
        else:
            # FLUJO CONVERSACIONAL (Error lógico corregido)
            await self.consultar_oraculo(text)

    async def consultar_oraculo(self, query: str):
        """Envía la consulta a Groq integrando el historial local."""
        self.console.write("[italic yellow]El Oráculo procesando...[/]")
        
        try:
            # Construimos un mini-contexto con los últimos 3 mensajes para no saturar el prompt
            # Historial reciente:
            contexto_reciente = "\n".join(self.historial_chat[-6:])
            prompt_final = f"Historial reciente:\n{contexto_reciente}\n\nUsuario: {query}"

            # Llamada al cliente (sin tocar groq_client.py)
            # Usamos run_in_executor si la llamada fuera bloqueante, pero consultar es async.
            respuesta = await oraculo.consultar(prompt_final)
            
            # Limpiar el aviso de "procesando" y escribir respuesta
            self.console.write(f"[bold purple]Oráculo:[/] {respuesta}")
            
            # Guardar en la memoria de la sesión
            self.historial_chat.append(f"Usuario: {query}")
            self.historial_chat.append(f"Oráculo: {respuesta}")
            
        except Exception as e:
            self.console.write(f"[red]Error de enlace cognitivo:[/] {e}")

    async def ejecutar_agente_async(self, script_path: str, nombre_agente: str):
        full_path = self.raiz / script_path
        if not full_path.exists():
            self.console.write(f"[red]Error:[/] No existe: {script_path}")
            return

        self.console.write(f"[bold yellow]>>>[/] Desplegando [bold]{nombre_agente}[/]...")

        try:
            await asyncio.create_subprocess_exec(
                "python", str(full_path),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            self.console.write(f"[dim]Agente {nombre_agente} operando en las sombras.[/]")
        except Exception as e:
            self.console.write(f"[red]Fallo crítico:[/] {e}")

    async def procesar_comando(self, cmd_input: str):
        parts = cmd_input.lower().split()
        if not parts: return
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
            self.console.clear()
            self.historial_chat.clear() # Limpiamos memoria también
            self.console.write("[dim]Buffer y memoria purgados.[/]")
        else:
            self.console.write(f"[red]Error:[/] '{cmd}' no reconocido.")

