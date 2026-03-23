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
    def on_mount(self) -> None:
        t = self.app.tema
        self.styles.background = t['bg']
        container = self.query_one("#chat_container")
        container.styles.border = ("tall", t['primary'])

        chat_log = self.query_one("#chat_log")
        chat_log.styles.color = t['primary']

        chat_input = self.query_one("#chat_input")
        chat_input.styles.border = ("double", t['accent'])
        chat_input.styles.color = t['text']

    def compose(self) -> ComposeResult:
        yield TelemetryBar()
        with Container(id="chat_container") as c:
            c.border_title = "CONEXIÓN CON EL ORÁCULO"
            yield Log(id="chat_log", highlight=True)
            yield Input(placeholder="Escribe al Oráculo (ej: 'Crea un hola mundo')...", id="chat_input")
        yield Footer()

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
            # Pasamos el agente_id para que el Oráculo use la identidad correcta
            respuesta = await oraculo.consultar(texto, agente_id=agente_id)

            # 🔍 Lógica de Intercepción Robusta
            if '"files"' in respuesta or '"folders"' in respuesta:
                try:
                    # Extraer el bloque JSON puro
                    match = re.search(r"\{.*\}", respuesta, re.DOTALL)
                    if match:
                        plano_raw = match.group(0)
                        plano = json.loads(plano_raw)
                        
                        archivos = plano.get('files', [])
                        resumen = "Propuesta de Arquitectura:\n" + "\n".join([f" • {f['path']}" for f in archivos])

                        def check_confirm(confirmado: bool) -> None:
                            if confirmado:
                                res = manager.ejecutar_plano_arquitecto(plano_raw)
                                if res["status"] == "success":
                                    log.write(f"\n[SISTEMA]: ✅ Materialización completa.")
                                    for det in res.get("details", []):
                                        log.write(f"  {det}")
                                else:
                                    log.write(f"\n[ERROR]: {res.get('message')}")
                            else:
                                log.write("\n[SISTEMA]: Operación abortada.")

                        self.app.push_screen(ConfirmBuildModal(resumen), check_confirm)
                        
                        # Si es puro JSON, no imprimimos la basura en el chat
                        if len(respuesta) < len(plano_raw) + 20: 
                            log.scroll_end()
                            return 

                except Exception as e:
                    log.write(f"\n[SISTEMA]: Se detectó un plano pero el formato es inválido.")

            # Mostrar respuesta normal
            log.write(f"\n[ORÁCULO]: {respuesta}\n")

        except Exception as e:
            log.write(f"\n[ERROR CRÍTICO]: {str(e)}")

        log.scroll_end()

