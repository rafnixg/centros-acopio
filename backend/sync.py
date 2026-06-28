"""
Tarea de sincronización: importa centros desde centrosdeacopiovzla.com/data.json
Se ejecuta cada hora (vía APScheduler o llamada manual desde el panel admin).
Compara por nombre+ciudad+estado y solo inserta/actualiza cambios detectados.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from database import SessionLocal
from models import CentroAcopio

logger = logging.getLogger(__name__)

DATA_URL = "https://www.centrosdeacopiovzla.com/data.json"
SOURCE_NAME = "centrosdeacopiovzla.com"

# Estados venezolanos para inferir pais
ESTADOS_VENEZUELA = [
    "Amazonas", "Anzoátegui", "Apure", "Aragua", "Barinas", "Bolívar",
    "Carabobo", "Cojedes", "Delta Amacuro", "Distrito Capital", "Falcón",
    "Guárico", "Lara", "La Guaira", "Mérida", "Miranda", "Monagas",
    "Nueva Esparta", "Portuguesa", "Sucre", "Táchira", "Trujillo",
    "Yaracuy", "Zulia"
]

# Mapeo de productos del JSON a nuestros productos
PRODUCT_MAP = {
    "agua potable": "Agua potable / embotellada",
    "alimentos no perecederos": "Alimentos no perecederos",
    "medicamentos e insumos médicos": "Botiquín / primeros auxilios",
    "kits de primeros auxilios": "Botiquín / primeros auxilios",
    "mantas y cobijas": "Ropa / frazadas / calzado",
    "ropa en buen estado": "Ropa / frazadas / calzado",
    "artículos de higiene personal": "Artículos de higiene personal",
    "abrigos y otros implementos de protección": "Ropa / frazadas / calzado",
    "cascos de protección": "Otros",
    "pañales de bebé": "Leche / fórmula infantil / pañales",
    "pañales de adulto": "Leche / fórmula infantil / pañales",
    "artículos para niños": "Leche / fórmula infantil / pañales",
    "artículos de limpieza": "Productos de limpieza",
    "materiales para refugio": "Otros",
    "linternas, pilas y cargadores portátiles": "Otros",
    "colchones, almohadas y colchones inflables": "Ropa / frazadas / calzado",
    "alimentos para mascotas": "Comida para mascotas",
}


def map_productos(recibe_list: Optional[list]) -> str:
    """Convierte la lista de productos del JSON a nuestro formato JSON string."""
    if not recibe_list:
        return "[]"
    mapped = set()
    for p in recibe_list:
        p_lower = p.lower().strip()
        if p_lower in PRODUCT_MAP:
            mapped.add(PRODUCT_MAP[p_lower])
        else:
            mapped.add("Otros")
    return json.dumps(sorted(mapped))


def get_estado_centro(nota: Optional[str]) -> str:
    """Intenta inferir el estado del centro desde la nota."""
    if not nota:
        return "Activo"
    nota_lower = nota.lower()
    if "cerrado" in nota_lower or "no recibe" in nota_lower:
        return "Cerrado"
    if "lleno" in nota_lower or "completo" in nota_lower or "capacidad" in nota_lower:
        return "Lleno"
    if "pausado" in nota_lower or "temporal" in nota_lower:
        return "Pausado"
    return "Activo"


def extract_centros_from_json(data: dict) -> list[dict]:
    """Extrae todos los centros del JSON anidado de centrosdeacopiovzla.com."""
    centros = []
    estados = data.get("estados", [])
    for estado_entry in estados:
        estado_nombre = estado_entry.get("nombre", "")
        ciudades = estado_entry.get("ciudades", [])
        for ciudad_entry in ciudades:
            ciudad_nombre = ciudad_entry.get("nombre", "")
            centros_list = ciudad_entry.get("centros", [])
            for c in centros_list:
                coords = c.get("coords", [None, None])
                telefono = c.get("telefono") or c.get("whatsapp") or c.get("contacto", "")
                if telefono and isinstance(telefono, str) and telefono.startswith("+"):
                    telefono = telefono.lstrip("+")
                horarios = c.get("horario", "")
                recibe = c.get("recibe", [])
                notas = c.get("nota", "")
                productos = map_productos(recibe)

                centros.append({
                    "nombre": c.get("nombre", "").strip(),
                    "pais": "Venezuela" if estado_nombre in ESTADOS_VENEZUELA else estado_nombre,
                    "estado": estado_nombre,
                    "ciudad": ciudad_nombre,
                    "direccion": c.get("direccion", "").strip(),
                    "telefono": str(telefono) if telefono else "",
                    "responsable": c.get("fuente", SOURCE_NAME),
                    "horarios": horarios,
                    "productos": productos,
                    "activo": True,
                    "estado_centro": get_estado_centro(notas),
                    "notas": f"Fuente: {c.get('fuente', SOURCE_NAME)}. {notas}".strip(),
                    "latitud": float(coords[0]) if coords and coords[0] else None,
                    "longitud": float(coords[1]) if coords and coords[1] else None,
                })
    return centros


def sync_from_remote(db: Session) -> dict:
    """
    Obtiene datos del JSON remoto y sincroniza con nuestra BD.
    Retorna un resumen de lo que hizo.
    """
    try:
        resp = httpx.get(DATA_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error(f"Error fetching {DATA_URL}: {e}")
        return {"error": str(e), "insertados": 0, "actualizados": 0, "total": 0}

    centros_remotos = extract_centros_from_json(data)
    total = len(centros_remotos)
    insertados = 0
    actualizados = 0

    for cr in centros_remotos:
        # Buscar si ya existe por nombre+ciudad+estado
        existente = (
            db.query(CentroAcopio)
            .filter(
                CentroAcopio.nombre == cr["nombre"],
                CentroAcopio.ciudad == cr["ciudad"],
                CentroAcopio.estado == cr["estado"],
            )
            .first()
        )

        if existente:
            # Actualizar solo si hay cambios
            cambios = False
            for key in ("direccion", "telefono", "horarios", "productos",
                        "estado_centro", "notas", "latitud", "longitud"):
                nuevo_valor = cr.get(key)
                old_valor = getattr(existente, key, None)
                if nuevo_valor != old_valor and nuevo_valor is not None and str(nuevo_valor).strip():
                    setattr(existente, key, nuevo_valor)
                    cambios = True
            if cambios:
                existente.ultima_actualizacion = datetime.now(timezone.utc)
                actualizados += 1
        else:
            # Insertar nuevo
            nuevo = CentroAcopio(**cr)
            db.add(nuevo)
            insertados += 1

    db.commit()
    logger.info(f"Sync completado: {insertados} insertados, {actualizados} actualizados de {total} remotos")
    return {"insertados": insertados, "actualizados": actualizados, "total": total}


def sync_job():
    """Wrapper para ejecutar desde el scheduler sin dependencia de BD."""
    db = SessionLocal()
    try:
        return sync_from_remote(db)
    finally:
        db.close()


if __name__ == "__main__":
    # Ejecución directa: python -m backend.sync
    logging.basicConfig(level=logging.INFO)
    result = sync_job()
    print(json.dumps(result, indent=2))