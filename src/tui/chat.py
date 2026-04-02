import subprocess
import re
import asyncio
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Input, Log, Footer
from textual.containers import Container
from src.tui.widgets import TelemetryBar
from src.api.groq_client import oraculo
from src.logic.agent_manager import manager
from src.tui.modals import ConfirmBuildModal

class ChatScreen(Screen):
    BINDINGS = [
        ("ctrl+y", "copy_last", "Copiar último"),
        ("escape", "back", "Volver")
    ]

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        with Container(id="chat_container") as c:
            c.border_title = "CONEXIÓN CON EL ORÁCULO"
            yield Log(id="chat_log", highlight=True)
            yield Input(placeholder="Escribe al Oráculo...", id="chat_input")
        yield Footer()

    def on_mount(self) -> None:
        t = self.app.tema
        self.styles.background = t['bg']
        # 'heavy' es más estable que 'tall' en terminales móviles
        self.query_one("#chat_container").styles.border = ("heavy", t['primary'])
        self.query_one("#chat_input").focus()

    def action_back(self) -> None:
        self.app.pop_screen()

    async def action_copy_last(self) -> None:
        """Copiado Asíncrono: No congela la UI del ZTE."""
        texto = getattr(self.app, "last_oraculo_response", "")

        if not texto:
            self.app.notify("Buffer vacío", severity="warning")
            return

        # Limpiamos el texto antes de lanzarlo al hilo
        limpio = re.sub(r'\[.*?\]', '', texto).strip()

        # Ejecutamos el copiado en un hilo de fondo para evitar congelamiento
        def _shell_copy():
            try:
                process = subprocess.Popen(['termux-clipboard-set'], stdin=subprocess.PIPE)
                process.communicate(input=limpio.encode('utf-8'))
                return True
            except:
                return False

        # Lanzamos la tarea al fondo
        exito = await asyncio.to_thread(_shell_copy)
        
        if exito:
            self.app.notify("Copiado al portapapeles", title="SHADOW_CLIP")
        else:
            self.app.notify("Error al acceder al portapapeles", severity="error")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        texto = event.value.strip()
        if not texto: return

        log = self.query_one("#chat_log", Log)
        self.query_one("#chat_input").value = ""

        log.write(f"\n[USER]: {texto}")
        log.write(" >> [SISTEMA]: Procesando consulta...")

        try:
            agente_id = "THE_ARCHITECT" if any(p in texto.lower() for p in ["crea", "build", "escribe"]) else None
            respuesta = await oraculo.consultar(texto, agente_id=agente_id)

            # Sincronizamos con el buffer global de la App
            self.app.last_oraculo_response = respuesta

            if '"files"' in respuesta:
                match = re.search(r"\{.*\}", respuesta, re.DOTALL)
                if match:
                    try:
                        plano_raw = match.group(0)
                        def check_confirm(confirmado: bool) -> None:
                            if confirmado:
                                manager.ejecutar_plano_arquitecto(plano_raw)
                                log.write("\n[SISTEMA]: ✅ Materialización completa.")
                        self.app.push_screen(ConfirmBuildModal("Plano detectado"), check_confirm)
                    except: pass

            log.write(f"\n[ORÁCULO]: {respuesta}\n")

        except Exception as e:
            log.write(f"\n[ERROR]: {str(e)}")

        await asyncio.sleep(0.05)
        log.scroll_end()

