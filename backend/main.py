import json
import os
from fastapi import FastAPI, Depends, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, get_db, Base
from models import CentroAcopio
from schemas import CentroAcopioCreate, CentroAcopioUpdate, CentroAcopioResponse

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Centros de Acopio Venezuela", description="Directorio nacional de centros de acopio")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
app.mount("/static", StaticFiles(directory=static_path), name="static")

# Templates con filtros personalizados
templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
templates = Jinja2Templates(directory=templates_path)


def from_json_filter(s):
    """Convierte un string JSON a un objeto Python."""
    try:
        return json.loads(s) if s else []
    except (json.JSONDecodeError, TypeError):
        return []


templates.env.filters["from_json"] = from_json_filter

# ---------------------------------------------------------------------------
# ESTADOS DE VENEZUELA
# ---------------------------------------------------------------------------
ESTADOS_VENEZUELA = [
    "Amazonas", "Anzoátegui", "Apure", "Aragua", "Barinas", "Bolívar",
    "Carabobo", "Cojedes", "Delta Amacuro", "Distrito Capital", "Falcón",
    "Guárico", "Lara", "La Guaira", "Mérida", "Miranda", "Monagas",
    "Nueva Esparta", "Portuguesa", "Sucre", "Táchira", "Trujillo",
    "Yaracuy", "Zulia"
]

PRODUCTOS_DISPONIBLES = [
    "Alimentos no perecederos",
    "Agua potable / embotellada",
    "Artículos de higiene personal",
    "Botiquín / primeros auxilios",
    "Productos de limpieza",
    "Ropa / frazadas / calzado",
    "Leche / fórmula infantil / pañales",
    "Comida para mascotas",
    "Otros",
]


# ---------------------------------------------------------------------------
# RUTAS DE TEMPLATES (HTML)
# ---------------------------------------------------------------------------
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "estados": ESTADOS_VENEZUELA, "productos": PRODUCTOS_DISPONIBLES},
    )


@app.get("/registrar")
def registrar(request: Request):
    return templates.TemplateResponse(
        "registro.html",
        {"request": request, "estados": ESTADOS_VENEZUELA, "productos": PRODUCTOS_DISPONIBLES},
    )


@app.get("/centro/{centro_id}")
def detalle_centro(request: Request, centro_id: int, db: Session = Depends(get_db)):
    centro = db.query(CentroAcopio).filter(CentroAcopio.id == centro_id).first()
    if not centro:
        raise HTTPException(status_code=404, detail="Centro no encontrado")
    return templates.TemplateResponse(
        "detalle.html",
        {"request": request, "centro": centro, "estados": ESTADOS_VENEZUELA},
    )


# ---------------------------------------------------------------------------
# API REST
# ---------------------------------------------------------------------------
@app.get("/api/centros", response_model=list[CentroAcopioResponse])
def listar_centros(
    db: Session = Depends(get_db),
    q: str = Query("", description="Búsqueda por nombre, ciudad o dirección"),
    estado: str = Query("", description="Filtrar por estado"),
    producto: str = Query("", description="Filtrar por tipo de producto"),
    estado_centro: str = Query("", description="Filtrar por estado del centro (Activo/Pausado/Lleno/Cerrado)"),
    activo: bool = Query(None, description="Filtrar por activo/inactivo"),
):
    query = db.query(CentroAcopio)

    if q:
        like = f"%{q}%"
        query = query.filter(
            CentroAcopio.nombre.ilike(like)
            | CentroAcopio.ciudad.ilike(like)
            | CentroAcopio.direccion.ilike(like)
        )

    if estado:
        query = query.filter(CentroAcopio.estado == estado)

    if producto:
        query = query.filter(CentroAcopio.productos.ilike(f"%{producto}%"))

    if estado_centro:
        query = query.filter(CentroAcopio.estado_centro == estado_centro)

    if activo is not None:
        query = query.filter(CentroAcopio.activo == activo)

    centros = query.order_by(CentroAcopio.fecha_registro.desc()).all()
    return centros


@app.get("/api/centros/{centro_id}", response_model=CentroAcopioResponse)
def obtener_centro(centro_id: int, db: Session = Depends(get_db)):
    centro = db.query(CentroAcopio).filter(CentroAcopio.id == centro_id).first()
    if not centro:
        raise HTTPException(status_code=404, detail="Centro no encontrado")
    return centro


@app.post("/api/centros", response_model=CentroAcopioResponse, status_code=201)
def crear_centro(data: CentroAcopioCreate, db: Session = Depends(get_db)):
    centro = CentroAcopio(**data.model_dump())
    db.add(centro)
    db.commit()
    db.refresh(centro)
    return centro


@app.put("/api/centros/{centro_id}", response_model=CentroAcopioResponse)
def actualizar_centro(centro_id: int, data: CentroAcopioUpdate, db: Session = Depends(get_db)):
    centro = db.query(CentroAcopio).filter(CentroAcopio.id == centro_id).first()
    if not centro:
        raise HTTPException(status_code=404, detail="Centro no encontrado")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(centro, key, value)

    db.commit()
    db.refresh(centro)
    return centro


@app.delete("/api/centros/{centro_id}", status_code=204)
def eliminar_centro(centro_id: int, db: Session = Depends(get_db)):
    centro = db.query(CentroAcopio).filter(CentroAcopio.id == centro_id).first()
    if not centro:
        raise HTTPException(status_code=404, detail="Centro no encontrado")
    db.delete(centro)
    db.commit()
    return None


@app.get("/api/estados")
def listar_estados():
    return ESTADOS_VENEZUELA


@app.get("/api/estadisticas")
def estadisticas(db: Session = Depends(get_db)):
    total = db.query(func.count(CentroAcopio.id)).scalar()
    por_estado = (
        db.query(CentroAcopio.estado, func.count(CentroAcopio.id))
        .group_by(CentroAcopio.estado)
        .all()
    )
    por_estado_centro = (
        db.query(CentroAcopio.estado_centro, func.count(CentroAcopio.id))
        .group_by(CentroAcopio.estado_centro)
        .all()
    )
    return {
        "total": total,
        "por_estado": {e: c for e, c in por_estado},
        "por_estado_centro": {e: c for e, c in por_estado_centro},
    }
