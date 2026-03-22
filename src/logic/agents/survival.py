import time
from src.utils.hardware_bridge import hw
from src.logic.agent_manager import manager

def run():
    """Protocolo de Supervivencia: Monitorea batería y recursos."""
    while True:
        specs = hw.obtener_specs()
        
        # Lógica de Supervivencia
        if specs['status'] == "online":
            # Si la RAM está muy baja (ej: < 200MB libres), pausamos agentes pesados
            if specs['ram_mb'] < 500: 
                print("\n\x1b[1;31m[SURVIVAL]: RAM CRÍTICA. Suspendiendo agentes pesados...\x1b[0m")
                manager.apagar_agente("ghost_coder")
            
            # Aquí podríamos añadir lectura de batería vía C++ más adelante
        
        time.sleep(30) # Escanea cada 30 segundos en segundo plano

if __name__ == "__main__":
    run()

