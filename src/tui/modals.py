from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static
from textual.containers import Grid, Vertical, ScrollableContainer

class ConfirmBuildModal(ModalScreen[bool]):
    """Ventana de confirmación para el Arquitecto."""

    def __init__(self, resumen: str):
        super().__init__()
        self.resumen = resumen

    def compose(self) -> ComposeResult:
        with Vertical(id="modal_container"):
            yield Label("🏗️ ESTRUCTURA DETECTADA", id="modal_title")
            yield Static(self.resumen, id="modal_body")
            with Grid(id="modal_buttons"):
                yield Button("MATERIALIZAR", variant="success", id="confirm")
                yield Button("ABORTAR", variant="error", id="cancel")

    def on_mount(self) -> None:
        t = self.app.tema
        container = self.query_one("#modal_container")
        container.styles.border = ("thick", t['primary'])
        container.styles.background = t['surface']
        self.query_one("#modal_title").styles.color = t['accent']

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            self.dismiss(True)
        else:
            self.dismiss(False)

    CSS = """
    #modal_container {
        width: 80%;
        height: auto;
        max-height: 20;
        align: center middle;
        padding: 1;
    }
    #modal_title { text-align: center; text-style: bold; margin-bottom: 1; }
    #modal_body { margin: 1 0; height: 1fr; border: solid #333; padding: 1; }
    #modal_buttons { grid-size: 2; grid-gutter: 2; height: 3; }
    """

class WatchdogErrorModal(ModalScreen):
    """Ventana de alerta roja para errores de sintaxis detectados por Watchdog."""

    def __init__(self, error_data: dict):
        super().__init__()
        self.error_data = error_data

    def compose(self) -> ComposeResult:
        file = self.error_data.get("file", "Desconocido")
        line = self.error_data.get("line", "?")
        error_msg = self.error_data.get("error", "Error de sintaxis no especificado.")

        with Vertical(id="watchdog_modal"):
            yield Label("⚠️ SINTAXIS DETECTADA ROTA", id="wd_title")
            yield Label(f"ARCHIVO: [bold white]{file}[/] | LÍNEA: [bold cyan]{line}[/]", id="wd_subtitle")
            
            with ScrollableContainer(id="wd_scroll"):
                yield Static(error_msg, id="wd_body")
            
            with Grid(id="wd_footer"):
                yield Button("ENTENDIDO (CERRAR)", variant="error", id="close_jn")

    def on_mount(self) -> None:
        container = self.query_one("#watchdog_modal")
        container.styles.border = ("thick", "#FF0000")
        container.styles.background = "#1a0000"
        self.query_one("#wd_title").styles.color = "#FF3131"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_close_watchdog": # ID más específico
            self.dismiss()


    CSS = """
    #watchdog_modal {
        width: 85%;
        height: 60%;
        align: center middle;
        padding: 1;
        border: thick #FF0000;
    }
    #wd_title { text-align: center; text-style: bold; margin-bottom: 0; }
    #wd_subtitle { text-align: center; background: #330000; margin: 1 0; padding: 0 1; }
    #wd_scroll { 
        height: 1fr; 
        border: solid #550000; 
        padding: 1; 
        background: #000;
        scrollbar-gutter: stable;
    }
    #wd_body { color: #FF9999; }
    #wd_footer { grid-size: 1; height: 3; margin-top: 1; }
    #btn_close_watchdog { width: 100%; border: none; background: #FF0000; }
    """


