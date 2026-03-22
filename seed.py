from src.database.manager import db
from src.database.models import Usuario

session = db.get_session()
if not session.query(Usuario).first():
    # Usamos tus datos reales
    yo = Usuario(alias="ShadowRoot07", rango="Desarrollador Fullstack Mobile")
    session.add(yo)
    session.commit()
    print("✅ Perfil de ShadowRoot07 inyectado en la base de datos.")
session.close()

