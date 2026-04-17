from src.database.manager import db
from src.database.models import Usuario

session = db.get_session()
user = session.query(Usuario).first()
if user:
    user.pruebas_completadas = False
    user.rango = "Iniciado"
    session.commit()
    print("✅ Memoria de Fase 1 borrada. Usuario reseteado a 'Iniciado'.")
session.close()

