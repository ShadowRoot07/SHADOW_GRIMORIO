from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, TextArea, ProgressBar, RadioSet, RadioButton, Static
from textual.containers import Vertical, Center
from src.logic.trials_v2_manager import trials_v2_logic
import time

class TrialScreenV2(Screen):
    """Interfaz de Alta Seguridad para la Fase 2."""

    def __init__(self):
        super().__init__()
        self.fase_actual = 1 # 1: Cifrado, 2: Secretos, 3: Cuestionario
        self.sub_step = 1
        self.preguntas_fase3 = trials_v2_logic.obtener_preguntas_aleatorias(3)
        self.current_q_index = 0
        self.tiempo_restante = 30

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="trial_box_v2"):
                yield Label("⚡ PROTOCOLO SAP: FASE 2", id="title_v2")
                yield Label("", id="instructions")
                
                # Input para Fases 1 y 2
                yield TextArea(id="input_area_v2", show_line_numbers=True)
                
                # Cuestionario Fase 3 (Oculto al inicio)
                with Vertical(id="quiz_box", classes="hidden"):
                    yield Label("", id="question_text")
                    with RadioSet(id="options_set"):
                        yield RadioButton("", id="opt_A")
                        yield RadioButton("", id="opt_B")
                        yield RadioButton("", id="opt_C")
                        yield RadioButton("", id="opt_D")
                    yield Label("SINCRONÍA DE INTEGRIDAD", id="timer_label")
                    yield ProgressBar(total=30, show_percentage=False, id="timer_bar")
                
                yield Button("PROCESAR", variant="primary", id="btn_action")

    def on_mount(self):
        self.timer_bar = self.query_one("#timer_bar")
        self.timer_bar.styles.bar_foreground = "#FF0000" # Barra Roja
        self.preparar_fase_1()

    def preparar_fase_1(self):
        self.reto = trials_v2_logic.generar_reto_cifrado()
        desc = f"PRUEBA 1/3 (Cifrado)\nReto {self.sub_step}/3: Descifra usando [bold cyan]{self.reto['tipo']}[/]\nCadena: [yellow]{self.reto['target']}[/]"
        self.query_one("#instructions").update(desc)

    def preparar_fase_2(self):
        secretos = ["BASE_DE_DATOS_URL", "GROQ_API_TOKEN", "GITHUB_TOKEN"]
        nombre_actual = secretos[self.sub_step - 1]
        desc = f"PRUEBA 2/3 (Secretos)\nInyecta el valor para: [bold magenta]{nombre_actual}[/]"
        self.query_one("#instructions").update(desc)
        self.query_one("#input_area_v2").text = ""

    def preparar_fase_3(self):
        self.query_one("#input_area_v2").add_class("hidden")
        self.query_one("#quiz_box").remove_class("hidden")
        self.mostrar_pregunta()

    def mostrar_pregunta(self):
        q = self.preguntas_fase3[self.current_q_index]
        self.query_one("#question_text").update(f"CUESTIONARIO {self.current_q_index+1}/3:\n{q['q']}")
        # Actualizar RadioButtons...
        self.tiempo_restante = 30
        self.timer_bar.progress = 30
        self.set_timer(1.0, self.tick)

    def tick(self):
        if self.fase_actual == 3 and self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            self.timer_bar.progress = self.tiempo_restante
            self.set_timer(1.0, self.tick)
        elif self.tiempo_restante == 0:
            self.app.notify("TIEMPO AGOTADO. REINICIANDO FASE 3.", severity="error")
            self.current_q_index = 0
            self.mostrar_pregunta()

    def on_button_pressed(self, event: Button.Pressed):
        if self.fase_actual == 1:
            if self.query_one("#input_area_v2").text.strip() == self.reto['solucion']:
                if self.sub_step < 3:
                    self.sub_step += 1
                    self.preparar_fase_1()
                else:
                    self.fase_actual = 2
                    self.sub_step = 1
                    self.preparar_fase_2()
            else:
                self.app.notify("Error de descifrado.", severity="error")

    CSS = """
    #trial_box_v2 { width: 90%; border: double #8A2BE2; padding: 1; background: #050505; }
    #title_v2 { text-align: center; color: #8A2BE2; text-style: bold; }
    .hidden { display: none; }
    #timer_bar { margin-top: 1; }
    #timer_label { text-align: center; color: red; font-size: 80%; }
    """

