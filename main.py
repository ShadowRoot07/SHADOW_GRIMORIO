import sys\
import os\
from core.engine import Engine\
from tui.app import App\
\
if __name__ == '__main__':\
\\tif sys.argv[1] == 'bot_on':\
\\t\\tEngine().start()\
\\telif sys.argv[1] == 'bot_off':\
\\t\\tEngine().stop()\
\\telif sys.argv[1] == 'tui':\
\\t\\tApp().run()\
\\telse:\
\\t\\tprint('Comando no reconocido')