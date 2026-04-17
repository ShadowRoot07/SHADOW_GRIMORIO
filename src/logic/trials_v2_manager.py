import random
import hashlib
import base64
import binascii
from loguru import logger
from src.database.manager import db
from src.database.models import Secreto, Usuario

class PhaseTwoManager:
    def __init__(self):
        # Algoritmos para la Prueba 1
        self.cifrados = [
            "Base64", "Hexadecimal", "Binario", "Reversa", "MD5", "SHA1",
            "Atbash", "Rot13", "Octal", "Base32", "Base85", "Decimal-ASCII",
            "URL-Encoding", "Morse-Code", "Bacon-Cipher", "Caesar-3",
            "SHA256-Short", "Double-Base64", "Hex-Reversa", "Upper-Case"
        ]

        # Banco de 39 preguntas técnicas (Programación & Tech)
        self.cuestionario = [
            # PYTHON & LOGIC
            {"q": "¿Qué método se usa en Python para añadir un elemento al final de una lista?", "options": {"A": "push()", "B": "add()", "C": "append()", "D": "insert()"}, "ans": "C"},
            {"q": "¿Cuál es la salida de: print(type([]))?", "options": {"A": "<class 'tuple'>", "B": "<class 'list'>", "C": "<class 'dict'>", "D": "<class 'array'>"}, "ans": "B"},
            {"q": "¿Qué significa el principio DRY en programación?", "options": {"A": "Don't Repeat Yourself", "B": "Data Ready Yield", "C": "Do Run Yearly", "D": "Direct Read Yield"}, "ans": "A"},
            {"q": "¿Cuál es la complejidad temporal de una búsqueda binaria?", "options": {"A": "O(n)", "B": "O(1)", "C": "O(log n)", "D": "O(n log n)"}, "ans": "C"},
            {"q": "¿Qué palabra clave se usa para crear una función anónima en Python?", "options": {"A": "def", "B": "anon", "C": "lambda", "D": "func"}, "ans": "C"},
            {"q": "En Python, ¿cuál es el resultado de 3 * 'A'?", "options": {"A": "AAA", "B": "3A", "C": "Error", "D": "A3"}, "ans": "A"},
            {"q": "¿Qué hace el operador '//' en Python?", "options": {"A": "División exacta", "B": "Módulo", "C": "División de enteros (suelo)", "D": "Exponente"}, "ans": "C"},
            {"q": "¿Cómo se manejan las excepciones en Python?", "options": {"A": "try/except", "B": "catch/throw", "C": "if/error", "D": "handle/exit"}, "ans": "A"},
            
            # WEB & API (FastAPI/Django)
            {"q": "¿Qué significa el código de estado HTTP 404?", "options": {"A": "OK", "B": "Unauthorized", "C": "Not Found", "D": "Server Error"}, "ans": "C"},
            {"q": "¿Cuál es el método HTTP usado para actualizar un recurso existente?", "options": {"A": "GET", "B": "POST", "C": "PUT", "D": "DELETE"}, "ans": "C"},
            {"q": "En FastAPI, ¿qué librería se usa para la validación de datos?", "options": {"A": "Django", "B": "Pydantic", "C": "Flask", "D": "SQLAlchemy"}, "ans": "B"},
            {"q": "¿Qué es un middleware?", "options": {"A": "Una base de datos", "B": "Código que corre entre la petición y la respuesta", "C": "Un hardware", "D": "Un compilador"}, "ans": "B"},
            {"q": "¿Qué formato es el más común para intercambiar datos en APIs REST?", "options": {"A": "XML", "B": "JSON", "C": "CSV", "D": "YAML"}, "ans": "B"},
            {"q": "¿Qué significa JWT?", "options": {"A": "Java Web Token", "B": "JSON Web Token", "C": "Just Web Time", "D": "Joint Web Tool"}, "ans": "B"},

            # DATABASES & SQL
            {"q": "¿Qué comando SQL se usa para eliminar todos los registros de una tabla sin borrar la tabla?", "options": {"A": "DELETE", "B": "DROP", "C": "TRUNCATE", "D": "REMOVE"}, "ans": "C"},
            {"q": "¿Qué es una Foreign Key?", "options": {"A": "Una clave para cifrar", "B": "Un vínculo entre dos tablas", "C": "Una clave temporal", "D": "El nombre de la DB"}, "ans": "B"},
            {"q": "¿Qué base de datos es NoSQL?", "options": {"A": "PostgreSQL", "B": "MySQL", "C": "MongoDB", "D": "SQLite"}, "ans": "C"},
            {"q": "¿Qué hace el comando 'GROUP BY' en SQL?", "options": {"A": "Ordena resultados", "B": "Agrupa filas con los mismos valores", "C": "Filtra nulos", "D": "Borra duplicados"}, "ans": "B"},
            
            # GIT & ARCHITECTURE
            {"q": "¿Qué comando de Git se usa para ver el historial de commits?", "options": {"A": "git status", "B": "git history", "C": "git log", "D": "git diff"}, "ans": "C"},
            {"q": "¿Qué es un 'Docker Image'?", "options": {"A": "Una foto del servidor", "B": "Una plantilla ejecutable con el software", "C": "Un hardware virtual", "D": "Un editor de texto"}, "ans": "B"},
            {"q": "¿Qué comando descarga cambios de un repo remoto sin fusionarlos?", "options": {"A": "git pull", "B": "git fetch", "C": "git push", "D": "git commit"}, "ans": "B"},
            {"q": "¿Cuál es la función del archivo '.gitignore'?", "options": {"A": "Subir archivos rápido", "B": "Excluir archivos del seguimiento de Git", "C": "Cifrar el repo", "D": "Guardar contraseñas"}, "ans": "B"},
            {"q": "¿Qué es un Webhook?", "options": {"A": "Un virus", "B": "Una llamada automática entre apps tras un evento", "C": "Un tipo de cable", "D": "Un navegador"}, "ans": "B"},
            
            # OPERATING SYSTEMS & TERMUX
            {"q": "En Linux/Termux, ¿qué comando muestra el directorio actual?", "options": {"A": "dir", "B": "pwd", "C": "ls", "D": "cd"}, "ans": "B"},
            {"q": "¿Qué hace 'chmod +x archivo'?", "options": {"A": "Borra el archivo", "B": "Lo hace ejecutable", "C": "Lo oculta", "D": "Lo comprime"}, "ans": "B"},
            {"q": "¿Cuál es el gestor de paquetes por defecto en Debian/Ubuntu?", "options": {"A": "pip", "B": "npm", "C": "apt", "D": "brew"}, "ans": "C"},
            {"q": "¿Qué significa SSH?", "options": {"A": "Secure Shell", "B": "Super Shadow Host", "C": "Simple Script Handler", "D": "System Shell"}, "ans": "A"},

            # ADVANCED / MISC
            {"q": "¿Qué es la recursividad?", "options": {"A": "Un bucle infinito", "B": "Una función que se llama a sí misma", "C": "Un error de memoria", "D": "Un tipo de variable"}, "ans": "B"},
            {"q": "¿Qué significa 'Big O Notation'?", "options": {"A": "El tamaño del archivo", "B": "La eficiencia de un algoritmo", "C": "La versión del software", "D": "Un tipo de dato"}, "ans": "B"},
            {"q": "¿Qué es un 'Deadlock' en sistemas operativos?", "options": {"A": "Un reinicio rápido", "B": "Bloqueo mutuo entre procesos", "C": "Una conexión segura", "D": "Un error de disco"}, "ans": "B"},
            {"q": "¿Qué puerto usa por defecto el protocolo HTTP?", "options": {"A": "443", "B": "22", "C": "80", "D": "21"}, "ans": "C"},
            {"q": "¿Qué es el Garbage Collector?", "options": {"A": "Un antivirus", "B": "Sistema de gestión automática de memoria", "C": "Un limpiador de discos", "D": "Un programador"}, "ans": "B"},
            {"q": "¿Cuál es el componente principal del Kernel de Linux?", "options": {"A": "El Shell", "B": "La gestión de recursos de hardware", "C": "El escritorio", "D": "El navegador"}, "ans": "B"},
            {"q": "¿Qué significa 'Open Source'?", "options": {"A": "Software gratis solamente", "B": "Código fuente accesible para todos", "C": "Software sin licencia", "D": "Código secreto"}, "ans": "B"},
            {"q": "¿Qué hace 'git stash'?", "options": {"A": "Borra los cambios", "B": "Guarda cambios temporalmente sin commitear", "C": "Sube cambios a la nube", "D": "Crea una rama"}, "ans": "B"},
            {"q": "¿Qué es un Singleton?", "options": {"A": "Un patrón que asegura una única instancia de una clase", "B": "Una variable sola", "C": "Una función sin retorno", "D": "Un tipo de base de datos"}, "ans": "A"},
            {"q": "¿Qué herramienta se usa para orquestar contenedores?", "options": {"A": "Docker Compose", "B": "Kubernetes", "C": "Ambas", "D": "Ninguna"}, "ans": "C"},
            {"q": "¿Cuál es la extensión de un archivo de bytecode en Python?", "options": {"A": ".py", "B": ".pyc", "C": ".exe", "D": ".bin"}, "ans": "B"},
            {"q": "¿Qué es el Event Loop en entornos asíncronos?", "options": {"A": "Un bucle de música", "B": "Mecanismo que gestiona tareas no bloqueantes", "C": "Un error de red", "D": "Un tipo de interfaz"}, "ans": "B"}
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
        return random.sample(self.cuestionario, k)

    def inyectar_secreto(self, nombre: str, valor: str):
        """Usa el DatabaseManager para cifrar y guardar con GHOST_SHELL."""
        try:
            db.save_secret(nombre, valor)
            return True
        except Exception as e:
            logger.error(f"Fallo al inyectar secreto {nombre}: {e}")
            return False
    
    def finalizar_fase_dos(self):
        """Eleva el rango del usuario y prepara el sellado de la Master Key."""
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            if user:
                user.rango = "Shadow_Coder"
                user.pruebas_completadas = True
                session.commit()
                logger.success("🏆 SAP: Evaluación técnica superada. Rango: Shadow_Coder.")
        except Exception as e:
            session.rollback()
            logger.error(f"Error al finalizar Fase 2: {e}")
        finally:
            session.close()

    def sellar_master_key(self, raw_key: str):
        """Sella la llave definitiva en la base de datos."""
        from src.logic.identity_matrix import sap
        session = db.get_session()
        try:
            user = session.query(Usuario).first()
            if user:
                user.master_key_hash = sap.generar_master_hash(raw_key)
                session.commit()
                logger.success("🔐 SAP: Master Key sellada criptográficamente.")
                return True
        except Exception as e:
            session.rollback()
            logger.error(f"Error al sellar Master Key: {e}")
        finally:
            session.close()
        return False

trials_v2_logic = PhaseTwoManager()
