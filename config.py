import os\
\
class Config:\
\\tdef __init__(self):\
\\t\\tself.binance_api_key = os.environ.get('BINANCE_API_KEY')\
\\t\\tself.binance_api_secret = os.environ.get('BINANCE_API_SECRET')\
\\t\\tself.groq_api_key = os.environ.get('GROQ_API_KEY')\
\\t\\tself.groq_api_secret = os.environ.get('GROQ_API_SECRET')\
\\t\\tself.api_endpoints = {\
\\t\\t\\t'binance':'wss://stream.binance.com:9443/ws/btcusdt@ticker',\
\\t\\t\\t'groq':'https://api.groq.com/v1/query'\
\\t\\t}