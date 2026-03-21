from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Usuario(Base):
    """Perfil del programador (ShadowRoot07)."""
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    alias = Column(String, unique=True)
    rango = Column(String, default="Iniciado") # Para tu progreso

class Conocimiento(Base):
    """Tabla para recordar qué sabes y qué te falta aprender."""
    __tablename__ = "conocimientos"
    id = Column(Integer, primary_key=True)
    tecnologia = Column(String, unique=True) # Ej: 'JSON', 'FastAPI'
    dominado = Column(Boolean, default=False)
    nivel = Column(Integer, default=0) # 0 a 100

class Proyecto(Base):
    """Registro de tus rituales (proyectos de GitHub)."""
    __tablename__ = "proyectos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String)
    path_local = Column(String)
    repo_url = Column(String, nullable=True)
    descripcion = Column(Text)

