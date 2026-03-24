import subprocess
import json
import re
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
        ("escape", "app.pop_screen", "Volver")
    ]

    def compose(self) -> ComposeResult:
        """Define la estructura visual de la pantalla (EL BLOQUE QUE FALTABA)."""
        yield TelemetryBar()
        with Container(id="chat_container") as c:
            c.border_title = "CONEXIÓN CON EL ORÁCULO"
            yield Log(id="chat_log", highlight=True)
            yield Input(placeholder="Escribe al Oráculo (ej: 'Crea un script de python')...", id="chat_input")
        yield Footer()

    def on_mount(self) -> None:
        """Aplica estilos basados en el tema actual."""
        t = self.app.tema
        self.styles.background = t['bg']
        container = self.query_one("#chat_container")
        container.styles.border = ("tall", t['primary'])

        chat_log = self.query_one("#chat_log")
        chat_log.styles.color = t['primary']
        
        chat_input = self.query_one("#chat_input")
        chat_input.styles.border = ("double", t['accent'])
        chat_input.styles.color = t['text']
        chat_input.focus()

    def action_copy_last(self) -> None:
        """Extrae el último mensaje del Oráculo y lo manda al portapapeles de Android."""
        try:
            log = self.query_one("#chat_log", Log)
            # Textual Log.lines puede contener objetos Rich. Console.export_text() es más seguro.
            contenido = log.export_plain()
            
            if not contenido:
                self.app.notify("No hay texto en el log", severity="warning")
                return

            # Separamos por líneas y buscamos la última respuesta del Oráculo
            lineas = contenido.splitlines()
            ultimo_mensaje = ""
            
            # Buscamos desde el final hacia arriba
            for i in range(len(lineas) - 1, -1, -1):
                if "[ORÁCULO]:" in lineas[i]:
                    # Tomamos desde donde empieza el mensaje hasta el final o hasta el siguiente tag
                    ultimo_mensaje = "\n".join(lineas[i:]).split("[ORÁCULO]:")[-1].strip()
                    break

            if ultimo_mensaje:
                # Usamos termux-clipboard-set
                process = subprocess.Popen(['termux-clipboard-set'], stdin=subprocess.PIPE)
                process.communicate(input=ultimo_mensaje.encode('utf-8'))
                self.app.notify("Copiado al portapapeles", title="SHADOW_CLIP")
            else:
                self.app.notify("No se detectó respuesta del Oráculo", severity="information")
        
        except Exception as e:
            self.app.notify(f"Fallo en copiado: {str(e)}", severity="error")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        texto = event.value.strip()
        if not texto: return

        log = self.query_one("#chat_log", Log)
        input_widget = self.query_one("#chat_input", Input)
        input_widget.value = ""

        log.write(f"\n[USER]: {texto}")

        # --- MOTOR DE ENRUTAMIENTO ---
        palabras_construccion = ["crea", "construye", "generar", "build", "refactoriza", "modifica", "escribe un archivo"]
        es_construccion = any(palabra in texto.lower() for palabra in palabras_construccion)

        agente_id = "THE_ARCHITECT" if es_construccion else None
        prompt_info = " >> [SISTEMA]: Invocando al Arquitecto..." if es_construccion else " >> [SISTEMA]: Consultando a la matriz..."
        log.write(prompt_info)

        try:
            respuesta = await oraculo.consultar(texto, agente_id=agente_id)

            # Lógica de Intercepción de Planos (Archivos)
            if '"files"' in respuesta or '"folders"' in respuesta:
                match = re.search(r"\{.*\}", respuesta, re.DOTALL)
                if match:
                    plano_raw = match.group(0)
                    try:
                        plano = json.loads(plano_raw)
                        archivos = plano.get('files', [])
                        resumen = "Propuesta de Arquitectura:\n" + "\n".join([f" • {f['path']}" for f in archivos])

                        def check_confirm(confirmado: bool) -> None:
                            if confirmado:
                                res = manager.ejecutar_plano_arquitecto(plano_raw)
                                if res["status"] == "success":
                                    log.write(f"\n[SISTEMA]: ✅ Materialización completa.")
                                else:
                                    log.write(f"\n[ERROR]: {res.get('message')}")
                            else:
                                log.write("\n[SISTEMA]: Operación abortada.")

                        self.app.push_screen(ConfirmBuildModal(resumen), check_confirm)
                        
                        if len(respuesta) < len(plano_raw) + 50:
                            log.scroll_end()
                            return
                    except:
                        pass

            log.write(f"\n[ORÁCULO]: {respuesta}\n")

        except Exception as e:
            log.write(f"\n[ERROR CRÍTICO]: {str(e)}")

        log.scroll_end()

