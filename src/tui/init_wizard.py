from textual.screen import Screen
from textual.widgets import Input, Button, Static, Checkbox
from textual.containers import Vertical, Horizontal
from src.logic.init_profile import ProfileManager

class InitWizard(Screen):
    """Pantalla de primer encuentro con el Grimorio."""
    
    def compose(self):
        yield Vertical(
            Static("[bold green]-- RITUAL DE INICIACIÓN --[/bold green]", id="title"),
            Static("¿Cómo debemos llamarte en la red?"),
            Input(placeholder="Alias (Ej: ShadowRoot07)", id="alias_input"),
            Static("\nMarca las tecnologías que ya dominas:"),
            Checkbox("Python", value=True, id="check_python"),
            Checkbox("C++ / C", id="check_cpp"),
            Checkbox("React / JS", id="check_react"),
            Checkbox("FastAPI / Django", id="check_backend"),
            Horizontal(
                Button("Sellar Contrato", variant="success", id="btn_save"),
                classes="actions"
            ),
            id="wizard_container"
        )

    def on_button_pressed(self, event):
        if event.button.id == "btn_save":
            alias = self.query_one("#alias_input").value
            techs = []
            if self.query_one("#check_python").value: techs.append("Python")
            if self.query_one("#check_cpp").value: techs.append("C++")
            # ... añadir las demás
            
            ProfileManager.registrar_usuario(alias, techs)
            self.app.pop_screen() # Volver a la app principal

