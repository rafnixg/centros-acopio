import os
import sys

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from database import Base  # noqa: E402
from models import CentroAcopio  # noqa: E402,F401
from sync import deduplicate_records, extract_centros_from_csv, sync_from_remote  # noqa: E402


class DummyResponse:
    def __init__(self, *, json_data=None, text_data="", status_code=200):
        self._json_data = json_data
        self.text = text_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self._json_data


@pytest.fixture()
def db_session(tmp_path):
    db_file = tmp_path / "sync_test.db"
    engine = create_engine(
        f"sqlite:///{db_file}",
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_extract_centros_from_csv_parsea_y_mapea_productos():
    csv_text = (
        "id,name,organization,country,state,city,address,latitude,longitude,phone,schedule,supply_types,"
        "accepts_volunteers,notes,is_active,created_at,updated_at\n"
        "1,Centro A,Org A,Venezuela,Miranda,Caracas,Dir A,10.5,-66.8,0412-000,8am-4pm,"
        "agua|alimentos|mascotas,false,Nota de prueba,false,2026-01-01,2026-01-01\n"
    )

    centros = extract_centros_from_csv(csv_text)

    assert len(centros) == 1
    c = centros[0]
    assert c["nombre"] == "Centro A"
    assert c["pais"] == "Venezuela"
    assert c["estado"] == "Miranda"
    assert c["ciudad"] == "Caracas"
    assert c["activo"] is False
    assert c["estado_centro"] == "Pausado"
    assert "Agua potable / embotellada" in c["productos"]
    assert "Alimentos no perecederos" in c["productos"]
    assert "Comida para mascotas" in c["productos"]


def test_deduplicate_records_une_registros_entre_fuentes():
    json_record = {
        "nombre": "Centro Único",
        "pais": "Venezuela",
        "estado": "Miranda",
        "ciudad": "Caracas",
        "direccion": "Dir 1",
        "telefono": "",
        "responsable": "Fuente JSON",
        "horarios": "",
        "productos": '["Agua potable / embotellada"]',
        "activo": True,
        "estado_centro": "Activo",
        "notas": "Fuente: json",
        "latitud": 10.1234,
        "longitud": -66.5678,
    }
    csv_record = {
        "nombre": "centro unico",
        "pais": "Venezuela",
        "estado": "Miranda",
        "ciudad": "Caracas",
        "direccion": "Dir 1",
        "telefono": "0412-1111111",
        "responsable": "Fuente CSV",
        "horarios": "9am-3pm",
        "productos": '["Alimentos no perecederos"]',
        "activo": True,
        "estado_centro": "Activo",
        "notas": "Fuente: csv",
        "latitud": 10.1234,
        "longitud": -66.5678,
    }

    merged, duplicates = deduplicate_records([json_record], [csv_record])

    assert len(merged) == 1
    assert duplicates == 1
    assert "Agua potable / embotellada" in merged[0]["productos"]
    assert "Alimentos no perecederos" in merged[0]["productos"]
    assert merged[0]["telefono"] == "0412-1111111"


def test_sync_from_remote_continua_con_falla_parcial(monkeypatch, db_session):
    json_payload = {
        "estados": [
            {
                "nombre": "Miranda",
                "ciudades": [
                    {
                        "nombre": "Caracas",
                        "centros": [
                            {
                                "nombre": "Centro Parcial",
                                "direccion": "Dir parcial",
                                "telefono": "0412-0000000",
                                "fuente": "json-fuente",
                                "horario": "9-5",
                                "recibe": ["agua potable"],
                                "nota": "Activo",
                                "coords": [10.4, -66.8],
                            }
                        ],
                    }
                ],
            }
        ]
    }

    def fake_get(url, timeout=30):
        if "data.json" in url:
            return DummyResponse(json_data=json_payload)
        raise Exception("csv unavailable")

    monkeypatch.setattr("sync.httpx.get", fake_get)

    result = sync_from_remote(db_session)

    assert result["insertados"] == 1
    assert result["actualizados"] == 0
    assert result["total"] == 1
    assert result["fuentes"]["json"]["error"] is None
    assert result["fuentes"]["csv"]["error"] is not None

    centros = db_session.query(CentroAcopio).all()
    assert len(centros) == 1
    assert centros[0].nombre == "Centro Parcial"


def test_sync_from_remote_no_falla_con_duplicado_interfuente(monkeypatch, db_session):
    json_payload = {
        "estados": [
            {
                "nombre": "Miranda",
                "ciudades": [
                    {
                        "nombre": "Caracas",
                        "centros": [
                            {
                                "nombre": "Centro Duplicado",
                                "direccion": "Dir duplicada",
                                "telefono": "0412-1111111",
                                "fuente": "json-fuente",
                                "horario": "9-5",
                                "recibe": ["agua potable"],
                                "nota": "Activo",
                                "coords": [10.5, -66.9],
                            }
                        ],
                    }
                ],
            }
        ]
    }

    csv_text = (
        "id,name,organization,country,state,city,address,latitude,longitude,phone,schedule,supply_types,"
        "accepts_volunteers,notes,is_active,created_at,updated_at\n"
        "1,centro duplicado,Org CSV,Venezuela,Miranda,Caracas,Dir duplicada,10.5,-66.9,0412-2222222,"
        "8am-4pm,alimentos,false,Duplicado entre fuentes,true,2026-01-01,2026-01-01\n"
    )

    def fake_get(url, timeout=30):
        if "data.json" in url:
            return DummyResponse(json_data=json_payload)
        if "centers/csv" in url:
            return DummyResponse(text_data=csv_text)
        raise Exception("url inesperada")

    monkeypatch.setattr("sync.httpx.get", fake_get)

    result = sync_from_remote(db_session)

    assert result["insertados"] == 1
    assert result["actualizados"] == 0
    assert result["total"] == 1
    assert result["duplicados_omitidos"] >= 1

    centros = db_session.query(CentroAcopio).all()
    assert len(centros) == 1
    assert centros[0].nombre == "Centro Duplicado"
