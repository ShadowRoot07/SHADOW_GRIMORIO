import asyncio
from pathlib import Path
from textual import events
from textual.screen import Screen
from textual.widgets import TextArea, RichLog, Header, Footer, Label, Button, ProgressBar, Static
from textual.containers import Container, Horizontal, ScrollableContainer
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
        height: 6;
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
        /* Altura fija para que el scroll funcione correctamente */
        height: 10; 
        background: #0a0a0a;
        color: #BB00FF;
        border-top: hkey #BB00FF;
        border-bottom: hkey #BB00FF;
        padding: 0 1;
        display: none;
        text-style: italic;
        /* Forzamos que sea un contenedor con scroll */
        overflow-y: scroll;
        scrollbar-gutter: stable;
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

            # Buffer de animación (Este ya lo tenías, lo dejamos quieto)
            yield Static("", id="typing_buffer")

            yield ProgressBar(id="chat_progress", total=100, show_eta=False)
            
            # EL CONTENEDOR DE SCROLL (Único con este ID)
            with ScrollableContainer(id="typing_overlay"):
                yield Static("", id="typing_buffer_internal")

            with Horizontal(id="input_container"):
                yield TextArea(
                    placeholder="Inyectar comando... (Ctrl+S == SEND)",
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


    def tipear_respuesta(self, texto: str) -> None:
        """
        Animación optimizada para ShadowRoot: 
        Usa un contenedor con scroll dedicado.
        """
        async def _animar():
            # El contenedor padre que tiene el scroll
            container = self.query_one("#typing_overlay")
            # El static interno donde inyectamos el texto
            internal_static = self.query_one("#typing_buffer_internal")
            
            container.styles.display = "block"
            prefix = "[bold purple]Oráculo:[/] "
            acumulado = ""

            for i, letra in enumerate(texto):
                acumulado += letra
                contenido_seguro = f"{prefix}{escape(acumulado)}█"
                internal_static.update(contenido_seguro)

                progreso = 50 + int((i / len(texto)) * 50)
                self.progress.update(progress=progreso)

                # Forzamos el scroll al final del CONTENEDOR
                container.scroll_end(animate=False)

                # Ajuste de delay para el ZTE
                delay = 0.04 if len(texto) < 500 else 0.01 
                
                await asyncio.sleep(delay)

                # Refresco visual cada 3 caracteres
                if i % 3 == 0:
                    self.app.refresh()

            await asyncio.sleep(0.2)
            self.console.write(f"{prefix}{escape(texto)}")
            
            # Limpieza
            internal_static.update("")
            container.styles.display = "none"
            self.progress.styles.display = "none"
            self.console.scroll_end()

        self.run_worker(_animar(), thread=True)

    async def consultar_oraculo(self, query: str):
        self.progress = self.query_one("#chat_progress")
        self.progress.styles.display = "block"
        self.progress.update(progress=10)
        
        self.console.write(f"\n[bold cyan]ShadowRoot07:[/] {query}")

        try:
            # Fase de pensamiento (Barra moviéndose)
            for p in range(15, 46, 10):
                self.progress.update(progress=p)
                await asyncio.sleep(0.05)

            # Llamada al API
            respuesta = await oraculo.consultar(query, agente_id="SPICA")
            # DISPARAR ANIMACIÓN (Sin await para que el worker tome el control)
            self.tipear_respuesta(respuesta)

            # --- LÓGICA DE CONSTRUCCIÓN (MOTOR) ---
            def ejecutar_construccion():
                from src.logic.architect_core import architect
                
                # MODIFICACIÓN AQUÍ: Pasamos el cwd_usuario de la app
                resultado = architect.procesar_instruccion(
                    respuesta, 
                    cwd_usuario=self.app.cwd_usuario
                )

                if resultado.get("status") == "success":
                    detalles = "\n".join(resultado.get("details", []))
                    self.app.call_from_thread(
                        self.console.write, f"[bold green]🏗️ ARCHITECT:[/] Despliegue exitoso en {self.app.cwd_usuario}:\n{detalles}"
                    )
                elif resultado.get("status") == "error" and "No se detectó estructura JSON" not in resultado["message"]:
                    self.app.call_from_thread(
                        self.console.write, f"[bold red]🚨 ARCHITECT ERROR:[/] {resultado['message']}"
                    )

            # Ejecutamos el motor en un hilo separado para no congelar la TUI
            self.run_worker(ejecutar_construccion, thread=True)

            # Creamos un worker para no bloquear la UI mientras escribimos en DB/Neon
            def guardar_en_db():
                from src.database.manager import db
                from src.database.models import HitoHistorial, Proyecto, Conocimiento
                from datetime import datetime
                import subprocess
                from loguru import logger

                # 1. ABRIR SESIÓN AL INICIO
                session = db.get_session()
                
                try:
                    # 2. LÓGICA DE MEMORIA PERSONAL (CONOCIMIENTO)
                    q_lower = query.lower()
                    if "recuerda que" in q_lower or "guarda que" in q_lower:
                        try:
                            # Extraemos lo que viene después de "que"
                            hecho = query.split("que", 1)[1].strip()
                            
                            nuevo_conocimiento = Conocimiento(
                                categoria="MEMORIA",
                                llave=f"recuerdo_{datetime.now().strftime('%H%M%S')}",
                                valor=hecho,
                                usuario_id=1 # ShadowRoot07
                            )
                            session.add(nuevo_conocimiento)
                            logger.success(f"🧠 SPICA: Hecho registrado: {hecho}")
                        except Exception as e:
                            logger.error(f"⚠️ Fallo al procesar recuerdo: {e}")

                    # 3. LÓGICA DE HITO (HISTORIAL DE CHAT)
                    try:
                        commit_hash = subprocess.check_output(
                            ["git", "rev-parse", "HEAD"],
                            cwd=str(self.raiz)
                        ).decode().strip()
                    except:
                        commit_hash = "unknown_shadow_pulse"

                    proyecto = session.query(Proyecto).filter_by(nombre="SHADOW_GRIMORIO").first()

                    nuevo_hito = HitoHistorial(
                        proyecto_id=proyecto.id if proyecto else None,
                        commit_hash=commit_hash,
                        prompt_usuario=query,
                        respuesta_ia=respuesta,
                        mensaje_commit="Neural Link Sync"
                    )
                    session.add(nuevo_hito)
                    
                    # 4. COMMIT ÚNICO PARA AMBOS
                    session.commit()
                    
                except Exception as db_e:
                    session.rollback()
                    logger.error(f"❌ Fallo crítico al persistir: {db_e}")
                finally:
                    session.close()

            self.run_worker(guardar_en_db, thread=True)


        except Exception as e:
            self.console.write(f"[bold red]⚠ ERROR DE ENLACE:[/] {e}")
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


