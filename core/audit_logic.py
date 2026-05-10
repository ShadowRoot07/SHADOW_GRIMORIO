import logging
from database import Database

class AuditLogic:
    def __init__(self):
        self.database = Database()

    def log_event(self, event):
        # Registrar el evento en la base de datos
        self.database.log_event(event)

    def get_audit_log(self):
        # Obtener el registro de eventos de la base de datos
        data = self.database.get_audit_log()

        return data
