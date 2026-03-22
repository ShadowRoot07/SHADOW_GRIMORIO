from textual.app import ComposeResult
from src.logic.config import ConfigManager # <--- Importado

# ... (dentro de la clase InitWizard)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_finish":
            # Obtener el label del RadioButton seleccionado
            radio_set = self.query_one(RadioSet)
            if radio_set.pressed_button:
                tema_seleccionado = str(radio_set.pressed_button.label)
                
                # PERSISTENCIA REAL
                ConfigManager.guardar_tema(tema_seleccionado)
                
                self.app.notify(f"MATRIZ {tema_seleccionado} SINCRONIZADA")
                self.app.pop_screen()
            else:
                self.app.notify("Selecciona una matriz primero", severity="error")

