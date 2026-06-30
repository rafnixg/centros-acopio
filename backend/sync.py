"""Sincronización de centros desde múltiples fuentes remotas (JSON + CSV)."""
import csv
import io
import json
import logging
import unicodedata
from datetime import datetime, timezone
from typing import Optional

import httpx
from sqlalchemy.orm import Session

from database import SessionLocal
from models import CentroAcopio

logger = logging.getLogger(__name__)

JSON_DATA_URL = "https://www.centrosdeacopiovzla.com/data.json"
CSV_DATA_URL = "https://ayudaparavenezuela.com/api/public/centers/csv"
SOURCE_JSON = "centrosdeacopiovzla.com"
SOURCE_CSV = "ayudaparavenezuela.com"

# Estados venezolanos para inferir pais
ESTADOS_VENEZUELA = [
    "Amazonas", "Anzoátegui", "Apure", "Aragua", "Barinas", "Bolívar",
    "Carabobo", "Cojedes", "Delta Amacuro", "Distrito Capital", "Falcón",
    "Guárico", "Lara", "La Guaira", "Mérida", "Miranda", "Monagas",
    "Nueva Esparta", "Portuguesa", "Sucre", "Táchira", "Trujillo",
    "Yaracuy", "Zulia"
]

# Mapeo de productos del JSON actual
PRODUCT_MAP_JSON = {
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

# Mapeo de productos del CSV de Ayuda para Venezuela
PRODUCT_MAP_CSV = {
    "agua": "Agua potable / embotellada",
    "alimentos": "Alimentos no perecederos",
    "medicinas": "Botiquín / primeros auxilios",
    "higiene": "Artículos de higiene personal",
    "ropa": "Ropa / frazadas / calzado",
    "bebes": "Leche / fórmula infantil / pañales",
    "mascotas": "Comida para mascotas",
    "herramientas": "Otros",
    "juguetes_educativo": "Otros",
    "otros": "Otros",
}


def map_productos(recibe_list: Optional[list]) -> str:
    """Convierte la lista de productos del JSON actual a JSON string."""
    if not recibe_list:
        return "[]"
    mapped = set()
    for p in recibe_list:
        p_lower = str(p).lower().strip()
        mapped.add(PRODUCT_MAP_JSON.get(p_lower, "Otros"))
    return json.dumps(sorted(mapped), ensure_ascii=False)


def map_productos_csv(supply_types: str) -> str:
    """Convierte supply_types (separado por '|') del CSV a JSON string interno."""
    if not supply_types:
        return "[]"
    mapped = set()
    for item in supply_types.split("|"):
        key = normalize_text(item)
        mapped.add(PRODUCT_MAP_CSV.get(key, "Otros"))
    return json.dumps(sorted(mapped), ensure_ascii=False)


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


def normalize_text(value: Optional[str]) -> str:
    """Normaliza texto para comparaciones canónicas entre fuentes."""
    if value is None:
        return ""
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(text.strip().lower().split())


def as_float(value) -> Optional[float]:
    """Convierte valores numéricos a float de forma segura."""
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def bool_from_str(value, default: bool = True) -> bool:
    """Parsea booleanos comunes desde CSV/API."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    normalized = normalize_text(str(value))
    if normalized in {"true", "1", "si", "sí", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    return default


def canonical_key(record: dict) -> tuple[str, str, str, str]:
    """Clave textual canónica para deduplicación."""
    return (
        normalize_text(record.get("nombre")),
        normalize_text(record.get("pais")),
        normalize_text(record.get("estado")),
        normalize_text(record.get("ciudad")),
    )


def canonical_coord_key(record: dict) -> Optional[tuple[str, str, float, float]]:
    """Clave alternativa por ubicación aproximada (cuando hay coordenadas)."""
    lat = record.get("latitud")
    lon = record.get("longitud")
    if lat is None or lon is None:
        return None
    return (
        normalize_text(record.get("estado")),
        normalize_text(record.get("ciudad")),
        round(float(lat), 4),
        round(float(lon), 4),
    )


def _parse_productos(productos_json: Optional[str]) -> list[str]:
    if not productos_json:
        return []
    try:
        parsed = json.loads(productos_json)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def merge_record_data(target: dict, incoming: dict) -> bool:
    """Mezcla datos de forma conservadora para enriquecer un centro sin degradar información."""
    changed = False

    # Unir productos (si existen en ambos) en lugar de sobreescribir.
    target_products = set(_parse_productos(target.get("productos")))
    incoming_products = set(_parse_productos(incoming.get("productos")))
    union_products = sorted(target_products | incoming_products)
    merged_productos = json.dumps(union_products, ensure_ascii=False)
    if merged_productos != target.get("productos"):
        target["productos"] = merged_productos
        changed = True

    for key in ("direccion", "telefono", "responsable", "horarios", "latitud", "longitud"):
        current = target.get(key)
        new_value = incoming.get(key)
        if new_value in (None, ""):
            continue
        if current in (None, ""):
            target[key] = new_value
            changed = True

    if target.get("estado_centro") == "Activo" and incoming.get("estado_centro") in {"Pausado", "Lleno", "Cerrado"}:
        target["estado_centro"] = incoming.get("estado_centro")
        changed = True

    if incoming.get("activo") is False and target.get("activo") is True:
        target["activo"] = False
        changed = True

    incoming_notes = (incoming.get("notas") or "").strip()
    target_notes = (target.get("notas") or "").strip()
    if incoming_notes and incoming_notes not in target_notes:
        target["notas"] = f"{target_notes} | {incoming_notes}".strip(" |")
        changed = True

    return changed


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

                centros.append({
                    "nombre": (c.get("nombre") or "").strip(),
                    "pais": "Venezuela" if estado_nombre in ESTADOS_VENEZUELA else estado_nombre,
                    "estado": estado_nombre,
                    "ciudad": ciudad_nombre,
                    "direccion": (c.get("direccion") or "").strip(),
                    "telefono": str(telefono) if telefono else "",
                    "responsable": c.get("fuente", SOURCE_JSON),
                    "horarios": horarios,
                    "productos": map_productos(recibe),
                    "activo": True,
                    "estado_centro": get_estado_centro(notas),
                    "notas": f"Fuente: {SOURCE_JSON}. {notas}".strip(),
                    "latitud": as_float(coords[0]) if coords else None,
                    "longitud": as_float(coords[1]) if coords else None,
                })
    return centros


def extract_centros_from_csv(csv_text: str) -> list[dict]:
    """Extrae centros desde el CSV público de ayudaparavenezuela.com."""
    centros = []
    reader = csv.DictReader(io.StringIO(csv_text))
    for row in reader:
        activo = bool_from_str(row.get("is_active"), default=True)
        notes = (row.get("notes") or "").strip()
        centros.append({
            "nombre": (row.get("name") or "").strip(),
            "pais": (row.get("country") or "Venezuela").strip() or "Venezuela",
            "estado": (row.get("state") or "").strip(),
            "ciudad": (row.get("city") or "").strip(),
            "direccion": (row.get("address") or "").strip(),
            "telefono": (row.get("phone") or "").strip(),
            "responsable": (row.get("organization") or SOURCE_CSV).strip() or SOURCE_CSV,
            "horarios": (row.get("schedule") or "").strip(),
            "productos": map_productos_csv(row.get("supply_types") or ""),
            "activo": activo,
            "estado_centro": "Activo" if activo else "Pausado",
            "notas": f"Fuente: {SOURCE_CSV}. {notes}".strip(),
            "latitud": as_float(row.get("latitude")),
            "longitud": as_float(row.get("longitude")),
        })
    return centros


def deduplicate_records(centros_json: list[dict], centros_csv: list[dict]) -> tuple[list[dict], int]:
    """Consolida registros JSON+CSV, evitando duplicados inter-fuente."""
    merged: list[dict] = []
    text_index: dict[tuple[str, str, str, str], dict] = {}
    coord_index: dict[tuple[str, str, float, float], dict] = {}
    duplicates = 0

    for record in centros_json + centros_csv:
        text_key = canonical_key(record)
        coord_key = canonical_coord_key(record)
        existing = text_index.get(text_key) or (coord_index.get(coord_key) if coord_key else None)
        if existing:
            merge_record_data(existing, record)
            duplicates += 1
            continue

        record_copy = dict(record)
        merged.append(record_copy)
        text_index[text_key] = record_copy
        if coord_key:
            coord_index[coord_key] = record_copy

    return merged, duplicates


def sync_from_remote(db: Session) -> dict:
    """Obtiene datos remotos (JSON + CSV) y sincroniza con la BD."""
    fuentes = {
        "json": {"url": JSON_DATA_URL, "total": 0, "error": None},
        "csv": {"url": CSV_DATA_URL, "total": 0, "error": None},
    }

    centros_json: list[dict] = []
    centros_csv: list[dict] = []

    try:
        resp_json = httpx.get(JSON_DATA_URL, timeout=30)
        resp_json.raise_for_status()
        centros_json = extract_centros_from_json(resp_json.json())
        fuentes["json"]["total"] = len(centros_json)
    except Exception as e:
        fuentes["json"]["error"] = str(e)
        logger.error(f"Error fetching {JSON_DATA_URL}: {e}")

    try:
        resp_csv = httpx.get(CSV_DATA_URL, timeout=30)
        resp_csv.raise_for_status()
        centros_csv = extract_centros_from_csv(resp_csv.text)
        fuentes["csv"]["total"] = len(centros_csv)
    except Exception as e:
        fuentes["csv"]["error"] = str(e)
        logger.error(f"Error fetching {CSV_DATA_URL}: {e}")

    if not centros_json and not centros_csv:
        return {
            "error": "No se pudo obtener datos de ninguna fuente",
            "insertados": 0,
            "actualizados": 0,
            "total": 0,
            "duplicados_omitidos": 0,
            "fuentes": fuentes,
        }

    centros_unificados, duplicados_interfuente = deduplicate_records(centros_json, centros_csv)
    total = len(centros_unificados)
    insertados = 0
    actualizados = 0
    duplicados_omitidos = duplicados_interfuente

    existentes = db.query(CentroAcopio).all()
    existing_by_text: dict[tuple[str, str, str, str], CentroAcopio] = {}
    existing_by_coords: dict[tuple[str, str, float, float], CentroAcopio] = {}
    for existente in existentes:
        record = {
            "nombre": existente.nombre,
            "pais": existente.pais,
            "estado": existente.estado,
            "ciudad": existente.ciudad,
            "latitud": existente.latitud,
            "longitud": existente.longitud,
        }
        existing_by_text[canonical_key(record)] = existente
        coord_key = canonical_coord_key(record)
        if coord_key:
            existing_by_coords[coord_key] = existente

    for cr in centros_unificados:
        text_key = canonical_key(cr)
        coord_key = canonical_coord_key(cr)
        existente = existing_by_text.get(text_key) or (existing_by_coords.get(coord_key) if coord_key else None)

        if existente:
            duplicados_omitidos += 1
            current_record = {
                "direccion": existente.direccion,
                "telefono": existente.telefono,
                "responsable": existente.responsable,
                "horarios": existente.horarios,
                "productos": existente.productos,
                "activo": existente.activo,
                "estado_centro": existente.estado_centro,
                "notas": existente.notas,
                "latitud": existente.latitud,
                "longitud": existente.longitud,
            }
            if merge_record_data(current_record, cr):
                for key, value in current_record.items():
                    setattr(existente, key, value)
                existente.ultima_actualizacion = datetime.now(timezone.utc)
                actualizados += 1
            continue

        nuevo = CentroAcopio(**cr)
        db.add(nuevo)
        insertados += 1

    db.commit()
    logger.info(
        "Sync completado: %s insertados, %s actualizados, %s duplicados omitidos, %s unificados",
        insertados,
        actualizados,
        duplicados_omitidos,
        total,
    )
    return {
        "insertados": insertados,
        "actualizados": actualizados,
        "total": total,
        "duplicados_omitidos": duplicados_omitidos,
        "fuentes": fuentes,
    }


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