class JanitorAuditModal(ModalScreen):
    """Ventana púrpura neón que lista detalladamente los elementos eliminados."""

    def __init__(self, data: dict):
        super().__init__()
        self.data = data

    def compose(self) -> ComposeResult:
        files = self.data.get("files", [])
        count = self.data.get("count", 0)

        with Vertical(id="janitor_modal"):
            yield Label("🧹 HIGIENIZACIÓN COMPLETADA", id="jn_title")
            yield Label(f"SE HAN PURGADO [bold #BC13FE]{count}[/] ELEMENTOS", id="jn_subtitle")
            
            with ScrollableContainer(id="jn_scroll"):
                if files:
                    for f in files:
                        # Cada archivo con un prefijo de flecha neón
                        yield Label(f"[#BC13FE]»[/] {f}", classes="file_entry")
                else:
                    yield Label("No se detectaron archivos residuales.", id="empty_msg")

            with Grid(id="jn_footer"):
                yield Button("ENTENDIDO", variant="primary", id="close_jn")

    def on_mount(self) -> None:
        container = self.query_one("#janitor_modal")
        # Estética Neón Púrpura Profundo
        container.styles.border = ("thick", "#BC13FE")
        container.styles.background = "#0a000f"
        self.query_one("#jn_title").styles.color = "#E0B0FF"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close_jn":
            self.app.pop_screen()

    CSS = """
    #janitor_modal {
        width: 85%;
        height: 65%;
        align: center middle;
        padding: 1;
    }
    #jn_title { text-align: center; text-style: bold; margin-bottom: 0; }
    #jn_subtitle { 
        text-align: center; 
        background: #1a0025; 
        margin: 1 0; 
        padding: 0 1; 
        border-bottom: solid #BC13FE;
    }
    #jn_scroll {
        height: 1fr;
        border: solid #3c005a;
        padding: 1;
        background: #000;
        scrollbar-gutter: stable;
    }
    .file_entry {
        color: #D8BFD8;
        margin-bottom: 0;
        width: 100%;
    }
    #empty_msg { color: #555; text-align: center; margin-top: 2; }
    #jn_footer { grid-size: 1; height: 3; margin-top: 1; }
    #close_jn { 
        width: 100%; 
        background: #BC13FE; 
        color: white; 
        text-style: bold;
        border: none; 
    }
    """


class GhostWritingModal(ModalScreen):
    """Ventana Cian Neón para el flujo de escritura del Ghost_Coder."""

    def __init__(self, data: dict):
        super().__init__()
        self.data = data

    def compose(self) -> ComposeResult:
        msg = self.data.get("message", "PROCESANDO...")
        details = self.data.get("details", [])

        with Vertical(id="ghost_modal"):
            yield Label(f"👻 {msg}", id="gh_title")

            with ScrollableContainer(id="gh_scroll"):
                for d in details:
                    yield Label(f"[#00FFFF]>>[/] {d}", classes="gh_entry")

            with Grid(id="gh_footer"):
                yield Button("CERRAR NEXO", id="close_gh")

    def on_mount(self) -> None:
        container = self.query_one("#ghost_modal")
        container.styles.border = ("thick", "#00FFFF")
        container.styles.background = "#000a0a"
        self.query_one("#gh_title").styles.color = "#00FFFF"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Cierre explícito de la pantalla modal
        if event.button.id == "close_gh":
            self.dismiss() # dismiss() es preferible para modales en Textual

    CSS = """
    #ghost_modal { width: 85%; height: 60%; align: center middle; padding: 1; }
    #gh_title { text-align: center; text-style: bold; margin-bottom: 1; }
    #gh_scroll { height: 1fr; border: solid #005555; background: #000; padding: 1; }
    .gh_entry { color: #AAFFFF; margin-bottom: 0; }
    #gh_footer { grid-size: 1; height: 3; margin-top: 1; }
    #close_gh { width: 100%; background: #005555; color: white; border: none; }
    """



class BrumaSyncModal(ModalScreen):
    """Ventana Gris/Blanco Neblina para el flujo de respaldo de Bruma_Sync."""

    def __init__(self, data: dict):
        super().__init__()
        self.data = data

    def compose(self) -> ComposeResult:
        msg = self.data.get("message", "SINCRONIZANDO...")
        details = self.data.get("details", [])

        with Vertical(id="bruma_modal"):
            yield Label(f"🌫️ {msg}", id="br_title")

            with ScrollableContainer(id="br_scroll"):
                for d in details:
                    yield Label(f"[#FFFFFF]»[/] {d}", classes="br_entry")

            with Grid(id="br_footer"):
                yield Button("CERRAR NEBLINA", id="close_br")

    def on_mount(self) -> None:
        container = self.query_one("#bruma_modal")
        # Estética Vapor/Gris
        container.styles.border = ("thick", "#E5E4E2")
        container.styles.background = "#121212"
        self.query_one("#br_title").styles.color = "#FFFFFF"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close_br":
            self.dismiss()

    CSS = """
    #bruma_modal { width: 85%; height: 50%; align: center middle; padding: 1; }
    #br_title { text-align: center; text-style: bold; margin-bottom: 1; }
    #br_scroll { height: 1fr; border: solid #444; background: #000; padding: 1; }
    .br_entry { color: #CCCCCC; margin-bottom: 0; }
    #br_footer { grid-size: 1; height: 3; margin-top: 1; }
    #close_br { width: 100%; background: #444; color: white; border: none; }
    """



