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
    #chat_container { padding: 1; height: 1fr; border: double #00FF00; }
    #console_log {
        background: #000;
        border: solid #111;
        height: 1fr;
        width: 100%;           /* Forzar ancho completo */
        color: #00FF00;
        scrollbar-gutter: stable;
        overflow-x: hidden;    /* Bloquear el scroll horizontal */
    }
    #chat_progress {
        width: 100%;
        height: 1;
        background: #1a1a1a;
        display: none;
        margin: 1 0; /* Espaciado para que no se pegue */
    }
    #chat_progress > .progress--bar {
        background: #220033;
        color: #BB00FF;
    }
    #input_container {
        height: auto;
        min-height: 3;
        /* Quitamos max-height fijo aquí para calcularlo en el método */
        margin-top: 1;
        border: tall #BB00FF;
        background: #0a0a0a;
    }

    #chat_input {
        height: 1fr; /* Ocupa todo el contenedor dinámico */
        border: none;
        background: transparent;
    }

    #btn_send {
        min-width: 8;
        height: 3;
        border: none;
        background: #BB00FF;
        color: white;
        margin-left: 1;
    }

    #typing_buffer {
        width: 100%;
        min-height: 1; /* Garantiza que ocupe al menos una línea */
        color: #BB00FF;
        background: #050505;
        padding: 0 1;
        text-style: italic;
    }
    """

    def __init__(self, contexto_inicial=None, **kwargs):
        super().__init__(**kwargs)
        self.contexto_inicial = contexto_inicial

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="chat_container"):
            yield Label("[ORÁCULO V3.0]", id="chat_header")
            yield RichLog(id="console_log", wrap=True)
            
            # ESTA ES LA CLAVE: El buffer de animación
            yield Static("", id="typing_buffer") 
            
            yield ProgressBar(id="chat_progress", total=100, show_eta=False)
            
            with Horizontal(id="input_container"):
                yield TextArea(id="chat_input", soft_wrap=True)
                yield Button("SEND", id="btn_send")
        yield Footer()

    def on_mount(self) -> None:
        self.raiz = Path(__file__).resolve().parents[2]
        self.console = self.query_one("#console_log")
        self.chat_input = self.query_one("#chat_input")

        self.console.write("[bold purple]NEXO ESTABLECIDO.[/] Oráculo sincronizado.")
        
        # --- NUEVA LÓGICA DE DETECCIÓN DE AGENTES ---
        self.reportar_agentes_activos()
        
        self.chat_input.focus()

        if self.contexto_inicial:
            h = self.contexto_inicial
            self.console.write(f"\n[bold yellow]⌛ CRONOLOGÍA RESTAURADA:[/]")
            self.console.write(f"[dim]Commit: {h['commit']}[/]")
            self.console.write(f"[cyan]Anteriormente:[/]\nU: {h['prompt_previo'][:50]}...")
            self.console.write(f"O: {h['respuesta_previa'][:50]}...")
            
            # Inyectamos en el historial real del chat para que Spica lo use
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

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        """Ajusta la altura dinámicamente limitándola al 50% de la pantalla."""
        # 1. Calcular altura necesaria basada en líneas de texto
        lines = event.text_area.text.count("\n") + 1
        
        # 2. Calcular el límite: 50% de la altura total de la terminal
        # self.size.height nos da la altura actual de la pantalla
        max_allowed = max(5, self.size.height // 2)
        
        # 3. Calcular nueva altura entre el mínimo (3) y el máximo dinámico
        new_height = max(3, min(lines + 1, max_allowed))
        
        # Aplicar altura al contenedor
        self.query_one("#input_container").styles.height = new_height

        # 4. BUG FIX: Forzar visibilidad del cursor
        # Usamos call_after_refresh para asegurar que el TextArea ya se renderizó 
        # con el nuevo tamaño antes de intentar scrollear al cursor.
        self.call_after_refresh(event.text_area.scroll_cursor_visible)

    async def on_key(self, event: events.Key) -> None:
        """Captura atajos de teclado para el Oráculo."""
        # Enviar con Ctrl+S o Enter simple
        if event.key in ("ctrl+s", "enter"):
            await self.action_enviar_mensaje()
            event.stop()
            event.prevent_default()
        
        # Permitir saltos de línea con Shift+Enter (si la terminal lo soporta)
        # o simplemente no hacer nada especial, permitiendo que TextArea maneje otros casos.

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_send":
            await self.action_enviar_mensaje()

    async def action_enviar_mensaje(self) -> None:
        text = self.chat_input.text.strip()
        if not text: return

        self.console.write(f"\n[bold cyan]ShadowRoot07:[/] {text}")
        self.console.scroll_end()

        # Reset total del widget
        self.chat_input.text = ""
        self.chat_input.cursor_location = (0, 0)
        
        # Forzar el reset de la altura al mínimo
        self.query_one("#input_container").styles.height = 3
        
        # Asegurar que el TextArea se entere del cambio de scroll interno
        self.chat_input.scroll_to(0, 0)

        if text.startswith("/"):
            await self.procesar_comando(text[1:])
        else:
            await self.consultar_oraculo(text)

    async def tipear_respuesta(self, texto: str):
        buffer_widget = self.query_one("#typing_buffer")
        # Aseguramos que la barra sea visible antes de empezar
        self.progress.styles.display = "block"
        
        prefix = "Oráculo: "
        current_text = ""
        
        # Si el texto es gigante, aumentamos la velocidad
        delay = 0.03 if len(texto) < 200 else 0.01

        for i, letra in enumerate(texto):
            current_text += letra
            # Usamos .update() pero controlando el refresco
            buffer_widget.update(f"[bold purple]{prefix}[/]{current_text}")

            progreso = 50 + int((i / len(texto)) * 50)
            self.progress.update(progress=progreso)

            # Pausas inteligentes
            if letra == ".": await asyncio.sleep(0.3)
            elif letra in (",", ":"): await asyncio.sleep(0.1)
            else: await asyncio.sleep(delay)

        # Traspaso final al historial
        self.console.write(f"[bold purple]Oráculo:[/] {texto}")
        buffer_widget.update("") 
        self.console.scroll_end()

    async def consultar_oraculo(self, query: str):
        self.progress = self.query_one("#chat_progress")
        self.progress.styles.display = "block"
        self.refresh()
        self.progress.update(progress=10) # 50% mientras "piensa"
        
        self.console.write("[italic yellow]El Oráculo procesando...[/]")
        
        try:
            contexto_reciente = "\n".join(self.historial_chat[-6:])
            prompt_final = f"Historial reciente:\n{contexto_reciente}\n\nUsuario: {query}"

            for p in range(10, 51, 5):
                self.progress.update(progress=p)
                await asyncio.sleep(0.05)

            # Llamada real al API
            respuesta = await oraculo.consultar(query)
            
            # Ejecutamos el tipeo
            await self.tipear_respuesta(respuesta)

            
            # Salto de línea estético después del tipeo
            self.console.write("") 

            # --- CONEXIÓN CON ARCHITECT CORE ---
            from src.logic.architect_core import architect
            plan = architect.planificar(respuesta)
            if plan:
                self.console.write("[dim]Plan de acción detectado. Ejecutando cambios...[/]")
                resultado = architect.procesar_instruccion(respuesta)
                if resultado["status"] == "success":
                    from src.logic.agents.chronicler import ChroniclerAgent
                    self.console.write("[bold green]💾 Sincronizando memoria...[/]")
                    cronista = ChroniclerAgent()
                    h_hash = cronista.registrar_hito(query, respuesta, plan)
                    self.console.write(f"[dim]Hito registrado: [cyan]{h_hash[:7]}[/][/]")
                else:
                    self.console.write(f"[red]⚠ Fallo en construcción:[/] {resultado['message']}")

            self.historial_chat.append(f"Usuario: {query}")
            self.historial_chat.append(f"Oráculo: {respuesta}")

        except Exception as e:
            self.console.write(f"\n[red]Error de enlace cognitivo:[/] {e}")
        
        finally:
            # Esperamos un poco para que el usuario vea la barra al 100%
            self.progress.update(progress=100)
            await asyncio.sleep(1.0)
            self.progress.styles.display = "none"
            self.console.write("")
            self.console.scroll_end()


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


