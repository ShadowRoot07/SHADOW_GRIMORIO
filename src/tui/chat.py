import asyncio
from pathlib import Path
from textual import events
from textual.screen import Screen
from textual.widgets import TextArea, RichLog, Header, Footer, Label, Button, ProgressBar, Static
from textual.containers import Container, Horizontal
from textual.app import ComposeResult

# Importamos el cliente de Groq existente
from src.api.groq_client import oraculo

class ChatScreen(Screen):
    """El Oráculo: Inteligencia Operativa Conversacional con UX Mejorada."""

    historial_chat = []

    CSS = """
    ChatScreen { background: #050505; }
    
    #chat_container { 
        padding: 1; 
        height: 1fr; 
        border: double #00FF00; 
        background: #000800 5%;
    }
    
    #chat_header {
        width: 100%;
        content-align: center middle;
        background: #00FF00 15%;
        color: #00FF00;
        text-style: bold;
        /* Cambiado: 'line' no existe, usamos 'solid' */
        border-bottom: solid #00FF00;
        margin-bottom: 1;
    }

    #console_log {
        background: #000;
        border: none;
        height: 1fr;
        color: #00FF00;
        scrollbar-gutter: stable;
    }

    #typing_buffer {
        width: 100%;
        min-height: 1;
        color: #BB00FF;
        background: #0a0a0a;
        padding: 0 1;
        text-style: italic;
        border-left: solid #BB00FF;
    }

    #chat_progress {
        width: 100%;
        height: 1;
        background: #1a1a1a;
        display: none;
        margin: 0;
    }

    #chat_progress > .progress--bar {
        background: #220033;
        color: #BB00FF;
    }

    #input_container {
        height: 3;
        margin-top: 1;
        border: tall #BB00FF;
        background: #0a0a0a;
        padding: 0 1;
    }

    #chat_input {
        height: 1fr;
        border: none;
        background: transparent;
        color: #e0e0e0;
    }

    #btn_send {
        min-width: 8;
        background: #BB00FF 20%;
        color: #BB00FF;
        /* Cambiado: 'outset' no existe, usamos 'heavy' o 'solid' */
        border: solid #BB00FF;
        text-style: bold;
    }
    
    #btn_send:hover {
        background: #BB00FF;
        color: white;
    }

    .cmd_hint {
        /* Cambiado: Eliminado font-size que no existe en Textual */
        color: #00FF00 50%;
        text-align: center;
    }
    #typing_overlay {
        width: 100%;
        height: auto;
        min-height: 1;
        background: #0a0a0a;
        color: #BB00FF;
        /* Cambiado: 'socket' no existe, usamos 'hkey' para un look ciberpunk */
        border-top: hkey #BB00FF; 
        padding: 0 1;
        display: none; 
        text-style: italic;
    }

    """


    def __init__(self, contexto_inicial=None, **kwargs):
        super().__init__(**kwargs)
        self.contexto_inicial = contexto_inicial

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="chat_container"):
            yield Label(" ⚡ ORÁCULO OPERATIVO V3.0-SHADOW ⚡ ", id="chat_header")
            
            yield RichLog(id="console_log", wrap=True, markup=True)

            # Buffer de animación (El pulso del Oráculo)
            yield Static("", id="typing_buffer")

            yield ProgressBar(id="chat_progress", total=100, show_eta=False)
            yield Static("", id="typing_overlay")

            with Horizontal(id="input_container"):
                yield TextArea(
                        placeholder="Inyectar comando... (Ctrl+S == Enter)",
                    id="chat_input", 
                    soft_wrap=True
                )
                yield Button("SEND", id="btn_send")

            yield Label("Sistemas: /scan | /sync | /map | /clear", classes="cmd_hint")
        yield Footer()

    def on_mount(self) -> None:
        self.raiz = Path(__file__).resolve().parents[2]
        # Referencias rápidas
        self.console = self.query_one("#console_log")
        self.chat_input = self.query_one("#chat_input")
        self.progress = self.query_one("#chat_progress")
        self.buffer = self.query_one("#typing_buffer")

        self.console.write("[bold purple]NEXO ESTABLECIDO.[/] Oráculo sincronizado.")
        
        # Reporte de agentes al iniciar
        self.reportar_agentes_activos()
        
        self.chat_input.focus()

        # Restaurar contexto si existe
        if self.contexto_inicial:
            self.restaurar_contexto(self.contexto_inicial)

    def restaurar_contexto(self, h):
        """Método auxiliar para limpiar el on_mount."""
        self.console.write(f"\n[bold yellow]⌛ CRONOLOGÍA RESTAURADA:[/]")
        self.console.write(f"[dim]Commit: {h['commit']}[/]")
        self.historial_chat.append(f"Usuario: {h['prompt_previo']}")
        self.historial_chat.append(f"Oráculo: {h['respuesta_previa']}")

    def reportar_agentes_activos(self) -> None:
        """Escanea y reporta agentes que ya estaban corriendo en las sombras."""
        from src.logic.agent_manager import manager
        agentes = manager.listar_agentes() # Devuelve {'nombre': 'on'/'off'}
        activos = [nombre for nombre, status in agentes.items() if status == "on"]

        if activos:
            lista_fmt = ", ".join([f"[bold green]{a}[/]" for a in activos])
            self.console.write(f"[yellow]⚠ ALERTA DE SOMBRAS:[/] Detectados procesos activos: {lista_fmt}")
            self.console.write("[dim]Usa /stop [nombre] para liberar recursos si es necesario.[/]")
        else:
            self.console.write("[dim]No hay agentes externos operando actualmente.[/]")



    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_send":
            await self.action_enviar_mensaje()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Ajuste de altura inteligente: 
        Crece con el código, pero respeta el espacio del Oráculo.
        """
        # Contar líneas reales
        lines = event.text_area.text.count("\n") + 1
        
        # El límite es el 40% de la pantalla para no ahogar el RichLog
        max_h = max(3, self.size.height // 2.5)
        new_height = int(max(3, min(lines + 1, max_h)))

        # Aplicar el cambio al contenedor con suavidad
        container = self.query_one("#input_container")
        container.styles.height = new_height
        
        # Mantener el cursor siempre a la vista
        self.call_after_refresh(event.text_area.scroll_cursor_visible)

    async def on_key(self, event: events.Key) -> None:
        """Atajos de teclado optimizados para ShadowRoot."""
        if event.key == "ctrl+s":
            await self.action_enviar_mensaje()
            event.stop()
        
        # Enter simple envía, Shift+Enter para nueva línea
        elif event.key == "enter":
            await self.action_enviar_mensaje()
            event.stop()
            event.prevent_default()

    async def action_enviar_mensaje(self) -> None:
        """Flujo de salida de datos: Limpieza y envío."""
        text = self.chat_input.text.strip()
        if not text:
            return

        # Limpiar interfaz antes de procesar
        self.chat_input.text = ""
        self.chat_input.cursor_location = (0, 0)
        self.query_one("#input_container").styles.height = 3
        
        # Iniciar consulta
        await self.consultar_oraculo(text)

    def on_descendant_focus(self, event: events.DescendantFocus) -> None:
        """Efecto visual cuando el input está activo."""
        if event.widget.id == "chat_input":
            self.query_one("#input_container").styles.border = ("tall", "#00FF00")
            
    def on_descendant_blur(self, event: events.DescendantBlur) -> None:
        """Efecto visual cuando el input pierde el foco."""
        if event.widget.id == "chat_input":
            self.query_one("#input_container").styles.border = ("tall", "#BB00FF")


    async def tipear_respuesta(self, texto: str):
        overlay = self.query_one("#typing_overlay")
        overlay.styles.display = "block"
        
        prefix = "[bold purple]Oráculo:[/] "
        acumulado = ""
        
        # En móviles, si el delay es muy bajo, el sistema lo ignora. 
        # 0.06s es el "punto dulce" para que el ZTE renderice letra por letra.
        for i, letra in enumerate(texto):
            acumulado += letra
            
            # Actualización del widget
            overlay.update(f"{prefix}{acumulado}█")
            
            # Forzar actualización de la barra
            progreso = 50 + int((i / len(texto)) * 50)
            self.progress.update(progress=progreso)

            # ESTO ES CLAVE: Obligamos al motor a procesar la UI antes de seguir
            await asyncio.sleep(0.06) 
            
            # Cada 2 letras, pedimos un refresco de pantalla explícito
            if i % 2 == 0:
                self.app.refresh()

        # Al terminar, esperamos un suspiro y movemos al log
        await asyncio.sleep(0.2)
        self.console.write(f"{prefix}{texto}")
        overlay.update("")
        overlay.styles.display = "none"
        self.console.scroll_end()

    async def consultar_oraculo(self, query: str):
        self.progress = self.query_one("#chat_progress")
        self.progress.styles.display = "block"
        self.progress.update(progress=10)
        
        self.console.write(f"\n[bold cyan]ShadowRoot07:[/] {query}")
        self.app.refresh() # Pintamos el prompt del usuario primero

        try:
            # Mientras Groq responde, hacemos que la barra se mueva
            # Esto confirma si el renderizado está vivo
            for p in range(15, 45, 5):
                self.progress.update(progress=p)
                await asyncio.sleep(0.05)
                self.app.refresh()

            respuesta = await oraculo.consultar(query)
            
            # Iniciamos el tipeo
            await self.tipear_respuesta(respuesta)

        except Exception as e:
            self.console.write(f"[bold red]⚠ ERROR:[/] {e}")
        finally:
            self.progress.update(progress=100)
            self.app.refresh()
            await asyncio.sleep(0.5)
            self.progress.styles.display = "none"

    async def procesar_comando(self, cmd_input: str):
        from src.logic.agent_manager import manager # Usar el manager oficial
        parts = cmd_input.lower().split()
        if not parts: return
        cmd = parts[0]

        # Mapeo de comandos a nombres de agentes en src/logic/agents/
        agentes = {
            "scan": "void_hunter",
            "clean": "janitor",
            "map": "explorer",
            "sync": "bruma_sync"
        }

        if cmd in agentes:
            nombre = agentes[cmd]
            self.console.write(f"[bold yellow]>>>[/] Despertando al Nodo: [bold]{nombre}[/]...")
            # El manager ahora se encarga de la asincronía y el log
            if manager.encender_agente(nombre):
                self.console.write(f"[dim]Nodo {nombre} operando en las sombras (Vía AgentManager).[/]")
            else:
                self.console.write(f"[red]Error:[/] No se pudo despertar al nodo {nombre}.")
        elif cmd == "clear":
            self.console.clear()
            self.historial_chat.clear()
            self.console.write("[dim]Buffer y memoria purgados.[/]")
            
        elif cmd == "stop":
            if len(parts) < 2:
                self.console.write("[red]Error:[/] Especifica el nombre del agente. Ej: /stop janitor")
                return
            
            nombre = parts[1]
            if manager.apagar_agente(nombre):
                self.console.write(f"[bold red]⚰[/] Agente [bold]{nombre}[/] neutralizado.")
            else:
                self.console.write(f"[red]Fallo:[/] El agente {nombre} no está activo o no existe.")
        
        elif cmd == "status":
            self.reportar_agentes_activos()

        elif cmd == "history" or cmd == "h":
            from src.logic.agents.chronicler import ChroniclerAgent
            c = ChroniclerAgent()
            arbol = c.obtener_arbol_visual()
            self.console.write("\n[bold cyan]--- LÍNEA DE TIEMPO DEL PROYECTO ---[/]")
            self.console.write(f"[green]{arbol}[/]")

        else:
            self.console.write(f"[red]Error:[/] '{cmd}' no reconocido.")

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


