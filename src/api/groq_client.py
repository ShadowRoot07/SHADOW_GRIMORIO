import aiohttp
import asyncio
import json
from loguru import logger
from src.logic.config import config

class GroqOraculo:
    """Cliente robusto con manejo de errores 4xx y pausas asíncronas."""

    BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(self):
        self.api_key = config.groq_api_key.get_secret_value()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.modelos_prohibidos = set()

    async def obtener_modelos_disponibles(self):
        """Filtra modelos para usar solo LLMs modernos, probados y aceptados."""
        url = f"{self.BASE_URL}/models"
        await asyncio.sleep(0.5)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, timeout=config.groq_timeout) as resp:
                    if resp.status == 200:
                        data = await resp.json()

                        # 🛡️ LISTA BLANCA ACTUALIZADA (Soporta Llama 3.1, 3.2 y 3.3)
                        # Hemos eliminado los modelos 'decommissioned' (llama3-70b-8192, etc.)
                        modelos_permitidos = [
                            "llama-3.3-70b-versatile",   # El más potente (Arquitecto Ideal)
                            "llama-3.1-70b-versatile",   # Versión anterior estable
                            "llama-3.1-8b-instant",      # Ultra rápido para móvil
                            "mixtral-8x7b-32768",        # Alternativa de alta capacidad
                            "gemma2-9b-it"               # Eficiente y preciso
                        ]

                        disponibles = [
                            m['id'] for m in data['data']
                            if m['id'] in modelos_permitidos
                            and m['id'] not in self.modelos_prohibidos
                        ]

                        # Fallback seguro: si la lista está vacía, usamos el 8b-instant
                        return disponibles if disponibles else ["llama-3.1-8b-instant"]

                    return ["llama-3.1-8b-instant"]
            except Exception as e:
                logger.error(f"Error de red al listar modelos: {e}")
                return ["llama-3.1-8b-instant"]

    async def consultar(self, prompt: str, agente_id: str = None):
        """Consulta al Oráculo con soporte para identidades específicas."""
        from src.logic.context_injector import ContextInjector

        modelos_disponibles = await self.obtener_modelos_disponibles()

        # Prioridad: Modelo en config -> Primer modelo disponible en lista blanca
        modelo_activo = config.groq_model if config.groq_model in modelos_disponibles else modelos_disponibles[0]

        # 1. Obtener y Limpiar Contexto
        contexto_raw = ContextInjector.obtener_contexto_completo(agente_id, query_usuario=prompt)

        # --- FIX SEGURIDAD: Asegurar que el contexto sea un string limpio ---
        if not contexto_raw or not isinstance(contexto_raw, str):
            contexto_sistema = "Eres Shadow Grimorio, un orquestador de agentes en Termux."
        else:
            contexto_sistema = contexto_raw.strip()

        url = f"{self.BASE_URL}/chat/completions"

        # 2. Construcción del Payload
        payload = {
            "model": str(modelo_activo),
            "messages": [
                {"role": "system", "content": contexto_sistema},
                {"role": "user", "content": str(prompt)}
            ],
            "temperature": 0.3,
            "max_tokens": 2048
        }

        reintentos = 0
        while reintentos < config.groq_retry_limit:
            # Pausa incremental para estabilidad en ZTE
            await asyncio.sleep(config.groq_cooldown * (reintentos + 1))

            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(
                        url,
                        data=json.dumps(payload),
                        headers=self.headers,
                        timeout=config.groq_timeout
                    ) as resp:

                        if resp.status == 200:
                            data = await resp.json()
                            return data['choices'][0]['message']['content']

                        elif resp.status == 400:
                            error_data = await resp.json()
                            msg = error_data.get('error', {}).get('message', 'Error desconocido')
                            logger.error(f"⚠️ Error 400: {msg}")
                            
                            # Si el modelo ya no existe, lo prohibimos para esta sesión
                            if "decommissioned" in msg.lower() or "model" in msg.lower():
                                self.modelos_prohibidos.add(modelo_activo)
                                logger.info(f"🚫 Modelo {modelo_activo} descartado por obsolescencia.")
                            
                            return f"ERROR 400: {msg[:100]}"

                        elif resp.status == 429:
                            logger.warning(f"⚠️ Rate limit (429). Reintento {reintentos+1}...")
                            reintentos += 1
                            continue

                        elif resp.status == 403:
                            self.modelos_prohibidos.add(modelo_activo)
                            return "ERROR 403: Acceso denegado al modelo."

                        else:
                            error_msg = await resp.text()
                            return f"ERROR: Código {resp.status} de Groq."

                except Exception as e:
                    logger.error(f"Fallo de conexión en Termux: {e}")
                    reintentos += 1

        return "Se agotaron los reintentos tras bloqueos del Oráculo."

oraculo = GroqOraculo()

