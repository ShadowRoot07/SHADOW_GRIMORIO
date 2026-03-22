import aiohttp
import asyncio
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
        await asyncio.sleep(config.groq_cooldown)

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
                logger.error(f"Error de red: {e}")
                return [config.groq_model]

    async def consultar(self, prompt: str, agente_id: str = None):
        """Consulta al Oráculo con soporte para identidades específicas."""
        from src.logic.context_injector import ContextInjector

        modelos = await self.obtener_modelos_disponibles()
        modelo_activo = config.groq_model if config.groq_model in modelos else modelos[0]
        
        # Inyectamos el contexto pasando el ID del agente
        contexto_sistema = ContextInjector.obtener_contexto_completo(agente_id, query_usuario=prompt)

        url = f"{self.BASE_URL}/chat/completions"
        payload = {
            "model": modelo_activo,
            "messages": [
                {"role": "system", "content": contexto_sistema},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.4, # Bajamos la temperatura para que sea más preciso y menos "disperso"
            "max_tokens": 4096   # Forzamos un límite de salida más alto
        }

        reintentos = 0
        while reintentos < config.groq_retry_limit:
            await asyncio.sleep(config.groq_cooldown * (reintentos + 1))
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(url, json=payload, headers=self.headers, timeout=config.groq_timeout) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data['choices'][0]['message']['content']
                        elif resp.status == 429:
                            reintentos += 1
                            await asyncio.sleep(2**reintentos)
                            continue
                        elif resp.status == 403:
                            self.modelos_prohibidos.add(modelo_activo)
                            return "ERROR: Acceso denegado (403). Cambiando de modelo..."
                        else:
                            return f"ERROR: Código {resp.status} de Groq."
                except Exception as e:
                    logger.error(f"Fallo de conexión: {e}")
                    return f"ERROR de conexión: {e}"
        return "Se agotaron los reintentos tras bloqueos del Oráculo."

oraculo = GroqOraculo()

