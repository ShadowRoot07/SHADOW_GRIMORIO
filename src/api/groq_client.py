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
        """Filtra modelos activos y evita los que han dado error 403."""
        url = f"{self.BASE_URL}/models"
        await asyncio.sleep(0.5)

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers, timeout=config.groq_timeout) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        modelos = [
                            m['id'] for m in data['data']
                            if "preview" not in m['id'] and m['id'] not in self.modelos_prohibidos
                        ]
                        return modelos if modelos else [config.groq_model]
                    return [config.groq_model]
            except Exception as e:
                logger.error(f"Error de red al listar modelos: {e}")
                return [config.groq_model]

    async def consultar(self, prompt: str, agente_id: str = None):
        """Consulta al Oráculo con soporte para identidades específicas."""
        from src.logic.context_injector import ContextInjector

        modelos = await self.obtener_modelos_disponibles()
        modelo_activo = config.groq_model if config.groq_model in modelos else modelos[0]

        # 1. Obtener y Limpiar Contexto
        contexto_raw = ContextInjector.obtener_contexto_completo(agente_id, query_usuario=prompt)
        
        # --- FIX SEGURIDAD 400: Asegurar que el contexto sea un string limpio ---
        if not contexto_raw or not isinstance(contexto_raw, str):
            contexto_sistema = "Eres Shadow Grimorio, un orquestador de agentes en Termux."
        else:
            # Limpiamos posibles espacios en blanco excesivos que rompen el JSON
            contexto_sistema = contexto_raw.strip()

        url = f"{self.BASE_URL}/chat/completions"
        
        # 2. Construcción del Payload con validación
        payload = {
            "model": str(modelo_activo),
            "messages": [
                {"role": "system", "content": contexto_sistema},
                {"role": "user", "content": str(prompt)}
            ],
            "temperature": 0.3, # Bajamos a 0.3 para mayor precisión en el Arquitecto
            "max_tokens": 2048   # Aumentamos para que el código no salga cortado
        }

        reintentos = 0
        while reintentos < config.groq_retry_limit:
            await asyncio.sleep(config.groq_cooldown * (reintentos + 1))

            async with aiohttp.ClientSession() as session:
                try:
                    # Usamos json.dumps para asegurar un formateo correcto
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
                            error_data = await resp.text()
                            logger.error(f"⚠️ Error 400 (Bad Request): {error_data}")
                            return f"ERROR: Estructura de mensaje inválida (400). Detalle: {error_data[:50]}"

                        elif resp.status == 429:
                            logger.warning(f"⚠️ Rate limit. Reintento {reintentos+1}...")
                            reintentos += 1
                            continue

                        elif resp.status == 403:
                            self.modelos_prohibidos.add(modelo_activo)
                            return "ERROR: Acceso denegado (403). Cambiando de modelo..."

                        else:
                            error_msg = await resp.text()
                            return f"ERROR: Código {resp.status} de Groq."

                except Exception as e:
                    logger.error(f"Fallo de conexión: {e}")
                    reintentos += 1

        return "Se agotaron los reintentos."

oraculo = GroqOraculo()

