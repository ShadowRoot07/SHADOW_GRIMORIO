from .schema import Base, engine
from sqlalchemy.orm import sessionmaker
from core import trading_logic, audit_logic, monitoring_logic, security_logic, scalability_logic
from machine_learning import MLModel

class Database:
    def __init__(self):
        self.session = sessionmaker(bind=engine)()

    def connect(self):
        # Conectar con la base de datos
        self.session.commit()

    def disconnect(self):
        # Desconectar de la base de datos
        self.session.rollback()

    def get_market_data(self):
        # Obtener los datos de mercado de la base de datos
        return self.session.query(MarketData).all()

    def get_trades(self):
        # Obtener los datos de las transacciones de la base de datos
        return self.session.query(Trades).all()

    def log_event(self, event):
        # Registrar el evento en la base de datos
        self.session.add(event)
        self.session.commit()

    def get_audit_log(self):
        # Obtener el registro de eventos de la base de datos
        return self.session.query(AuditLog).all()

    def log_system_info(self, data):
        # Registrar la información del sistema en la base de datos
        self.session.add(data)
        self.session.commit()

    def get_ml_model(self):
        # Obtener el modelo de aprendizaje automático de la base de datos
        return self.session.query(MLModel).all()
