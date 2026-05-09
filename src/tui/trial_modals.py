from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Input, Static
from textual.containers import Vertical, Grid
from src.logic.trials_manager import trials

class PhaseOneModal(ModalScreen[dict]):
    """Fase 1: Acertijos de Python y Test de Humildad."""
    
    def compose(self) -> ComposeResult:
        with Vertical(id="trial_container"):
            yield Label("💀 PRUEBA DE INICIACIÓN: FASE I", id="trial_title")
            yield Static("Pregunta de Desarrollo Web (Respuesta Humana Corta):", id="instruction")
            yield Label("[cyan]¿Qué sucede realmente cuando escribes una URL en el navegador?[/]")
            yield Input(placeholder="Escribe tu respuesta aquí...", id="user_input")
            yield Button("ENVIAR RESPUESTA", variant="primary", id="submit")

    def on_mount(self):
        trials.registrar_inicio_input()

    def on_button_pressed(self, event: Button.Pressed):
        val = self.query_one("#user_input").value
        if not trials.es_humano(val):
            self.app.notify("⚠️ IA DETECTADA. Honestidad requerida.", severity="error")
            return
        self.dismiss({"status": "ok", "answer": val})

    CSS = """
    #trial_container { width: 80%; height: auto; padding: 2; background: #050505; border: double #00FF00; }
    #trial_title { text-align: center; color: #00FF00; text-style: bold; }
    #instruction { margin: 1 0; color: #888; }
    """

class EthicsLoopModal(ModalScreen[str]):
    """Fase 3: El Bucle de los 42 Pasos (7 preguntas x 6 repeticiones)."""
    
    def __init__(self, rep: int):
        super().__init__()
        self.rep = rep

    def compose(self) -> ComposeResult:
        with Vertical(id="ethics_container"):
            yield Label(f"⚖️ BUCLE ÉTICO - REPETICIÓN {self.rep}/6", id="ethics_title")
            yield Label("Pregunta 1: ¿Priorizarías la seguridad del sistema sobre la privacidad del usuario?")
            yield Input(id="ans_1")
            # ... Aquí irían las otras 6 preguntas ...
            yield Button("CONFIRMAR CONSISTENCIA", variant="success", id="next")

    def on_button_pressed(self, event: Button.Pressed):
        # Aquí recolectaríamos las 7 respuestas y las devolveríamos como un hash
        ans = self.query_one("#ans_1").value
        self.dismiss(ans)

