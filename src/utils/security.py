import hashlib
from src.utils.hardware import generar_huella_hardware

def verificar_integridad_clave(input_text: str, hash_esperado: str) -> bool:
    """Compara un texto con un hash sin revelar el contenido original."""
    return hashlib.sha256(input_text.encode()).hexdigest() == hash_esperado

def derivar_llave_sesion(clave_maestra: str) -> str:
    """Genera una llave temporal basada en el hardware y la maestra."""
    dna = generar_huella_hardware()
    seed = f"{clave_maestra}{dna[::-1]}".encode() # ADN invertido para extra ofuscación
    return hashlib.sha256(seed).hexdigest()[:32]

