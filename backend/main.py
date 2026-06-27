import json
import os
import httpx
from fastapi import FastAPI, Depends, HTTPException, Query, Request, Form, Cookie
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, get_db, Base
from models import CentroAcopio, ReporteActualizacion
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
# ADMIN TOKEN (simple, configurable vía variable de entorno)
# ---------------------------------------------------------------------------
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "admin123")


def verify_admin(token: str = Cookie(None)):
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="No autorizado")
    return True


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
def landing(request: Request, db: Session = Depends(get_db)):
    """Landing page informativa estilo ayudavenezuela.venevision.com"""
    total = db.query(func.count(CentroAcopio.id)).scalar()
    activos = db.query(CentroAcopio).filter(CentroAcopio.estado_centro == "Activo").count()
    centros_recientes = (
        db.query(CentroAcopio)
        .order_by(CentroAcopio.fecha_registro.desc())
        .limit(3)
        .all()
    )
    return templates.TemplateResponse(
        "landing.html",
        {
            "request": request,
            "total": total,
            "activos": activos,
            "centros_recientes": centros_recientes,
            "estados": ESTADOS_VENEZUELA,
        },
    )


@app.get("/centros")
def centros_directory(request: Request):
    """Directorio completo de centros de acopio (antes index)"""
    return templates.TemplateResponse(
        "centros.html",
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
    reportes = db.query(ReporteActualizacion).filter(
        ReporteActualizacion.centro_id == centro_id
    ).order_by(ReporteActualizacion.fecha.desc()).all()
    return templates.TemplateResponse(
        "detalle.html",
        {
            "request": request,
            "centro": centro,
            "reportes": reportes,
            "estados": ESTADOS_VENEZUELA,
        },
    )


@app.get("/admin/login")
def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.get("/admin")
def admin_panel(
    request: Request,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin),
):
    centros = db.query(CentroAcopio).order_by(CentroAcopio.fecha_registro.desc()).all()
    reportes = db.query(ReporteActualizacion).order_by(ReporteActualizacion.fecha.desc()).limit(20).all()
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "centros": centros, "reportes": reportes, "estados": ESTADOS_VENEZUELA},
    )


@app.get("/admin/editar/{centro_id}")
def admin_editar(
    request: Request,
    centro_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin),
):
    centro = db.query(CentroAcopio).filter(CentroAcopio.id == centro_id).first()
    if not centro:
        raise HTTPException(status_code=404, detail="Centro no encontrado")
    return templates.TemplateResponse(
        "admin_editar.html",
        {"request": request, "centro": centro, "estados": ESTADOS_VENEZUELA, "productos": PRODUCTOS_DISPONIBLES},
    )


@app.get("/estadisticas")
def stats_page(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        "estadisticas.html",
        {"request": request, "estados": ESTADOS_VENEZUELA, "productos": PRODUCTOS_DISPONIBLES},
    )


@app.post("/admin/login")
def admin_login(password: str = Form(...)):
    if password == ADMIN_TOKEN:
        resp = RedirectResponse(url="/admin", status_code=302)
        resp.set_cookie(key="token", value=ADMIN_TOKEN, httponly=True, max_age=86400 * 7)
        return resp
    return templates.TemplateResponse(
        "admin_login.html",
        {"request": {}, "error": "Contraseña incorrecta"},
    )


@app.post("/admin/logout")
def admin_logout():
    resp = RedirectResponse(url="/", status_code=302)
    resp.delete_cookie("token")
    return resp


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
def actualizar_centro(
    centro_id: int,
    data: CentroAcopioUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin),
):
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
def eliminar_centro(
    centro_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_admin),
):
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
    # Productos más solicitados
    por_producto = db.query(CentroAcopio.productos).all()
    productos_count = {}
    for (p_str,) in por_producto:
        if p_str:
            try:
                for p in json.loads(p_str):
                    productos_count[p] = productos_count.get(p, 0) + 1
            except:
                pass

    # Centros recién registrados
    centros_recientes = (
        db.query(CentroAcopio)
        .order_by(CentroAcopio.fecha_registro.desc())
        .limit(5)
        .all()
    )

    # Reportes pendientes
    total_reportes = db.query(func.count(ReporteActualizacion.id)).scalar()

    return {
        "total": total,
        "por_estado": {e: c for e, c in por_estado},
        "por_estado_centro": {e: c for e, c in por_estado_centro},
        "por_producto": dict(sorted(productos_count.items(), key=lambda x: -x[1])),
        "recientes": [
            {"id": c.id, "nombre": c.nombre, "ciudad": c.ciudad, "estado": c.estado}
            for c in centros_recientes
        ],
        "total_reportes": total_reportes,
    }


# ---------------------------------------------------------------------------
# GEOCODIFICACIÓN AUTOMÁTICA (Nominatim)
# ---------------------------------------------------------------------------
@app.post("/api/geocodificar")
async def geocodificar(data: dict):
    direccion = data.get("direccion", "")
    ciudad = data.get("ciudad", "")
    estado = data.get("estado", "")

    query = f"{direccion}, {ciudad}, {estado}, Venezuela"

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": query, "format": "json", "limit": 1},
                headers={"User-Agent": "CentrosAcopioVE/1.0"},
                timeout=10,
            )
            results = resp.json()
            if results:
                return {"latitud": float(results[0]["lat"]), "longitud": float(results[0]["lon"])}
        except Exception:
            pass

    return {"latitud": None, "longitud": None}


# ---------------------------------------------------------------------------
# REPORTES DE ACTUALIZACIÓN (ciudadanos reportan cambios)
# ---------------------------------------------------------------------------
@app.get("/api/reportes/{centro_id}")
def listar_reportes(centro_id: int, db: Session = Depends(get_db)):
    reportes = db.query(ReporteActualizacion).filter(
        ReporteActualizacion.centro_id == centro_id
    ).order_by(ReporteActualizacion.fecha.desc()).all()
    return [
        {
            "id": r.id,
            "nombre_reportador": r.nombre_reportador,
            "mensaje": r.mensaje,
            "fecha": r.fecha.isoformat(),
            "nuevo_estado": r.nuevo_estado,
        }
        for r in reportes
    ]


@app.post("/api/reportes")
def crear_reporte(data: dict, db: Session = Depends(get_db)):
    centro_id = data.get("centro_id")
    nombre = data.get("nombre_reportador", "Anónimo")
    mensaje = data.get("mensaje", "")
    nuevo_estado = data.get("nuevo_estado", "")

    if not centro_id:
        raise HTTPException(status_code=400, detail="centro_id requerido")

    centro = db.query(CentroAcopio).filter(CentroAcopio.id == centro_id).first()
    if not centro:
        raise HTTPException(status_code=404, detail="Centro no encontrado")

    reporte = ReporteActualizacion(
        centro_id=centro_id,
        nombre_reportador=nombre,
        mensaje=mensaje,
        nuevo_estado=nuevo_estado,
    )
    db.add(reporte)

    # Si reportaron un nuevo estado, actualizar el centro automáticamente
    if nuevo_estado and nuevo_estado in ("Activo", "Lleno", "Pausado", "Cerrado"):
        centro.estado_centro = nuevo_estado

    db.commit()
    db.refresh(reporte)
    return {"mensaje": "Reporte enviado", "id": reporte.id}
