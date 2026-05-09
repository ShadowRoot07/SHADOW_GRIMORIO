from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, ProgressBar, RadioSet, RadioButton
from textual.containers import Vertical, Center
from src.logic.trials_v2_manager import trials_v2_logic

class TrialScreenV3(Screen):
    """Fase 3: Evaluación técnica bajo presión (15s)."""

    def __init__(self):
        super().__init__()
        self.tiempo = 15
        self.preguntas = trials_v2_logic.obtener_preguntas_aleatorias(3)
        self.q_idx = 0
        self.timer_active = False

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="trial_box_v3"):
                yield Label("💀 PROTOCOLO SAP: FASE 3 (PRESIÓN)", id="title_v3")
                yield Label("", id="debug_status")
                yield Label("", id="q_text")

                with RadioSet(id="options"):
                    yield RadioButton("", id="opt_a")
                    yield RadioButton("", id="opt_b")
                    yield RadioButton("", id="opt_c")
                    yield RadioButton("", id="opt_d")

                yield Label("TIEMPO RESTANTE", id="timer_label")
                yield ProgressBar(total=15, show_percentage=False, id="timer_bar")
                yield Button("CONFIRMAR SELECCIÓN", variant="primary", id="btn_confirm")

    def on_mount(self):
        self.query_one("#timer_bar").styles.bar_foreground = "red"
        self.lanzar_pregunta()

    def lanzar_pregunta(self):
        if self.q_idx < len(self.preguntas):
            q = self.preguntas[self.q_idx]
            self.query_one("#q_text").update(f"[bold white]{q['q']}[/]")

            opts = q['options']
            self.query_one("#opt_a").label = f"A) {opts['A']}"
            self.query_one("#opt_b").label = f"B) {opts['B']}"
            self.query_one("#opt_c").label = f"C) {opts['C']}"
            self.query_one("#opt_d").label = f"D) {opts['D']}"

            # Limpieza de cualquier rastro previo en el área de estado
            self.query_one("#debug_status").update("[#1a1a1a]Analizando integridad...[/]")

            self.query_one("#options")._selected = None
            self.tiempo = 15
            self.query_one("#timer_bar").progress = 15

            if not self.timer_active:
                self.timer_active = True
                self.tick()
        else:
            self.finalizar_sistema()

    def tick(self):
        if self.tiempo > 0 and self.q_idx < len(self.preguntas):
            self.tiempo -= 1
            self.query_one("#timer_bar").progress = self.tiempo
            self.set_timer(1, self.tick)
        elif self.tiempo == 0:
            self.timer_active = False
            self.app.notify("¡TIEMPO AGOTADO!", severity="error")
            self.q_idx += 1
            self.lanzar_pregunta()

    def on_button_pressed(self, event: Button.Pressed):
        radioset = self.query_one("#options")
        if radioset.pressed_button:
            seleccion = radioset.pressed_button.id.split("_")[1].upper()
            if seleccion == self.preguntas[self.q_idx]['ans']:
                self.app.notify("Módulo Validado", severity="success")
            else:
                self.app.notify("Inconsistencia detectada", severity="error")

            self.q_idx += 1
            self.lanzar_pregunta()
        else:
            self.app.notify("Selecciona una opción", severity="warning")

    def finalizar_sistema(self):
        trials_v2_logic.finalizar_fase_dos()
        self.app.notify("ACCESO TOTAL CONCEDIDO", severity="success")
        self.app.pop_screen() # Cierra V3
        self.app.pop_screen() # Cierra V2
        if hasattr(self.app, "verificar_acceso_shadow"):
            self.app.verificar_acceso_shadow()

    CSS = """
    #trial_box_v3 {
        width: 95%;
        height: auto;
        border: double red;
        padding: 1;
        background: #080000;
    }
    #title_v3 {
        text-align: center;
        color: red;
        text-style: bold;
    }
    #debug_status {
        text-align: center;
        height: 1;
        color: #444444;
        margin-bottom: 1;
    }
    #q_text {
        margin: 1 0;
        text-align: center;
        min-height: 3;
    }
    #timer_label {
        text-align: center;
        color: red;
        margin-top: 1;
    }
    #options {
        background: transparent;
        border: none;
    }
    #btn_confirm {
        width: 100%;
        margin-top: 1;
        background: red;
    }
    """

