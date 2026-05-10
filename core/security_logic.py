import hashlib
import logging
from database import Database

class SecurityLogic:
    def __init__(self):
        self.database = Database()

    def hash_password(self, password):
        # Hashear la contraseña
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        return hashed_password

    def verify_password(self, password, hashed_password):
        # Verificar la contraseña
        return hashlib.sha256(password.encode()).hexdigest() == hashed_password
