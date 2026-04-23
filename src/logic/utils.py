import re

def limpiar_secuencias_ansi(texto: str) -> str:
    """
    Elimina secuencias de escape ANSI (CSI) que Termux/Terminal 
    pueden inyectar en el TextArea.
    """
    # Expresión regular para capturar secuencias de escape ANSI
    ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', texto)

def test_manual(): 
    pass

