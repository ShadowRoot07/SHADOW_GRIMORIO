from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Rango(Base):
    __tablename__ = "rangos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    nivel_acceso = Column(Integer, default=1)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    usuarios = relationship("Usuario", back_populates="rango_rel")

# src/database/models.py

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    alias = Column(String(50), default="ShadowRoot07")
    rango_id = Column(Integer, ForeignKey("rangos.id"))
    pruebas_completadas = Column(Boolean, default=False)
    master_key_hash = Column(String(255), nullable=True)
    progreso_trials = Column(String, default="F1_S1_P0")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    rango_rel = relationship("Rango", back_populates="usuarios")
    dispositivos = relationship("Dispositivo", back_populates="usuario")
    preferencias = relationship("Preferencia", back_populates="usuario", uselist=False)
    conocimientos = relationship("Conocimiento", back_populates="usuario")



class Conocimiento(Base):
    __tablename__ = "conocimientos"
    id = Column(Integer, primary_key=True)
    categoria = Column(String, default="GENERAL") # Ej: "PERSONAL", "STACK", "PREFERENCIA"
    llave = Column(String)    # Ej: "lenguaje_favorito"
    valor = Column(Text)      # Ej: "Python"
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    usuario = relationship("Usuario", back_populates="conocimientos")

class Dispositivo(Base):
    __tablename__ = "dispositivos"
    id = Column(Integer, primary_key=True)
    hw_fingerprint = Column(String, unique=True, nullable=False)
    nombre_modelo = Column(String, default="ZTE Blade A54")
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    usuario = relationship("Usuario", back_populates="dispositivos")

class Preferencia(Base):
    __tablename__ = "preferencias"
    id = Column(Integer, primary_key=True)
    tema = Column(String, default="CYBERPUNK")
    idioma = Column(String, default="ES")
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    usuario = relationship("Usuario", back_populates="preferencias")

class Proveedor(Base):
    """3FN: Entidad para servicios externos."""
    __tablename__ = "proveedores"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False) # Ej: "GROQ"
    secretos = relationship("Secreto", back_populates="proveedor")

# --- BUSCA ESTA PARTE EN src/database/models.py Y REEMPLÁZALA ---

class Secreto(Base):
    """3FN: Bóveda vinculada a proveedores."""
    __tablename__ = "secretos"
    id = Column(Integer, primary_key=True)
    nombre_llave = Column(String, nullable=False) # Ej: "PRIMARY_TOKEN"
    valor_cifrado = Column(Text, nullable=False)
    
    # ESTA ES LA COLUMNA CRÍTICA QUE ESTÁ CAUSANDO EL ERROR
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"))
    
    # Marcador de tiempo para el SyncEngine
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # RELACIONES
    proveedor = relationship("Proveedor", back_populates="secretos")


class Proyecto(Base):
    """Representa un repositorio o directorio de trabajo gestionado."""
    __tablename__ = "proyectos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    path_local = Column(String, nullable=False)
    rama_actual = Column(String, default="main")
    last_sync = Column(DateTime, server_default=func.now())
    
    # Relación con sus hitos
    hitos = relationship("HitoHistorial", back_populates="proyecto", cascade="all, delete-orphan")

class HitoHistorial(Base):
    """Instante congelado de un proyecto: Código + Contexto IA."""
    __tablename__ = "hitos_historial"
    id = Column(Integer, primary_key=True)
    proyecto_id = Column(Integer, ForeignKey("proyectos.id"))
    
    # Datos de Git
    commit_hash = Column(String(40), nullable=False)
    mensaje_commit = Column(Text)
    
    # Datos del Oráculo
    prompt_usuario = Column(Text)
    respuesta_ia = Column(Text)
    
    # Contexto técnico organizado (JSON para flexibilidad)
    # Aquí guardaremos el orden de directorios y detalles del stack
    contexto_tecnico = Column(Text) 
    
    fecha = Column(DateTime, server_default=func.now())
    
    proyecto = relationship("Proyecto", back_populates="hitos")

