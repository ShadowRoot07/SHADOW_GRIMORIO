import aiohttp
import asyncio
import json
from loguru import logger
from src.logic.config import config
from src.database.manager import db  # Importamos la bóveda

class GroqOraculo:
    """Cliente robusto con llaves extraídas de la Bóveda de Sombras."""

    BASE_URL = "https://api.groq.com/openai/v1"

    def __init__(self):
        # Intentamos obtener de la Bóveda primero, si no, del config (fallback)
        self._api_key = self._cargar_llave()
        self.modelos_prohibidos = set()

    def _cargar_llave(self) -> str:
        """Extrae la llave de la Bóveda de forma segura."""
        llave_boveda = db.get_secret("GROQ_API_KEY")
        if llave_boveda:
            return llave_boveda
        
        # Si no hay nada en la DB, usamos lo que haya en el config (SecretStr o str)
        logger.warning("⚠️ GROQ_CLIENT: Llave no encontrada en Bóveda. Usando respaldo de Config.")
        try:
            return config.groq_api_key.get_secret_value()
        except AttributeError:
            return str(config.groq_api_key)

    def _recortar_contexto(self, texto: str, max_chars: int = 15000) -> str:
        """Evita el error 413 recortando el contexto si es excesivo."""
        if len(texto) > max_chars:
            logger.warning(f"⚠️ CONTEXTO EXCESIVO ({len(texto)} chars). Recortando a {max_chars}...")
            return texto[:max_chars] + "\n[...Contexto truncado por seguridad...]"
        return texto


    @property
    def headers(self):
        """Headers dinámicos para asegurar que siempre usen la llave más reciente."""
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json"
        }

    async def obtener_modelos_disponibles(self):
        """Filtra modelos para usar solo LLMs modernos, probados y aceptados."""
        url = f"{self.BASE_URL}/models"

        async with aiohttp.ClientSession() as session:
            try:
                custom_timeout = aiohttp.ClientTimeout(total=60)
                async with session.post(
            url,
            data=json.dumps(payload),
            headers=self.headers,
            timeout=custom_timeout # <--- Aplicar aquí
        ) as resp:
                    if resp.status == 200:
                        data = await resp.json()

                        modelos_permitidos = [
                            "llama-3.1-8b-instant",
                            "llama-3.3-70b-versatile",
                            "llama-3.1-70b-versatile",
                            "llama-3.2-11b-vision-preview",
                            "llama-3.2-3b-preview",
                            "mixtral-8x7b-32768",
                            "gemma2-9b-it"
                        ]

                        disponibles = [
                            m['id'] for m in data['data']
                            if m['id'] in modelos_permitidos
                            and m['id'] not in self.modelos_prohibidos
                        ]

                        return disponibles if disponibles else ["llama-3.1-8b-instant"]
                    
                    if resp.status == 401:
                        logger.error("❌ GROQ_CLIENT: Error 401. Llave de API inválida o expirada.")
                    
                    return ["llama-3.1-8b-instant"]
            except Exception as e:
                logger.error(f"Error de red al listar modelos: {e}")
                return ["llama-3.1-8b-instant"]

    async def consultar(self, prompt: str, agente_id: str = None):
        """Consulta al Oráculo con soporte para identidades específicas."""
        from src.logic.context_injector import ContextInjector
        
        # Refrescamos la llave antes de la consulta por si hubo cambios en la sesión
        self._api_key = self._cargar_llave()

        modelos_disponibles = await self.obtener_modelos_disponibles()
        modelo_activo = config.groq_model if config.groq_model in modelos_disponibles else modelos_disponibles[0]
        
        contexto_raw = ContextInjector.obtener_contexto_completo(agente_id, query_usuario=prompt)
        logger.debug(f"Modelo: {modelo_activo} | Agente: {agente_id}")

        contexto_sistema = self._recortar_contexto(str(contexto_raw).strip(), max_chars=9000)

        url = f"{self.BASE_URL}/chat/completions"

        payload = {
            "model": str(modelo_activo),
            "messages": [
                {"role": "system", "content": contexto_sistema}, # Contexto ya saneado
                {"role": "user", "content": str(prompt)}
            ],
            "temperature": 0.3,
            "max_tokens": 2048
        }

        reintentos = 0
        while reintentos < config.groq_retry_limit:
            # Backoff Exponencial: 2s, 4s, 8s...
            espera = config.groq_cooldown * (2 ** reintentos)
            if reintentos > 0:
                logger.info(f"⏳ Reintento {reintentos}/{config.groq_retry_limit}. Esperando {espera}s...")
            
            await asyncio.sleep(espera)

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

                        elif resp.status == 429:
                            # Rate Limit: Groq nos dice cuánto esperar en los headers
                            retry_after = resp.headers.get("Retry-After")
                            if retry_after:
                                await asyncio.sleep(float(retry_after))
                            reintentos += 1
                            continue

                        elif resp.status in [400, 404]:
                            error_data = await resp.json()
                            msg = error_data.get('error', {}).get('message', '')
                            # Si el modelo murió, lo sacamos de la lista y probamos otro
                            if "model" in msg.lower() or "not found" in msg.lower():
                                logger.warning(f"🚫 Modelo {modelo_activo} fallido. Cambiando...")
                                self.modelos_prohibidos.add(modelo_activo)
                                modelos_nuevos = await self.obtener_modelos_disponibles()
                                if modelos_nuevos:
                                    payload["model"] = modelos_nuevos[0]
                            reintentos += 1
                            continue

                        else:
                            logger.error(f"❌ Error inesperado: {resp.status}")
                            reintentos += 1

                except Exception as e:
                    logger.error(f"📡 Fallo de conexión en Termux: {e}")
                    reintentos += 1

        return "Se agotaron los reintentos tras bloqueos del Oráculo."

oraculo = GroqOraculo()

