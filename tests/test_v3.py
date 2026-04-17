from textual.app import App
from src.tui.trial_screen_v3 import TrialScreenV3

class TestApp(App):
    def on_mount(self):
        self.push_screen(TrialScreenV3())

    # Mock de la función que llama la pantalla al final
    def verificar_acceso_shadow(self):
        print("Acceso verificado con éxito.")

if __name__ == "__main__":
    app = TestApp()
    app.run()

