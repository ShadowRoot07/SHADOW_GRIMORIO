import asyncio
import logging
from database import Database
from api import BinanceClient, GroqClient
from tui import App
from machine_learning import MLModel
from trading_logic import TradingLogic
from audit_logic import AuditLogic
from monitoring_logic import MonitoringLogic
from security_logic import SecurityLogic
from scalability_logic import ScalabilityLogic

class Engine:
    def __init__(self):
        self.database = Database()
        self.binance_client = BinanceClient()
        self.groq_client = GroqClient()
        self.app = App()
        self.ml_model = MLModel()
        self.trading_logic = TradingLogic()
        self.audit_logic = AuditLogic()
        self.monitoring_logic = MonitoringLogic()
        self.security_logic = SecurityLogic()
        self.scalability_logic = ScalabilityLogic()

    def start(self):
        # Iniciar la conexión con la base de datos
        self.database.connect()

        # Iniciar la conexión con la API de Binance
        self.binance_client.connect()

        # Iniciar la conexión con la API de Groq
        self.groq_client.connect()

        # Iniciar la aplicación de usuario
        self.app.run()

        # Iniciar el modelo de aprendizaje automático
        self.ml_model.train()

    def stop(self):
        # Detener la conexión con la base de datos
        self.database.disconnect()

        # Detener la conexión con la API de Binance
        self.binance_client.disconnect()

        # Detener la conexión con la API de Groq
        self.groq_client.disconnect()

        # Detener la aplicación de usuario
        self.app.stop()

        # Detener el modelo de aprendizaje automático
        self.ml_model.stop()
