import json
from datetime import datetime
from loguru import logger
from sqlalchemy.orm import Session

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, OptionList, Label, Static
from textual.containers import Container
from textual.binding import Binding

from src.database.manager import db
from src.database.models import Proyecto, HitoHistorial

class HistoryScreen(Screen):
    """Explorador asíncrono y de alta fidelidad para el Historial del Grimorio."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Volver"),
        Binding("enter", "seleccionar_entidad", "Seleccionar / Ejecutar"),
    ]

    CSS = """
    #history_main {
        padding: 1;
        background: #050505;
    }
    #hist_title {
        color: #00FF00;
        text-style: bold;
        background: #00FF00 15%;
        width: 100%;
        content-align: center middle;
        padding: 1;
        margin-bottom: 1;
        border: solid #00FF00;
    }
    #hist_subtitle {
        color: #BB00FF;
        margin-bottom: 1;
        text-style: italic;
    }
    #hist_list {
        background: #000800 30%;
        border: tall #BB00FF;
        height: 1fr;
    }
    #commit_preview {
        background: #0a0a0a;
        color: #e0e0e0;
        border: dashed #00FF00 50%;
        height: 8;
        margin-top: 1;
        padding: 1;
    }
    """

    def __init__(self):
        super().__init__()
        self.proyecto_seleccionado = None
        self.fase = "PROYECTOS"  # Estados estables: PROYECTOS | COMMITS
        self.proyectos_ids = []  # Caché de IDs para mapear índices visuales
        self.hitos_data = []     # Contenedor en memoria de los hitos cargados

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Container(id="history_main"):
            yield Label(" ⚡ NÚCLEO DE MEMORIA CRONOLÓGICA ⚡ ", id="hist_title")
            yield Label("Cargando registros del tejido local...", id="hist_subtitle")
            yield OptionList(id="hist_list")
            yield Static("[ Panel de Datos: Esperando selección... ]", id="commit_preview")
        yield Footer()

    def on_mount(self) -> None:
        """Punto de entrada: Sincroniza la UI e inicia la carga asíncrona."""
        self.cargar_proyectos()

    def cargar_proyectos(self) -> None:
        """Lee de forma segura los proyectos activos registrados."""
        self.fase = "PROYECTOS"
        self.proyecto_seleccionado = None
        self.proyectos_ids.clear()
        
        subtitle = self.query_one("#hist_subtitle")
        subtitle.update("Selecciona un proyecto para inspeccionar sus hitos operativos:")
        
        list_widget = self.query_one("#hist_list")
        list_widget.clear_options()

        # Usar un worker asíncrono evita lags en procesadores móviles
        def _bg_load():
            session: Session = db.get_session()
            try:
                proyectos = session.query(Proyecto).all()
                # Ordenar por última sincronización de forma segura
                proyectos.sort(key=lambda x: getattr(x, 'last_sync', None) or datetime.min, reverse=True)
                
                if not proyectos:
                    self.app.call_from_thread(list_widget.add_option, "⚠️ No hay proyectos en el Grimorio")
                    return

                for p in proyectos:
                    self.proyectos_ids.append(p.id)
                    rama = getattr(p, 'rama_actual', 'master')
                    fmt_option = f"📁 {p.nombre} [dim]({rama})[/]"
                    self.app.call_from_thread(list_widget.add_option, fmt_option)
            except Exception as e:
                logger.error(f"Error al leer proyectos en base de datos: {e}")
                self.app.call_from_thread(list_widget.add_option, "❌ Error crítico al leer la Bóveda")
            finally:
                session.close()

        self.run_worker(_bg_load, thread=True, name="load_projects_task")

    def cargar_commits(self, proyecto_id: int) -> None:
        """Carga y despliega la línea de tiempo de un proyecto específico."""
        self.fase = "COMMITS"
        self.hitos_data.clear()
        
        subtitle = self.query_one("#hist_subtitle")
        subtitle.update("Línea de tiempo del proyecto activo. Selecciona para restaurar contexto:")
        
        list_widget = self.query_one("#hist_list")
        list_widget.clear_options()
        
        list_widget.add_option("⬅️ [ VOLVER A LA LISTA DE PROYECTOS ]")

        def _bg_load_commits():
            session: Session = db.get_session()
            try:
                hitos = session.query(HitoHistorial).filter_by(proyecto_id=proyecto_id).order_by(HitoHistorial.fecha.desc()).all()
                
                if not hitos:
                    self.app.call_from_thread(list_widget.add_option, "⚠️ Este proyecto no tiene hitos construidos.")
                    return

                for h in hitos:
                    # Guardamos una copia en diccionario para evitar errores de sesión cerrada
                    self.hitos_data.append({
                        "id": h.id,
                        "commit_hash": h.commit_hash,
                        "mensaje_commit": h.mensaje_commit or "Neural Link Sync",
                        "prompt_usuario": h.prompt_usuario,
                        "respuesta_ia": h.respuesta_ia,
                        "contexto_tecnico": h.contexto_tecnico
                    })
                    
                    fecha_str = h.fecha.strftime("%d/%m %H:%M") if h.fecha else "??/??"
                    msg_corto = h.mensaje_commit[:35] if h.mensaje_commit else "Sin mensaje"
                    list_widget.add_option(f"⚓ {h.commit_hash[:7]} | {msg_corto}... [bold magenta][{fecha_str}][/]")
                    
            except Exception as e:
                logger.error(f"Error al extraer hitos del proyecto {proyecto_id}: {e}")
                self.app.call_from_thread(list_widget.add_option, "❌ Error al mapear la línea de tiempo")
            finally:
                session.close()

        self.run_worker(_bg_load_commits, thread=True, name="load_commits_task")


    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Actualiza el panel inferior de previsualización en tiempo real al navegar."""
        preview = self.query_one("#commit_preview")
        
        # CAMBIO CRÍTICO: Usar option_index en lugar de index
        index = event.option_index

        if self.fase == "PROYECTOS" or index == 0:
            preview.update("[ Selecciona una opción para desplegar metadatos ]")
            return

        # Restamos 1 por el botón superior de regresar de la lista
        if self.hitos_data and (index - 1) < len(self.hitos_data):
            hito = self.hitos_data[index - 1]
            hash_fmt = f"[bold green]Commit:[/] {hito['commit_hash'][:7]}"
            msg_fmt = f"[bold purple]Msg:[/] {hito['mensaje_commit']}"
            prompt_fmt = f"[bold cyan]Prompt:[/] {hito['prompt_usuario'][:50]}..."
            preview.update(f"{hash_fmt} | {msg_fmt}\n{prompt_fmt}")

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Manejador nativo de selección interactiva (Al presionar Enter o Click)."""
        index = event.option_index

        if index is None or index == -1:
            return

        if self.fase == "PROYECTOS":
            if index < len(self.proyectos_ids):
                self.proyecto_seleccionado = self.proyectos_ids[index]
                self.cargar_commits(self.proyecto_seleccionado)
        else:
            if index == 0:
                self.cargar_proyectos()
            else:
                actual_index = index - 1
                if actual_index < len(self.hitos_data):
                    hito_dict = self.hitos_data[actual_index]
                    self.restaurar_contexto_y_abrir_chat(hito_dict)

    def restaurar_contexto_y_abrir_chat(self, hito_info: dict) -> None:
        """Encapsula los datos cronológicos y abre el Nexo de Chat de forma nativa."""
        from src.tui.chat import ChatScreen

        # Empaquetamos mapeando los nombres correctos esperados por ChatScreen
        contexto_paquete = {
            "commit": hito_info["commit_hash"],
            "prompt_previo": hito_info["prompt_usuario"],
            "respuesta_previa": hito_info["respuesta_ia"],
            "metadata": json.loads(hito_info["contexto_tecnico"]) if hito_info["contexto_tecnico"] else {}
        }

        # Cambiado a 'contexto_inicial' para emparejar perfectamente con el constructor de chat.py
        self.app.push_screen(ChatScreen(contexto_inicial=contexto_paquete))

