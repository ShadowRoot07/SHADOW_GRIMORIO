from src.utils.hardware_bridge import hw

specs = hw.obtener_specs()
print("--- TEST DE HARDWARE ---")
print(f"Estado: {specs['status']}")
print(f"RAM Total: {specs['ram_mb']} MB")
print(f"Núcleos CPU: {specs['cores']}")

