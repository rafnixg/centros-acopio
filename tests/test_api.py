"""Tests para la API de Centros de Acopio Venezuela."""
import json
import os
import sys
import tempfile

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

# -------------------------------------------------------------------
# Base de datos temporal para tests
# -------------------------------------------------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
Base.metadata.create_all(bind=engine_test)

client = TestClient(app)


# -------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------
@pytest.fixture(autouse=True)
def clean_db():
    """Limpia la BD antes de cada test."""
    for table in reversed(Base.metadata.sorted_tables):
        with engine_test.connect() as conn:
            conn.execute(table.delete())
            conn.commit()


def sample_centro():
    return {
        "nombre": "Centro Test",
        "pais": "Venezuela",
        "estado": "Distrito Capital",
        "ciudad": "Caracas",
        "direccion": "Av. Test, Edificio Test",
        "telefono": "0412-0000000",
        "responsable": "Test User",
        "horarios": "Lun-Vie 9:00-15:00",
        "productos": json.dumps(["Alimentos no perecederos", "Agua potable / embotellada"]),
        "activo": True,
        "estado_centro": "Activo",
        "latitud": 10.4806,
        "longitud": -66.9036,
    }


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------

class TestLandingPage:
    def test_landing_returns_200(self):
        """La landing page debe cargar correctamente."""
        resp = client.get("/")
        assert resp.status_code == 200
        assert "text/html" in resp.headers["content-type"]

    def test_landing_has_stats(self):
        """La landing debe mostrar estadísticas."""
        resp = client.get("/")
        html = resp.text.lower()
        assert "emergencia" in html
        assert "centros registrados" in html


class TestDirectorioPage:
    def test_centros_page_returns_200(self):
        """El directorio debe cargar."""
        resp = client.get("/centros")
        assert resp.status_code == 200

    def test_registrar_page_returns_200(self):
        """El formulario de registro debe cargar."""
        resp = client.get("/registrar")
        assert resp.status_code == 200

    def test_estadisticas_page_returns_200(self):
        """La página de estadísticas debe cargar."""
        resp = client.get("/estadisticas")
        assert resp.status_code == 200


class TestCentrosAPI:
    def test_listar_centros_vacio(self):
        """Al inicio no hay centros."""
        resp = client.get("/api/centros")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_crear_centro(self):
        """Crear un centro debe retornar 201."""
        data = sample_centro()
        resp = client.post("/api/centros", json=data)
        assert resp.status_code == 201
        body = resp.json()
        assert body["nombre"] == "Centro Test"
        assert body["id"] == 1

    def test_crear_centro_sin_requeridos(self):
        """Falta nombre debe dar 422."""
        resp = client.post("/api/centros", json={"estado": "Carabobo"})
        assert resp.status_code == 422

    def test_listar_centros_con_datos(self):
        """Listar debe retornar los centros creados."""
        client.post("/api/centros", json=sample_centro())
        resp = client.get("/api/centros")
        assert len(resp.json()) == 1

    def test_obtener_centro_por_id(self):
        """GET /api/centros/1 debe retornar el detalle."""
        client.post("/api/centros", json=sample_centro())
        resp = client.get("/api/centros/1")
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Centro Test"

    def test_obtener_centro_404(self):
        """Centro inexistente debe dar 404."""
        resp = client.get("/api/centros/999")
        assert resp.status_code == 404

    def test_eliminar_centro_sin_auth(self):
        """Eliminar sin cookie admin debe dar 401."""
        resp = client.delete("/api/centros/1")
        assert resp.status_code == 401

    def test_actualizar_centro_sin_auth(self):
        """Actualizar sin cookie admin debe dar 401."""
        resp = client.put("/api/centros/1", json={"nombre": "Nuevo"})
        assert resp.status_code == 401


class TestFiltros:
    def test_filtrar_por_estado(self):
        """Filtrar centros por estado."""
        c1 = sample_centro()
        c2 = sample_centro()
        c2["estado"] = "Carabobo"
        c2["ciudad"] = "Valencia"
        client.post("/api/centros", json=c1)
        client.post("/api/centros", json=c2)

        resp = client.get("/api/centros?estado=Carabobo")
        assert len(resp.json()) == 1
        assert resp.json()[0]["ciudad"] == "Valencia"

    def test_filtrar_por_producto(self):
        """Filtrar centros que reciben un producto."""
        c = sample_centro()
        c["productos"] = json.dumps(["Ropa / frazadas / calzado"])
        client.post("/api/centros", json=c)

        resp = client.get("/api/centros?producto=Ropa")
        assert len(resp.json()) == 1

    def test_buscar_por_texto(self):
        """Búsqueda por nombre."""
        client.post("/api/centros", json=sample_centro())
        resp = client.get("/api/centros?q=Test")
        assert len(resp.json()) == 1


class TestEstadisticas:
    def test_estadisticas_vacias(self):
        """Estadísticas sin datos."""
        resp = client.get("/api/estadisticas")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0

    def test_estadisticas_con_datos(self):
        """Estadísticas con centros cargados."""
        client.post("/api/centros", json=sample_centro())
        resp = client.get("/api/estadisticas")
        assert resp.json()["total"] == 1


class TestReportes:
    def test_crear_reporte(self):
        """Crear un reporte de actualización."""
        client.post("/api/centros", json=sample_centro())
        resp = client.post("/api/reportes", json={
            "centro_id": 1,
            "nombre_reportador": "Ciudadano",
            "mensaje": "Está lleno",
            "nuevo_estado": "Lleno",
        })
        assert resp.status_code == 200
        assert resp.json()["mensaje"] == "Reporte enviado"

    def test_reporte_sin_centro(self):
        """Reporte sin centro_id da 400."""
        resp = client.post("/api/reportes", json={})
        assert resp.status_code == 400

    def test_reporte_centro_inexistente(self):
        """Reporte a centro que no existe da 404."""
        resp = client.post("/api/reportes", json={"centro_id": 999})
        assert resp.status_code == 404

    def test_reporte_actualiza_estado(self):
        """Reportar nuevo estado debe actualizar el centro."""
        client.post("/api/centros", json=sample_centro())
        client.post("/api/reportes", json={
            "centro_id": 1,
            "nuevo_estado": "Lleno",
        })
        resp = client.get("/api/centros/1")
        assert resp.json()["estado_centro"] == "Lleno"


class TestEstados:
    def test_listar_estados(self):
        """Debe retornar los 24 estados de Venezuela."""
        resp = client.get("/api/estados")
        assert resp.status_code == 200
        assert len(resp.json()) == 24
        assert "Zulia" in resp.json()


# -------------------------------------------------------------------
# Limpieza
# -------------------------------------------------------------------
def teardown_module(module):
    """Eliminar BD de test."""
    try:
        os.unlink("./test.db")
    except OSError:
        pass