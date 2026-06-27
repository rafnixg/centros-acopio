from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from database import Base


class CentroAcopio(Base):
    __tablename__ = "centros_acopio"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(200), nullable=False, index=True)
    estado = Column(String(50), nullable=False, index=True)
    ciudad = Column(String(100), nullable=False)
    direccion = Column(Text, nullable=False)
    telefono = Column(String(100), nullable=False)
    responsable = Column(String(200), nullable=False)
    horarios = Column(String(200), nullable=True)
    productos = Column(Text, nullable=True)  # JSON array string
    activo = Column(Boolean, default=True)
    estado_centro = Column(String(20), default="Activo")  # Activo, Pausado, Lleno, Cerrado
    email = Column(String(100), nullable=True)
    redes = Column(String(300), nullable=True)
    foto_url = Column(String(500), nullable=True)
    notas = Column(Text, nullable=True)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    fecha_registro = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ultima_actualizacion = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
