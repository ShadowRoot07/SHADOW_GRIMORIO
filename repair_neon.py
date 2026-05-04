from sqlalchemy import text
from src.database.manager import db

def force_repair():
    print("📡 Conectando con Neon...")
    db.init_db()
    if not db.online:
        print("❌ No hay conexión a Neon. Revisa tu internet o DATABASE_URL.")
        return

    # Columnas que detectamos que faltan en tu error
    columnas = [
        ("rama_actual", "VARCHAR"),
        ("last_sync", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ]

    with db.engine_remote.connect() as conn:
        for col_nombre, col_tipo in columnas:
            try:
                print(f"🛠️ Intentando añadir {col_nombre}...")
                # Sintaxis PostgreSQL
                conn.execute(text(f"ALTER TABLE proyectos ADD COLUMN {col_nombre} {col_tipo};"))
                conn.commit()
                print(f"✅ Columna {col_nombre} creada.")
            except Exception as e:
                if "already exists" in str(e):
                    print(f"ℹ️ La columna {col_nombre} ya existía.")
                else:
                    print(f"❌ Fallo en {col_nombre}: {e}")

    print("\n💀 Ritual de reparación completado. Prueba iniciar el sistema.")

if __name__ == "__main__":
    force_repair()

