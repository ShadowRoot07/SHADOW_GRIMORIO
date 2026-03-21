from src.logic.load_agent import load_agent
from src.logic.github_sync import gh_sync

def ritual_de_compilacion():
    # 1. El Agente analiza tu ZTE Blade A54
    analisis = load_agent.analizar_tarea("compilacion_cpp", "alta")
    
    print(f"--- REPORTE DEL ORQUESTADOR ---")
    print(f"Dispositivo: {analisis['modelo_dispositivo']}")
    print(f"Decisión: {analisis['destino']}")
    print(f"Razón: {analisis['razon']}")

    # 2. Si decide ir a la nube, generamos el archivo automáticamente
    if analisis['destino'] == "GITHUB_ACTIONS":
        load_agent.notificar_estado("inicio_workflow", "core_high_perf")
        exito = gh_sync.generar_workflow_compilacion("core_high_perf")
        
        if exito:
            print("\n[!] ARCHIVO .yml CREADO. Haz 'git push' para activar la nube.")
            load_agent.notificar_estado("fin_compilacion")

if __name__ == "__main__":
    ritual_de_compilacion()

