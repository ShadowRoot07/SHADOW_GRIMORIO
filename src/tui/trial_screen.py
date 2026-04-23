from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Button, Label, TextArea
from textual.containers import Vertical, Center
from src.logic.trials_manager import trials_logic
from src.logic.utils import limpiar_secuencias_ansi

class TrialScreen(Screen):
    """Pantalla de bloqueo para las Pruebas de Iniciación (Fase 1)."""

    def __init__(self):
        super().__init__()
        progreso = trials_logic.obtener_progreso_db()
        self.current_step = progreso["step"]
        self.patience_count = progreso["paciencia"]

    def compose(self) -> ComposeResult:
        with Center():
            with Vertical(id="trial_box"):
                yield Label("🔒 PROTOCOLO DE ACCESO: FASE 1", id="title")
                yield Label("", id="challenge_desc")
                yield Label("", id="char_limit_msg")
                yield TextArea(id="trial_input", show_line_numbers=True)
                yield Label("Caracteres: 0", id="char_counter")
                yield Button("VALIDAR ENTRADA", variant="primary", id="btn_trial_f1")

    def on_mount(self):
        self.actualizar_desafio()

    def actualizar_desafio(self):
        if self.current_step > len(trials_logic.challenges):
            self.finalizar_fase_actual()
            return

        challenge = trials_logic.challenges[self.current_step - 1]
        self.query_one("#challenge_desc").update(f"[bold cyan]DESAFÍO {self.current_step}:[/]\n{challenge['task']}")
        self.query_one("#trial_input").text = ""
        self.query_one("#char_limit_msg").update(f"Rango: {challenge['min_chars']}-{challenge['max_chars']} caracteres.")
        trials_logic.registrar_inicio()

    def on_text_area_changed(self, event: TextArea.Changed):
        # Limpiamos visualmente el conteo
        texto_real = limpiar_secuencias_ansi(event.text_area.text)
        self.query_one("#char_counter").update(f"Caracteres: {len(texto_real)}")

    def on_button_pressed(self, event: Button.Pressed):
        val = self.query_one("#trial_input").text
        if trials_logic.validar_respuesta(val, self.current_step):
            # Lógica de paciencia para el último paso
            if self.current_step == 4 and self.patience_count < 2:
                self.patience_count += 1
                self.app.notify(f"Sincronización: {self.patience_count}/3", severity="warning")
                trials_logic.guardar_progreso_db(self.current_step, self.patience_count)
                self.actualizar_desafio()
            elif self.current_step < 4:
                self.current_step += 1
                trials_logic.guardar_progreso_db(self.current_step, 0)
                self.app.notify("Paso completado.", severity="success")
                self.actualizar_desafio()
            else:
                self.finalizar_fase_actual()
        else:
            self.app.notify("Error: Caracteres fuera de rango o entrada no humana.", severity="error")
            trials_logic.registrar_inicio()

    def finalizar_fase_actual(self):
        """Cierra la fase actual y fuerza a la App a evaluar la siguiente fase."""
        trials_logic.finalizar_fase_uno()
        self.app.notify("Fase 1 completada. Iniciando Fase 2...", severity="success")
        
        # Primero quitamos esta pantalla
        self.app.pop_screen()
        
        # TRIGGER CRÍTICO: Llamamos al método de la App principal para que 
        # detecte el rango 'F1_COMPLETADA' y lance la TrialScreenV2
        if hasattr(self.app, "verificar_acceso_shadow"):
            self.app.verificar_acceso_shadow()

    def action_back(self) -> None:
        pass

    def on_key(self, event):
        if event.key == "f1":
            # Dejamos que la App maneje el bypass
            return
        if event.key == "escape":
            event.prevent_default()
            self.app.notify("Acceso denegado: Completa las pruebas primero.", severity="error")

    CSS = """
    #trial_box {
        width: 90%;
        height: auto;
        border: double #00FF00;
        padding: 1;
        background: #050505;
    }
    #title { text-align: center; color: #00FF00; text-style: bold; margin-bottom: 1; }
    #challenge_desc { margin-bottom: 1; height: 3; text-align: center; }
    #char_limit_msg { color: #555555; text-align: center; margin-bottom: 1; text-style: italic; }
    #trial_input {
        height: 10;
        border: solid #333;
        background: #000;
        color: #00FF00;
    }
    #char_counter { text-align: right; color: #00AA00; margin-top: 1; }
    #btn_trial_f1 { width: 100%; margin-top: 1; }
    """