class ExplorerModal(ModalScreen):
    """Ventana Amarilla/Dorado para visualizar el mapa del proyecto."""

    def __init__(self, data: dict):
        super().__init__()
        self.data = data

    def compose(self) -> ComposeResult:
        tree = self.data.get("tree", [])
        total = self.data.get("total_files", 0)

        with Vertical(id="explorer_modal"):
            yield Label("🧭 CARTOGRAFÍA DEL GRIMORIO", id="ex_title")
            yield Label(f"ELEMENTOS RASTREADOS: [bold]{total}[/]", id="ex_subtitle")

            with ScrollableContainer(id="ex_scroll"):
                for line in tree:
                    # Aplicamos color dorado a los conectores ASCII
                    clean_line = line.replace("├──", "[#FFD700]├──[/]").replace("└──", "[#FFD700]└──[/]").replace("│", "[#FFD700]│[/]")
                    yield Label(clean_line, classes="tree_line")

            with Grid(id="ex_footer"):
                yield Button("CERRAR MAPA", id="close_ex")

    def on_mount(self) -> None:
        container = self.query_one("#explorer_modal")
        container.styles.border = ("thick", "#FFD700") # Dorado
        container.styles.background = "#0f0f00" # Fondo oscuro con tinte amarillento
        self.query_one("#ex_title").styles.color = "#FFFF00" # Amarillo Neón

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close_ex":
            self.dismiss()

    CSS = """
    #explorer_modal { 
        width: 95%; 
        height: 90%; 
        align: center middle; 
        padding: 1; 
    }
    #ex_title { text-align: center; text-style: bold; margin-bottom: 0; }
    #ex_subtitle { text-align: center; background: #222200; margin: 1 0; padding: 0 1; }
    #ex_scroll { 
        height: 1fr; 
        border: double #555500; 
        background: #000; 
        padding: 1;
        scrollbar-gutter: stable;
    }
    /* Eliminamos white-space que causaba el crash */
    .tree_line { 
        color: #FFFACD; 
        text-style: bold; 
        width: auto;
    }
    #ex_footer { grid-size: 1; height: 3; margin-top: 1; }
    #close_ex { width: 100%; background: #555500; color: white; border: none; }
    """


class VoidHunterModal(ModalScreen):
    def __init__(self, data: dict):
        super().__init__()
        self.data = data

    def compose(self) -> ComposeResult:
        findings = self.data.get("findings", [])
        
        with Vertical(id="void_modal"):
            yield Label("🌌 DIAGNÓSTICO DEL VACÍO", id="vd_title")
            
            with ScrollableContainer(id="vd_scroll"):
                if findings:
                    for f in findings:
                        with Vertical(classes="finding_card"):
                            yield Label(f"[b]ARCHIVO:[/b] [#00BFFF]{f['file']}[/]")
                            yield Label(f"[b]FALLO:[/b] [#FF9999]{f['issue']}[/]")
                            yield Label(f"[b]FIX:[/b] [#99FF99]{f['fix']}[/]")
                            yield Label("─" * 20, classes="separator")
                else:
                    yield Label("El Grimorio está optimizado. Sin vacíos.", id="vd_empty")

            with Grid(id="vd_footer"):
                yield Button("ENTENDIDO", id="btn_close_void") # Agregado ID explícito

    def on_mount(self) -> None:
        c = self.query_one("#void_modal")
        c.styles.border = ("thick", "#0047AB")
        c.styles.background = "#00050a"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_close_void":
            self.dismiss()

    CSS = """
    #void_modal { width: 90%; height: 80%; align: center middle; padding: 1; }
    #vd_title { text-align: center; text-style: bold; color: #00BFFF; margin-bottom: 1; }
    #vd_scroll { height: 1fr; border: solid #0047AB; background: #000; padding: 1; }
    .finding_card { margin-bottom: 1; padding: 0 1; }
    .separator { color: #002244; margin: 0; }
    #vd_footer { grid-size: 1; height: 3; margin-top: 1; }
    #btn_close_void { width: 100%; background: #0047AB; color: white; border: none; }
    """

