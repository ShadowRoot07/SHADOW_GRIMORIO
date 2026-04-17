from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, TextArea
from textual.containers import Vertical, Center
from src.logic.trials_v2_manager import trials_v2_logic

class TrialScreenV2(Screen):
    """Pantalla de bloqueo para la Fase 2: Descifrado e Inyección de Secretos."""

    def __init__(self):
        super().__init__()
        self.sub_step = 1
        self.fase_interna = 1  # 1: Cifrado, 2: Secretos
        self.reto = None

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="trial_box_v2"):
                yield Label("⚡ PROTOCOLO SAP: FASE 2", id="title_v2")
                yield Label("", id="status_line")
                yield Label("", id="instructions")
                yield TextArea(id="input_v2")
                yield Button("PROCESAR", variant="primary", id="btn_next")

    def on_mount(self):
        self.preparar_fase()

    def preparar_fase(self):
        inst = self.query_one("#instructions")
        input_area = self.query_one("#input_v2")
        status = self.query_one("#status_line")

        if self.fase_interna == 1:
            self.reto = trials_v2_logic.generar_reto_cifrado()
            msg = f"DESCIFRADO ({self.sub_step}/3)\nAlgoritmo: [cyan]{self.reto['tipo']}[/]\nCadena: [yellow]{self.reto['target']}[/]"
            inst.update(msg)
            status.update("[#666666]Sincronizando llaves de cifrado...[/]")
        else:
            secretos = ["BASE_DE_DATOS_URL", "GROQ_TOKEN", "GITHUB_TOKEN"]
            msg = f"INYECCIÓN ({self.sub_step}/3)\nConfigurando: [magenta]{secretos[self.sub_step-1]}[/]"
            inst.update(msg)
            input_area.text = ""
            status.update("[#666666]Escribiendo en la Bóveda de Sombras...[/]")

    def on_button_pressed(self, event: Button.Pressed):
        if self.fase_interna == 1:
            val = self.query_one("#input_v2").text.strip()
            if val == self.reto['solucion']:
                if self.sub_step < 3:
                    self.sub_step += 1
                else:
                    self.fase_interna = 2
                    self.sub_step = 1
                self.preparar_fase()
            else:
                self.app.notify("Error de descifrado.", severity="error")
        else:
            val = self.query_one("#input_v2").text.strip()
            secretos = ["BASE_DE_DATOS_URL", "GROQ_TOKEN", "GITHUB_TOKEN"]
            if trials_v2_logic.inyectar_secreto(secretos[self.sub_step-1], val):
                if self.sub_step < 3:
                    self.sub_step += 1
                    self.preparar_fase()
                else:
                    self.app.notify("Fase 2 Sellada. Iniciando Evaluación Técnica...", severity="success")
                    from src.tui.trial_screen_v3 import TrialScreenV3
                    self.app.push_screen(TrialScreenV3())
            else:
                self.app.notify("Fallo en la persistencia de la bóveda.", severity="error")

    CSS = """
    #trial_box_v2 {
        width: 95%;
        height: auto;
        border: double #8A2BE2;
        padding: 1;
        background: #050505;
    }
    #title_v2 {
        text-align: center;
        color: #8A2BE2;
        text-style: bold;
    }
    #status_line {
        text-align: center;
        margin-bottom: 1;
        height: 1;
        color: #666666;
    }
    #instructions {
        margin-bottom: 1;
        text-align: center;
        height: 4;
    }
    #input_v2 {
        height: 5;
        border: solid #333;
        background: #000;
        color: #8A2BE2;
    }
    #btn_next {
        width: 100%;
        margin-top: 1;
        background: #8A2BE2;
    }
    """

