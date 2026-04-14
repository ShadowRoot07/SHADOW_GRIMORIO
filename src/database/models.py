from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Secreto(Base):
    """Bóveda cifrada para llaves de API y Tokens."""
    __tablename__ = "secretos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    valor_cifrado = Column(Text, nullable=False)

class Usuario(Base):
    """Perfil del programador con Protocolo SAP."""
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    alias = Column(String, default="ShadowRoot07")
    rango = Column(String, default="Iniciado") # Usado para trackear el sub-paso de la prueba
    
    # --- Protocolo de Acceso Shadow (SAP) ---
    pruebas_completadas = Column(Boolean, default=False)

    # Hashes de seguridad
    key_hash_1 = Column(String, nullable=True)
    key_hash_2 = Column(String, nullable=True)
    key_hash_3 = Column(String, nullable=True)

    # El sello final
    super_key_hash = Column(String, nullable=True)
    hw_fingerprint = Column(String, nullable=True)

class Conocimiento(Base):
    __tablename__ = "conocimientos"
    id = Column(Integer, primary_key=True)
    tecnologia = Column(String, unique=True)
    dominado = Column(Boolean, default=False)
    nivel = Column(Integer, default=0)

class Proyecto(Base):
    __tablename__ = "proyectos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    path_local = Column(String)
    repo_url = Column(String, nullable=True)
    descripcion = Column(Text)

