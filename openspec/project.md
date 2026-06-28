# Project Context

## Purpose
Directorio nacional de centros de acopio en Venezuela — una plataforma ciudadana para centralizar la información de los centros de acopio activos durante la emergencia. Permite buscar, registrar y filtrar centros, consultar estadísticas en vivo, y reportar el estado actual de cada centro.

## Tech Stack

### Backend
- **Python 3.12+** — Runtime
- **FastAPI** — Web framework (SSR + REST API)
- **SQLAlchemy 2.0** — ORM
- **SQLite** — Base de datos
- **Jinja2** — Template engine (with custom `from_json` filter)
- **APScheduler** — Tareas periódicas (sync cada hora)
- **httpx** — HTTP client para sync remoto
- **Uvicorn** — ASGI server

### Frontend
- **HTML5 + CSS3** — Templates Jinja2, diseño responsive mobile-first
- **JavaScript Vanilla** — Sin frameworks ni librerías JS externas
- **Leaflet.js + OpenStreetMap** — Mapas interactivos (sin API key)
- **CSS custom properties** — Modo oscuro unificado

### Testing
- **pytest** — Test runner
- **FastAPI TestClient** — Tests de integración de API

### DevOps
- **Docker** — Contenedor con Python 3.12-slim
- **Docker Compose** — Orquestación local

## Project Conventions

### Code Style
- **Idioma**: Código y comentarios en español (variable names, funciones, strings UI)
- **Backend**: PEP 8, type hints, docstrings en español en funciones principales
- **Frontend**: JavaScript moderno (ES6+), arrow functions, template literals
- **CSS**: Variables CSS para theming (`var(--primary)`, `var(--bg)`, etc.), mobile-first
- **Naming**: `snake_case` en Python, `camelCase` en JS, lowercase-dashed para templates
- **Imports**: stdlib → terceros → locales, separados por línea en blanco

### Architecture Patterns
- **API-First**: Las rutas HTML consumen la misma API REST que los clientes externos
- **SSR**: Las páginas HTML se renderizan con Jinja2 desde FastAPI
- **CSR**: La página /centros carga datos vía fetch() y renderiza dinámicamente
- **REST API pública**: 7+ endpoints públicos en `/api/` + endpoints administrativos protegidos
- **Admin con cookie token**: Autenticación simple vía cookie `token` (variable de entorno `ADMIN_TOKEN`)
- **Geocodificación automática**: Vía Nominatim (OpenStreetMap) al registrar centros
- **Scheduler asíncrono**: Sync de datos remotos cada hora con APScheduler
- **URL persistence**: Filtros en /centros se sincronizan con query params de URL

### Testing Strategy
- Tests de integración con pytest + TestClient de FastAPI
- Tests enfocados en API REST (23 tests actuales)
- `pyproject.toml` configura testpaths y pythonpath
- Correr con: `pytest` o `python -m pytest`

### Git Workflow
- Proyecto open source en GitHub: https://github.com/rafnixg/centros-acopio
- Commits en español
- Convención OpenSpec para cambios planificados

## Domain Context
- **Centro de acopio**: Punto de recolección de donaciones (alimentos, agua, ropa, medicinas) para emergencias
- **Estados posibles**: Activo 🟢, Lleno 🟡, Pausado 🔵, Cerrado 🔴
- **Productos típicos**: Alimentos no perecederos, agua, higiene personal, botiquín, limpieza, ropa, leche/fórmula/pañales, comida para mascotas
- **Países**: Principalmente Venezuela, pero también centros en el extranjero (diáspora)
- **Ciudadanía**: Cualquier persona puede registrar centros y reportar su estado

## Important Constraints
- **Sin API key**: Mapas con OpenStreetMap (Leaflet.js) — sin depender de Google Maps
- **SQLite**: Base de datos embebida, no adecuada para alta concurrencia
- **Admin simple**: Autenticación por cookie token, no OAuth ni roles
- **Mobile-first**: Diseño responsive obligatorio
- **Modo oscuro**: Toda la UI debe soportar dark mode

## External Dependencies
- **OpenStreetMap (Nominatim)**: Geocodificación automática de direcciones
- **Leaflet.js**: Librería de mapas (CDN)
- **OpenStreetMap tiles**: Capa base del mapa
- **Sincronización remota**: Origen externo de datos de centros
