from textual.app import App, ComposeResult
from textual.widgets import Footer, Static, Label
from textual.containers import Container, Vertical, Center, Middle
from src.utils.ascii_loader import ASCIILoader
from src.logic.config import config
from src.tui.themes import THEMES
from src.tui.widgets import TelemetryBar
from src.logic.github_sync import sync_manager
import os

class ShadowGrimorio(App):
    """Orquestador persistente con soporte de temas y cifrado."""

    BINDINGS = [
        ("q", "quit", "Salir"),
        ("g", "agentes", "Agentes"),
        ("c", "chat", "Oráculo"),
        ("t", "next_theme", "Tema")
    ]

    def __init__(self):
        super().__init__()
        self.nombre_tema = config.shadow_theme
        self.tema = THEMES.get(self.nombre_tema, THEMES["CYBERPUNK"])
        self.cipher = config.get_cipher()

    def get_css(self) -> str:
        t = self.tema
        return f"""
        Screen {{ background: {t['bg']}; align: center middle; }}
        
        TelemetryBar {{
            dock: top;
            height: 1;
            background: {t['bg']};
            color: {t['primary']};
            text-align: center;
            border-bottom: solid {t['primary']};
        }}

        #main_layout {{
            width: 100%;
            height: 1fr;
            align: center middle;
        }}

        #logo {{
            width: 100%;
            content-align: center middle;
            color: {t['primary']};
            margin-bottom: 1;
        }}

        #status {{
            width: 100%;
            text-align: center;
            color: {t['accent']};
            text-style: bold;
        }}

        Footer {{ background: {t['secondary']}; color: {t['text']}; }}
        """

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        with Container(id="main_layout"):
            with Vertical():
                with Center():
                    # Usamos expand=False para que el logo no intente ocupar más de lo que debe
                    yield Static(ASCIILoader.get_art('splash'), id="logo", expand=False)
                yield Label("[ NÚCLEO ONLINE ]", id="status")
        yield Footer()

    def action_chat(self) -> None:
        from src.tui.chat import ChatScreen
        self.push_screen(ChatScreen())

    def action_agentes(self) -> None:
        from src.tui.agents_menu import AgentsMenu
        self.push_screen(AgentsMenu())

    def action_next_theme(self) -> None:
        temas = list(THEMES.keys())
        idx = (temas.index(self.nombre_tema) + 1) % len(temas)
        self.nombre_tema = temas[idx]
        self.tema = THEMES[self.nombre_tema]
        config.guardar_tema(self.nombre_tema)
        self.refresh()
        self.notify(f"Matriz Visual: {self.nombre_tema}")

    async def action_quit(self) -> None:
        if not self.cipher:
            self.exit()
            return
        self.notify("🛡️ Cifrando botín...")
        archivos_criticos = ["data/shadow_local.db", "config.yaml", ".env"]
        for ruta in archivos_criticos:
            if os.path.exists(ruta):
                try:
                    with open(ruta, "rb") as f: datos = f.read()
                    datos_cifrados = self.cipher.encrypt(datos)
                    ruta_tmp = f"{ruta}.shadow"
                    with open(ruta_tmp, "wb") as f: f.write(datos_cifrados)
                    await sync_manager.respaldar_archivo(ruta_tmp)
                    os.remove(ruta_tmp)
                except Exception as e:
                    self.notify(f"Error en {ruta}: {str(e)}", severity="error")
        self.exit()

if __name__ == "__main__":
    app = ShadowGrimorio()
    app.run()

