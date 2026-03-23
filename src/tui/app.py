from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, Label
from textual.containers import Container, Vertical, Center
from src.utils.ascii_loader import ASCIILoader
from src.logic.config import config
from src.tui.themes import THEMES
from src.tui.widgets import TelemetryBar
from src.logic.github_sync import sync_manager
import os

class ShadowGrimorio(App):
    """Orquestador persistente con soporte de temas reactivos y cifrado."""
    
    BINDINGS = [
        ("q", "quit", "Salir"),
        ("g", "agentes", "Agentes"),
        ("c", "chat", "Oráculo"),
        ("t", "next_theme", "Tema"),
        ("m", "main_menu", "Matriz")
    ]

    def __init__(self):
        super().__init__()
        # Sincronizamos con la configuración persistente
        self.nombre_tema = config.shadow_theme 
        self.tema = THEMES.get(self.nombre_tema, THEMES["CYBERPUNK"])
        self.cipher = config.get_cipher()

    def on_mount(self) -> None:
        """Configuración inicial al montar la app."""
        self.title = "SHADOW_GRIMORIO"
        self.sub_title = f"v3.13 | {config.shadow_alias}"
        self.aplicar_estilos_tema()

    def aplicar_estilos_tema(self) -> None:
        """Inyecta los colores del tema actual directamente en el DOM de Textual."""
        t = self.tema
        # Actualizamos el fondo de la pantalla principal
        self.screen.styles.background = t['bg']
        
        # Intentamos actualizar los estilos de los widgets si ya existen
        try:
            self.query_one("TelemetryBar").styles.color = t['primary']
            self.query_one("TelemetryBar").styles.border_bottom = ("solid", t['primary'])
            self.query_one("#logo").styles.color = t['primary']
            self.query_one("#status").styles.color = t['accent']
        except:
            pass # Los widgets aún no se han compuesto

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        with Container(id="main_layout"):
            with Vertical():
                with Center():
                    # El splash cargado desde assets/ascii
                    yield Static(ASCIILoader.get_art('splash'), id="logo")
                yield Label("[ NÚCLEO ONLINE ]", id="status")
        yield Footer()

    def action_chat(self) -> None:
        from src.tui.chat import ChatScreen
        self.push_screen(ChatScreen())

    def action_agentes(self) -> None:
        from src.tui.agents_menu import AgentsMenu
        self.push_screen(AgentsMenu())

    def action_next_theme(self) -> None:
        """Cicla entre los temas disponibles y actualiza la UI al instante."""
        temas = list(THEMES.keys())
        idx = (temas.index(self.nombre_tema) + 1) % len(temas)
        self.nombre_tema = temas[idx]
        self.tema = THEMES[self.nombre_tema]
        
        # Persistimos el cambio en el objeto config
        config.guardar_tema(self.nombre_tema)
        
        # Aplicamos el cambio visual sin reiniciar
        self.aplicar_estilos_tema()
        self.notify(f"Matriz Visual: {self.nombre_tema}", title="SISTEMA")

    def action_main_menu(self) -> None:
        from src.tui.main_menu import MainMenuScreen
        self.push_screen(MainMenuScreen())


    async def action_quit(self) -> None:
        """Protocolo de cierre con respaldo cifrado en la nube."""
        if not self.cipher:
            self.exit()
            return

        self.notify("🛡️ Cifrando botín y sincronizando...", severity="information")
        
        # Archivos que ShadowRoot07 considera vitales
        archivos_criticos = ["data/shadow_local.db", "config.yaml", ".env"]
        
        for ruta in archivos_criticos:
            if os.path.exists(ruta):
                try:
                    with open(ruta, "rb") as f:
                        datos = f.read()
                    
                    # Cifrado con la Master Key del .env
                    datos_cifrados = self.cipher.encrypt(datos)
                    ruta_tmp = f"{ruta}.shadow"
                    
                    with open(ruta_tmp, "wb") as f:
                        f.write(datos_cifrados)
                    
                    # Subida asíncrona a GitHub
                    await sync_manager.respaldar_archivo(ruta_tmp)
                    
                    if os.path.exists(ruta_tmp):
                        os.remove(ruta_tmp)
                except Exception as e:
                    self.notify(f"Fallo en backup {ruta}: {str(e)}", severity="error")
        
        self.exit()

if __name__ == "__main__":
    app = ShadowGrimorio()
    app.run()

