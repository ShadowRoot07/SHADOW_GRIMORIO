import asyncio\
import aiohttp\
import ujson\
\
class GroqClient:\
\\tdef __init__(self):\
\\t\\tself.url = 'https://api.groq.com/predict'\
\
async def send_data(self, data):\
\\t\\tasync with aiohttp.ClientSession() as session:\
\\t\\t\\tasync with session.post(self.url, json=data) as response:\
\\t\\t\\t\\treturn await response.json()