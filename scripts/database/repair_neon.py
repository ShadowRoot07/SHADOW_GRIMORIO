from sqlalchemy import text
from src.database.manager import db

def force_repair_v2():
    print("📡 Iniciando Protocolo de Reparación Atómica...")
    db.init_db()
    if not db.online:
        print("❌ Neon fuera de alcance.")
        return

    columnas = [
        ("rama_actual", "VARCHAR"),
        ("last_sync", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ]

    # Usamos el engine directamente para manejar transacciones individuales
    for col_nombre, col_tipo in columnas:
        print(f"🛠️ Procesando: {col_nombre}...")
        # Abrimos una conexión nueva por cada columna para asegurar limpieza total
        with db.engine_remote.connect() as conn:
            try:
                conn.execute(text(f"ALTER TABLE proyectos ADD COLUMN {col_nombre} {col_tipo};"))
                conn.commit()
                print(f"✅ Columna {col_nombre} integrada exitosamente.")
            except Exception as e:
                # Si falla, hacemos rollback para limpiar el estado de la conexión
                conn.rollback()
                if "already exists" in str(e).lower():
                    print(f"ℹ️ {col_nombre} ya existe en el tejido de Neon.")
                else:
                    print(f"❌ Error crítico en {col_nombre}: {e}")

    print("\n💀 Reparación finalizada. Ejecuta main.py para verificar.")

if __name__ == "__main__":
    force_repair_v2()

