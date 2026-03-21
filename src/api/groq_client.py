import aiohttp
from loguru import logger
from src.logic.config import config

class GroqOraculo:
    """Cliente inteligente para Groq con auto-filtrado de modelos."""
    
    BASE_URL = "https://api.groq.com/openai/v1"
    
    def __init__(self):
        self.api_key = config.groq_api_key.get_secret_value()
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def obtener_modelos_disponibles(self):
        """Algoritmo de filtrado para evitar errores 403/404."""
        url = f"{self.BASE_URL}/models"
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=self.headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Filtramos modelos que suelen ser gratuitos/disponibles
                        # como llama3, mixtral o gemma.
                        modelos = [m['id'] for m in data['data'] if "preview" not in m['id']]
                        logger.info(f"Modelos detectados: {len(modelos)}")
                        return modelos
                    else:
                        logger.error(f"Error al listar modelos: {resp.status}")
                        return ["llama3-8b-8192"] # Fallback seguro
            except Exception as e:
                logger.error(f"Fallo de red: {e}")
                return ["llama3-8b-8192"]

    async def consultar(self, prompt: str, contexto_usuario: str = ""):
        """Envía el prompt al mejor modelo disponible."""
        modelos = await self.obtener_modelos_disponibles()
        modelo_activo = config.groq_model if config.groq_model in modelos else modelos[0]
        
        url = f"{self.BASE_URL}/chat/completions"
        payload = {
            "model": modelo_activo,
            "messages": [
                {"role": "system", "content": f"Eres el SHADOW_GRIMORIO. {contexto_usuario}"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data['choices'][0]['message']['content']
                elif resp.status == 413: # Request too large
                    return "ERROR: El pergamino es demasiado largo para la IA."
                else:
                    return f"ERROR CRÍTICO: El Oráculo responde con código {resp.status}"

# Instancia global
oraculo = GroqOraculo()

