# 🇻🇪 Centros de Acopio Venezuela — v1.0.0

**Primer release oficial** · 28 de junio de 2026

Plataforma ciudadana para centralizar la información de centros de acopio activos en Venezuela durante la emergencia. [Código abierto en GitHub](https://github.com/rafnixg/centros-acopio)

---

## ✨ Funcionalidades completas

### 🌐 Públicas

| Funcionalidad | Ruta | Descripción |
|---|---|---|
| **Landing informativa** | `/` | Hero con estadísticas en vivo, secciones: Donaciones, Centros de acopio, Voluntariado, Emergencia |
| **Directorio de centros** | `/centros` | Grid con tarjetas, buscador, filtros por estado/producto/estado del centro |
| **Mapa interactivo** | `/centros` | Leaflet.js + OpenStreetMap, marcadores por estado, se sincroniza con filtros |
| **Registro de centros** | `/registrar` | Formulario completo con geocodificación automática vía Nominatim |
| **Vista detalle** | `/centro/{id}` | Info completa, mapa, botones compartir (WhatsApp, Telegram, Twitter/X) |
| **Reportes ciudadanos** | `/centro/{id}` | Cualquier persona reporta el estado actual de un centro |
| **Estadísticas** | `/estadisticas` | Dashboard con donut charts, centros por país/estado (VE), productos, recientes |
| **API Docs** | `/api/docs` | Documentación interactiva de la API REST |

### 🔐 Administrativas

| Funcionalidad | Descripción |
|---|---|
| **Panel admin** | CRUD completo de centros, revisión de reportes ciudadanos |
| **Login protegido** | Autenticación por cookie token configurable (`ADMIN_TOKEN`) |
| **Sincronización remota** | Importación automática desde `centrosdeacopiovzla.com` (cada hora) |

### ⚙️ Técnicas

- **API REST pública** — 10 endpoints (`/api/centros`, `/api/estadisticas`, `/api/reportes`, etc.)
- **Mapa sin API key** — Leaflet.js + OpenStreetMap tiles
- **Modo oscuro** unificado en todo el sitio (CSS custom properties)
- **Diseño responsive** mobile-first (3 → 2 → 1 columnas)
- **Geocodificación automática** al registrar un centro (Nominatim)
- **Skeleton loading** + filtros persistentes en URL
- **Campo Estado/Región dinámico** — `<select>` para Venezuela, texto libre para otros países
- **SEO completo** — Open Graph, Twitter Cards, canonical URL, meta keywords
- **Analytics** — Umami self-hosted (privado, sin cookies)
- **URL base configurable** vía `SITE_URL`

---

## 🏗️ Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Backend** | Python 3.12+ · FastAPI |
| **Base de datos** | SQLite + SQLAlchemy 2.0 |
| **Frontend** | HTML5 + CSS3 + JavaScript Vanilla |
| **Mapas** | Leaflet.js + OpenStreetMap |
| **Templates** | Jinja2 con filtro personalizado `from_json` |
| **Scheduler** | APScheduler (sync cada hora) |
| **Tests** | pytest + TestClient (FastAPI) — 23 tests |
| **Despliegue** | Docker / Uvicorn / Docker Compose |

---

## 📁 Estructura del proyecto

```
centros-acopios/
├── backend/
│   ├── main.py           # FastAPI: 22 endpoints (HTML + API REST)
│   ├── database.py       # SQLAlchemy engine + session
│   ├── models.py         # ORM: CentroAcopio, ReporteActualizacion
│   ├── schemas.py        # Pydantic: Create, Update, Response
│   └── sync.py           # Sincronización desde centrosdeacopiovzla.com
├── static/
│   ├── css/
│   │   ├── styles.css    # Componentes: formularios, tarjetas, mapa, botones
│   │   └── landing.css   # Landing page premium (oscuro, glass effect)
│   └── js/
│       ├── app.js        # Fetch, render, filtros, geocoding, registro
│       └── map.js        # Leaflet: marcadores por estado, popups
├── templates/
│   ├── base.html         # Layout base con navbar, footer, SEO tags
│   ├── landing.html      # Página principal informativa
│   ├── centros.html      # Directorio con buscador + filtros + mapa
│   ├── registro.html     # Formulario de registro
│   ├── detalle.html      # Vista detalle + reportes + compartir
│   ├── estadisticas.html # Dashboard con donut charts
│   ├── admin.html        # Panel de administración
│   ├── admin_login.html  # Login protegido
│   ├── admin_editar.html # Edición de centros
│   ├── api_docs.html     # Documentación de la API
│   ├── privacidad.html   # Política de privacidad
│   └── terminos.html     # Términos y condiciones
├── tests/
│   └── test_api.py       # 23 tests de integración de API
├── openspec/
│   ├── project.md        # Contexto y convenciones del proyecto
│   ├── AGENTS.md         # Instrucciones OpenSpec para asistentes IA
│   └── changes/          # Propuestas de cambio planificadas
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── run.py                # Script para desarrollo local
└── RELEASE.md            # Este archivo
```

---

## 🚀 Inicio Rápido

### Local (sin Docker)

```bash
git clone https://github.com/rafnixg/centros-acopio.git
cd centros-acopio
pip install -r requirements.txt
python run.py
# Abrir http://localhost:8000
```

### Con Docker Compose (recomendado)

```bash
docker compose up -d
# Abrir http://localhost:8000
```

> Con `docker compose` la base de datos SQLite se guarda en un volumen persistente y no se pierde al reiniciar.

---

## 🔌 API REST

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/centros` | Listar centros (filtros: `?q=&estado=&producto=&estado_centro=`) |
| `GET` | `/api/centros/{id}` | Detalle de un centro |
| `POST` | `/api/centros` | Registrar un nuevo centro |
| `PUT` | `/api/centros/{id}` | Actualizar un centro (requiere auth admin) |
| `DELETE` | `/api/centros/{id}` | Eliminar un centro (requiere auth admin) |
| `GET` | `/api/estados` | Lista de 24 estados de Venezuela |
| `GET` | `/api/estadisticas` | Estadísticas: total, por país, por estado, por producto |
| `GET` | `/api/paises` | Lista de países con centros registrados |
| `POST` | `/api/geocodificar` | Geocodificar dirección vía Nominatim |
| `GET` | `/api/reportes/{id}` | Listar reportes de un centro |
| `POST` | `/api/reportes` | Crear reporte ciudadano |

> Documentación interactiva: [`/docs`](https://centrosacopio.rafnixg.dev/docs) (Swagger UI)

---

## 🧪 Tests

```bash
python -m pytest tests/ -v
```

---

## 🧰 OpenSpec

Este proyecto usa **OpenSpec** para planificar cambios de forma estructurada:

```bash
# Ver cambios activos
openspec list

# Ver especificaciones
openspec list --specs

# Validar un cambio
openspec validate <change-id> --strict
```

---

## 📜 Licencia

Código abierto. Hecho con ❤️ por [@rafnixg](https://links.rafnixg.dev).
