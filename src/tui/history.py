from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, OptionList, Label, Static
from textual.containers import Container, Vertical
from textual.binding import Binding
from src.database.manager import db
from src.database.models import Proyecto, HitoHistorial
import json

class HistoryScreen(Screen):
    """Explorador de la Memoria Akáshica del Grimorio."""
    
    BINDINGS = [
        Binding("escape", "app.pop_screen", "Volver"),
        Binding("enter", "seleccionar_entidad", "Seleccionar"),
    ]

    def __init__(self):
        super().__init__()
        self.proyecto_seleccionado = None
        self.fase = "PROYECTOS" # PROYECTOS o COMMITS

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(id="history_main"):
            yield Label("[ HISTORIAL DE CONSTRUCCIÓN ]", id="hist_title")
            yield Label("Selecciona un proyecto para ver su línea de tiempo:", id="hist_subtitle")
            yield OptionList(id="hist_list")
            yield Static("", id="commit_preview")
        yield Footer()

    def on_mount(self) -> None:
        self.cargar_proyectos()

    def cargar_proyectos(self):
        self.fase = "PROYECTOS"
        list_widget = self.query_one("#hist_list")
        list_widget.clear_options()
        
        try:
            session = db.get_session()
            proyectos = session.query(Proyecto).all()

            proyectos.sort(key=lambda x: getattr(x, 'last_sync', 0) or 0, reverse=True)
            for p in proyectos:
                # Usar getattr para evitar errores si la columna falta físicamente
                rama = getattr(p, 'rama_actual', 'main')
                list_widget.add_option(f"📁 {p.nombre} [dim]({rama})[/]")
        except Exception as e:
            from loguru import logger
            logger.error(f"Fallo al cargar historial: {e}")
            list_widget.add_option("❌ Error al cargar base de datos")

    def cargar_commits(self, proyecto_id):
        self.fase = "COMMITS"
        list_widget = self.query_one("#hist_list")
        list_widget.clear_options()
        
        session = db.get_session()
        hitos = session.query(HitoHistorial).filter_by(proyecto_id=proyecto_id).order_by(HitoHistorial.fecha.desc()).all()
        
        list_widget.add_option("⬅ [ VOLVER A PROYECTOS ]")
        for h in hitos:
            fecha_fmt = h.fecha.strftime("%d/%m %H:%M")
            list_widget.add_option(f"⚓ {h.commit_hash[:7]} | {h.mensaje_commit[:30]}... [{fecha_fmt}]")
        
        self.hitos_data = hitos
        session.close()

    def action_seleccionar_entidad(self):
        list_widget = self.query_one("#hist_list")
        index = list_widget.highlighted
        
        if self.fase == "PROYECTOS":
            self.proyecto_seleccionado = self.proyectos_ids[index]
            self.cargar_commits(self.proyecto_seleccionado)
        else:
            if index == 0:
                self.cargar_proyectos()
            else:
                # El hito real es index - 1 por la opción de "Volver"
                hito = self.hitos_data[index - 1]
                self.restaurar_contexto_y_abrir_chat(hito)

    def restaurar_contexto_y_abrir_chat(self, hito):
        """Inyecta el contexto en el Oráculo y salta al Chat."""
        from src.tui.chat import ChatScreen
        
        # 1. Preparar el paquete de datos
        contexto_paquete = {
            "commit": hito.commit_hash,
            "prompt_previo": hito.prompt_usuario,
            "respuesta_previa": hito.respuesta_ia,
            "metadata": json.loads(hito.contexto_tecnico) if hito.contexto_tecnico else {}
        }
        
        # 2. Abrir el chat pasándole el estado
        # Nota: Necesitaremos modificar el ChatScreen para aceptar este argumento
        self.app.push_screen(ChatScreen(estado_restaurado=contexto_paquete))

