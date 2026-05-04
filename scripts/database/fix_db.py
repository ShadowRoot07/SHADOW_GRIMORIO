from sqlalchemy import text
from src.database.manager import db

def fix():
    db.init_db()
    engines = [("Local", db.engine_local)]
    if db.online:
        engines.append(("Neon", db.engine_remote))

    for name, engine in engines:
        print(f"🛠️ Reparando {name}...")
        with engine.connect() as conn:
            try:
                # SQL estándar para añadir columna si no existe
                conn.execute(text("ALTER TABLE proyectos ADD COLUMN rama_actual VARCHAR;"))
                conn.commit()
                print(f"✅ Columna añadida en {name}.")
            except Exception as e:
                print(f"ℹ️ {name} ya tenía la columna o falló: {e}")

if __name__ == "__main__":
    fix()

