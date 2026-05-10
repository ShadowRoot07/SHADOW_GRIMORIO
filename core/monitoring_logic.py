import psutil
import logging
from database import Database

class MonitoringLogic:
    def __init__(self):
        self.database = Database()

    def get_system_info(self):
        # Obtener la información del sistema
        data = {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }

        return data

    def log_system_info(self, data):
        # Registrar la información del sistema en la base de datos
        self.database.log_system_info(data)
