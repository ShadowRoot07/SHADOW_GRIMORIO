# Definición de Paletas de Colores para la TUI de Shadow Grimorio
THEMES = {
    "CYBERPUNK": {
        "bg": "#000800", "primary": "#00ff00", "secondary": "#ff00ff", "accent": "#00ffff", "text": "#ffffff",
        "surface": "#001500"
    },
    "CYBERZEN": {
        "bg": "#050a05", "primary": "#4e9a06", "secondary": "#2e3436", "accent": "#8ae234", "text": "#eeeeec",
        "surface": "#0a110a"
    },
    "RETRO_TERMINAL": {
        "bg": "#000000", "primary": "#ffb000", "secondary": "#333333", "accent": "#ff8000", "text": "#ffb000",
        "surface": "#111111"
    },
    "CEO_OFFICE": {
        "bg": "#ffffff", "primary": "#2c3e50", "secondary": "#ecf0f1", "accent": "#3498db", "text": "#2c3e50",
        "surface": "#f8f9fa"
    },
    # ... (Deep Blue, Blood Neon, Toxic Waste se mantienen igual)
}

def get_theme(name: str) -> dict:
    """Retorna el tema solicitado o el por defecto."""
    return THEMES.get(name.upper(), THEMES["CYBERPUNK"])

def obtener_siguiente_tema(nombre_actual: str) -> str:
    nombres = list(THEMES.keys())
    idx = nombres.index(nombre_actual) if nombre_actual in nombres else 0
    return nombres[(idx + 1) % len(nombres)]
