from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CentroAcopioBase(BaseModel):
    nombre: str
    estado: str
    ciudad: str
    direccion: str
    telefono: str
    responsable: str
    horarios: Optional[str] = ""
    productos: Optional[str] = "[]"
    activo: bool = True
    estado_centro: str = "Activo"
    email: Optional[str] = ""
    redes: Optional[str] = ""
    foto_url: Optional[str] = ""
    notas: Optional[str] = ""
    latitud: Optional[float] = None
    longitud: Optional[float] = None


class CentroAcopioCreate(CentroAcopioBase):
    pass


class CentroAcopioUpdate(BaseModel):
    nombre: Optional[str] = None
    estado: Optional[str] = None
    ciudad: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    responsable: Optional[str] = None
    horarios: Optional[str] = None
    productos: Optional[str] = None
    activo: Optional[bool] = None
    estado_centro: Optional[str] = None
    email: Optional[str] = None
    redes: Optional[str] = None
    foto_url: Optional[str] = None
    notas: Optional[str] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None


class CentroAcopioResponse(CentroAcopioBase):
    id: int
    fecha_registro: datetime
    ultima_actualizacion: datetime

    class Config:
        from_attributes = True
