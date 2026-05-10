import asyncio\
import websockets\
import ujson\
\
class BinanceClient:\
\\tdef __init__(self):\
\\t\\tself.ws_url = 'wss://stream.binance.com:9443/ws/btcusdt@ticker'\
\
async def connect(self):\
\\t\\tasync with websockets.connect(self.ws_url) as ws:\
\\t\\t\\twhile True:\
\\t\\t\\t\\ttry:\
\\t\\t\\t\\t\\tmsg = await ws.recv()\
\\t\\t\\t\\t\\tyield ujson.loads(msg)\
\\t\\t\\texcept websockets.ConnectionClosed:\
\\t\\t\\t\\tbreak