from textual.app import App
from src.tui.trial_screen_v2 import TrialScreenV2
from src.logic.identity_matrix import sap

class ShadowGrimorioTestApp(App):
    def on_mount(self):
        # Iniciamos en la Fase 2 (Cifrado y Secretos)
        self.push_screen(TrialScreenV2())

    def verificar_acceso_shadow(self):
        """Esta función simula la reacción del menú principal tras el éxito."""
        if sap.tiene_acceso_total():
            self.notify("SISTEMA: Rango Shadow_Coder detectado. Desbloqueando módulos...", severity="success")
        else:
            self.notify("ERROR: Rango insuficiente tras la prueba.", severity="error")

if __name__ == "__main__":
    app = ShadowGrimorioTestApp()
    app.run()

