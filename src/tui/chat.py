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
    """Pantalla de chat optimizada para dispositivos móviles (ZTE Blade A54)."""
    
    # Bindings simplificados y directos
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
        # Usamos 'heavy' en lugar de 'tall' para reducir carga gráfica
        self.query_one("#chat_container").styles.border = ("heavy", t['primary'])
        self.query_one("#chat_input").focus()

    def action_back(self) -> None:
        """Cierra la pantalla actual de forma segura."""
        self.app.pop_screen()

    def action_copy_last(self) -> None:
        """Copia el buffer de memoria de la App. No toca el widget Log."""
        # Recuperamos del buffer global que definimos en app.py
        texto_a_copiar = getattr(self.app, "last_oraculo_response", "")

        if not texto_a_copiar:
            self.app.notify("Buffer vacío: Espera a que el Oráculo responda", severity="warning")
            return

        try:
            # Limpieza agresiva de etiquetas Rich/Textual
            limpio = re.sub(r'\[.*?\]', '', texto_a_copiar).strip()
            
            # Ejecución directa en el portapapeles de Termux
            process = subprocess.Popen(['termux-clipboard-set'], stdin=subprocess.PIPE)
            process.communicate(input=limpio.encode('utf-8'))
            
            self.app.notify("Copiado al portapapeles", title="SHADOW_CLIP")
        except Exception as e:
            self.app.notify(f"Error de sistema: {e}", severity="error")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        texto = event.value.strip()
        if not texto: 
            return

        log = self.query_one("#chat_log", Log)
        self.query_one("#chat_input").value = ""
        
        # Feedback visual inmediato
        log.write(f"\n[USER]: {texto}")
        log.write(" >> [SISTEMA]: Consultando al Oráculo...")

        try:
            # Identificar si se requiere al Arquitecto
            agente_id = "THE_ARCHITECT" if any(p in texto.lower() for p in ["crea", "build", "escribe", "genera"]) else None
            
            # Consulta asíncrona
            respuesta = await oraculo.consultar(texto, agente_id=agente_id)

            # ACTUALIZACIÓN DEL BUFFER (Clave para CTRL+Y)
            self.app.last_oraculo_response = respuesta

            # Detección de planos de construcción (JSON)
            if '"files"' in respuesta:
                match = re.search(r"\{.*\}", respuesta, re.DOTALL)
                if match:
                    try:
                        plano_raw = match.group(0)
                        def check_confirm(confirmado: bool) -> None:
                            if confirmado:
                                manager.ejecutar_plano_arquitecto(plano_raw)
                                log.write("\n[SISTEMA]: ✅ Despliegue de archivos completado.")
                        self.app.push_screen(ConfirmBuildModal("Plano detectado"), check_confirm)
                    except Exception:
                        pass

            # Escritura de la respuesta
            log.write(f"\n[ORÁCULO]: {respuesta}\n")

        except Exception as e:
            log.write(f"\n[ERROR CRÍTICO]: {str(e)}")
        
        # Scroll suave para evitar congelamiento de UI en móvil
        await asyncio.sleep(0.1)
        log.scroll_end()

