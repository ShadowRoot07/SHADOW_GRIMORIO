from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, TextArea, ProgressBar, RadioSet, RadioButton
from textual.containers import Vertical, Center
from src.logic.trials_v2_manager import trials_v2_logic

class TrialScreenV2(Screen):
    """Pantalla de bloqueo para la Fase 2: Producción (Sin Debug)."""

    def __init__(self):
        super().__init__()
        self.fase = 1  # 1: Cifrado, 2: Secretos, 3: Quiz Técnico
        self.sub_step = 1
        self.tiempo = 30
        # Ahora el manager debe devolver preguntas de programación pura
        self.preguntas = trials_v2_logic.obtener_preguntas_aleatorias(3)
        self.q_idx = 0
        self.reto = None

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="trial_box_v2"):
                yield Label("⚡ PROTOCOLO SAP: FASE 2", id="title_v2")
                # Label de estado (limpio de soluciones)
                yield Label("[ ESTADO: SISTEMA CIFRADO ]", id="status_line")
                yield Label("", id="instructions")

                yield TextArea(id="input_v2")

                with Vertical(id="quiz_box", classes="hidden"):
                    yield Label("", id="q_text")
                    with RadioSet(id="options"):
                        yield RadioButton("", id="opt_a")
                        yield RadioButton("", id="opt_b")
                        yield RadioButton("", id="opt_c")
                        yield RadioButton("", id="opt_d")

                    yield Label("TIEMPO RESTANTE", id="timer_label")
                    yield ProgressBar(total=30, show_percentage=False, id="timer_bar")

                yield Button("PROCESAR", variant="primary", id="btn_next")

    def on_mount(self):
        self.query_one("#timer_bar").styles.bar_foreground = "red"
        self.preparar_fase()

    def preparar_fase(self):
        inst = self.query_one("#instructions")
        input_area = self.query_one("#input_v2")
        status = self.query_one("#status_line")

        if self.fase == 1:
            self.reto = trials_v2_logic.generar_reto_cifrado()
            msg = f"DESCIFRADO ({self.sub_step}/3)\nAlgoritmo: [cyan]{self.reto['tipo']}[/]\nCadena: [yellow]{self.reto['target']}[/]"
            inst.update(msg)
            status.update("[#666666]Sincronizando llaves de cifrado...[/]")

        elif self.fase == 2:
            secretos = ["BASE_DE_DATOS_URL", "GROQ_TOKEN", "GITHUB_TOKEN"]
            msg = f"INYECCIÓN DE SECRETOS ({self.sub_step}/3)\nConfigurando: [magenta]{secretos[self.sub_step-1]}[/]"
            inst.update(msg)
            input_area.text = ""
            status.update("[#666666]Escribiendo en la Bóveda de Sombras...[/]")

        elif self.fase == 3:
            input_area.add_class("hidden")
            inst.add_class("hidden")
            self.query_one("#quiz_box").remove_class("hidden")
            status.update("[#8A2BE2]EVALUACIÓN DE APTITUD TÉCNICA[/]")
            self.lanzar_pregunta()

    def lanzar_pregunta(self):
        if self.q_idx < len(self.preguntas):
            q = self.preguntas[self.q_idx]
            self.query_one("#q_text").update(f"[bold white]{q['q']}[/]")

            self.query_one("#opt_a").label = f"A) {q['options']['A']}"
            self.query_one("#opt_b").label = f"B) {q['options']['B']}"
            self.query_one("#opt_c").label = f"C) {q['options']['C']}"
            self.query_one("#opt_d").label = f"D) {q['options']['D']}"

            self.query_one("#options")._selected = None
            self.tiempo = 30
            self.query_one("#timer_bar").progress = 30
            self.tick()
        else:
            self.finalizar_fase_dos()

    def tick(self):
        if self.fase == 3 and self.tiempo > 0:
            self.tiempo -= 1
            self.query_one("#timer_bar").progress = self.tiempo
            self.set_timer(1, self.tick)
        elif self.fase == 3 and self.tiempo == 0:
            self.app.notify("¡TIEMPO AGOTADO!", severity="error")
            self.q_idx += 1
            self.lanzar_pregunta()

    def on_button_pressed(self, event: Button.Pressed):
        if self.fase == 1:
            val = self.query_one("#input_v2").text.strip()
            if val == self.reto['solucion']:
                if self.sub_step < 3:
                    self.sub_step += 1
                else:
                    self.fase = 2
                    self.sub_step = 1
                self.preparar_fase()
            else:
                self.app.notify("Error de descifrado.", severity="error")

        elif self.fase == 2:
            # Aquí podrías llamar a trials_v2_logic.inyectar_secreto(...) 
            # con el valor de input_area.text
            if self.sub_step < 3:
                self.sub_step += 1
            else:
                self.fase = 3
            self.preparar_fase()

        elif self.fase == 3:
            radioset = self.query_one("#options")
            if radioset.pressed_button:
                seleccion = radioset.pressed_button.id.split("_")[1].upper()
                correcta = self.preguntas[self.q_idx]['ans']

                if seleccion == correcta:
                    self.app.notify("Módulo validado.", severity="success")
                else:
                    self.app.notify("Inconsistencia técnica detectada.", severity="error")

                self.q_idx += 1
                self.lanzar_pregunta()
            else:
                self.app.notify("Debes seleccionar una respuesta.", severity="warning")

    def finalizar_fase_dos(self):
        trials_v2_logic.finalizar_fase_dos()
        self.app.notify("Protocolo SAP: ACCESO TOTAL CONCEDIDO.", severity="success")
        self.app.pop_screen()
        if hasattr(self.app, "verificar_acceso_shadow"):
            self.app.verificar_acceso_shadow()

    CSS = """
    #trial_box_v2 {
        width: 95%;
        height: auto;
        border: double #8A2BE2;
        padding: 1;
        background: #050505;
    }
    #title_v2 { text-align: center; color: #8A2BE2; text-style: bold; }
    #status_line { text-align: center; margin-bottom: 1; height: 1; font-style: italic; }
    #instructions { margin-bottom: 1; text-align: center; height: 4; }
    #input_v2 { height: 5; border: solid #333; background: #000; color: #8A2BE2; }
    .hidden { display: none; }
    #timer_bar { margin-top: 1; }
    #timer_label { text-align: center; color: red; text-style: italic; margin-top: 1; }
    #q_text { margin-bottom: 1; text-align: center; min-height: 3; }
    #options { background: transparent; border: none; margin-bottom: 1; }
    #btn_next { width: 100%; margin-top: 1; background: #8A2BE2; }
    """

