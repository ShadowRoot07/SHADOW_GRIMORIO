import random
import hashlib
import base64
import binascii
from src.database.manager import db
from src.database.models import Secreto, Usuario

class PhaseTwoManager:
    def __init__(self):
        # 32 Algoritmos/Formatos para la Prueba 1
        self.cifrados = [
            "Base64", "Hexadecimal", "Binario", "Reversa", "MD5", "SHA1",
            "Atbash", "Rot13", "Octal", "Base32", "Base85", "Decimal-ASCII",
            "URL-Encoding", "Morse-Code", "Bacon-Cipher", "Caesar-3",
            "SHA256-Short", "Double-Base64", "Hex-Reversa", "Upper-Case",
            "Snake-Case-Hex", "Binary-Inverted", "XOR-Fixed", "Base16",
            "Zlib-Comp", "Slugify", "B64-NoPadding", "JWT-Sim", "AES-Mock",
            "Shadow-Format", "Ghost-Protocol", "Vigenere-Mock"
        ]

        # 39 Preguntas para la Prueba 3 (Diccionario expandible)
        self.cuestionario = [
            {"q": "¿Qué agente gestiona el versionado con Git?", "options": {"A": "JANITOR", "B": "BRUMA_SYNC", "C": "EXPLORER", "D": "WATCHDOG"}, "ans": "B"},
            {"q": "¿Cuál es la altura del portador (ShadowRoot07)?", "options": {"A": "1.80m", "B": "1.92m", "C": "1.75m", "D": "2.00m"}, "ans": "B"},
            {"q": "¿Qué tecnología usa el 'Shadow Radar'?", "options": {"A": "Django", "B": "FastAPI + Gemini", "C": "React Native", "D": "Unity"}, "ans": "B"},
            {"q": "¿En qué entorno corre el Grimorio?", "options": {"A": "VS Code", "B": "Termux", "C": "PyCharm", "D": "Docker Hub"}, "ans": "B"},
            # Nota: Aquí puedes seguir pegando el resto de las 39 preguntas
        ]

    def generar_reto_cifrado(self):
        tipo = random.choice(self.cifrados)
        secreto_base = f"GHOST_{random.randint(1000, 9999)}"

        if tipo == "Base64": res = base64.b64encode(secreto_base.encode()).decode()
        elif tipo == "Hexadecimal": res = secreto_base.encode().hex()
        elif tipo == "Reversa": res = secreto_base[::-1]
        elif tipo == "Binario": res = ' '.join(format(ord(x), '08b') for x in secreto_base)
        else: res = hashlib.md5(secreto_base.encode()).hexdigest()[:10]

        return {"tipo": tipo, "target": res, "solucion": secreto_base}

    def obtener_preguntas_aleatorias(self, k=3):
        """Extrae k preguntas al azar del banco de 39."""
        return random.sample(self.cuestionario, k)

    def finalizar_fase_dos(self):
        """Otorga acceso total al sistema marcando el booleano global."""
        session = db.get_session()
        user = session.query(Usuario).first()
        if user:
            user.rango = "F2_COMPLETADA"
            user.pruebas_completadas = True 
            session.commit()
        session.close()

    def inyectar_secreto(self, nombre: str, valor: str):
        """Persistencia de tokens en la tabla de secretos."""
        session = db.get_session()
        try:
            nuevo = Secreto(nombre=nombre, valor_cifrado=valor)
            session.merge(nuevo)
            session.commit()
            return True
        except Exception:
            return False
        finally:
            session.close()

trials_v2_logic = PhaseTwoManager()

