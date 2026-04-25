from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Rango(Base):
    """3FN: Entidad de Autoridad."""
    __tablename__ = "rangos"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False) # Ej: "Shadow_Coder"
    nivel_acceso = Column(Integer, default=1)
    usuarios = relationship("Usuario", back_populates="rango_rel")

class Usuario(Base):
    """3FN: Entidad central sin dependencias transitivas."""
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    alias = Column(String, default="ShadowRoot07")
    rango_id = Column(Integer, ForeignKey("rangos.id"))
    pruebas_completadas = Column(Boolean, default=False)
    master_key_hash = Column(String, nullable=True)

    rango_rel = relationship("Rango", back_populates="usuarios")
    dispositivos = relationship("Dispositivo", back_populates="usuario")
    preferencias = relationship("Preferencia", back_populates="usuario", uselist=False)

class Dispositivo(Base):
    """3FN: Separación de hardware y usuario."""
    __tablename__ = "dispositivos"
    id = Column(Integer, primary_key=True)
    hw_fingerprint = Column(String, unique=True, nullable=False)
    nombre_modelo = Column(String, default="ZTE Blade A54")
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario", back_populates="dispositivos")

class Preferencia(Base):
    """3FN: Persistencia de configuración visual."""
    __tablename__ = "preferencias"
    id = Column(Integer, primary_key=True)
    tema = Column(String, default="CYBERPUNK")
    idioma = Column(String, default="ES")
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    usuario = relationship("Usuario", back_populates="preferencias")

class Proveedor(Base):
    """3FN: Entidad para servicios externos."""
    __tablename__ = "proveedores"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False) # Ej: "GROQ"
    secretos = relationship("Secreto", back_populates="proveedor")

class Secreto(Base):
    """3FN: Bóveda vinculada a proveedores."""
    __tablename__ = "secretos"
    id = Column(Integer, primary_key=True)
    nombre_llave = Column(String, nullable=False) # Ej: "PRIMARY_TOKEN"
    valor_cifrado = Column(Text, nullable=False)
    proveedor_id = Column(Integer, ForeignKey("proveedores.id"))
    proveedor = relationship("Proveedor", back_populates="secretos")

# Las tablas Conocimiento y Proyecto permanecen similares pero con integridad referencial si lo deseas
class Conocimiento(Base):
    __tablename__ = "conocimientos"
    id = Column(Integer, primary_key=True)
    tecnologia = Column(String, unique=True)
    nivel = Column(Integer, default=0)

