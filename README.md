# 🇻🇪 Centros de Acopio Venezuela

**Directorio nacional de centros de acopio** — una plataforma ciudadana para centralizar la información de los centros de acopio activos en Venezuela durante la emergencia.

Hecho con ❤️ por [@rafnixg](https://links.rafnixg.dev) · [Código abierto en GitHub](https://github.com/rafnixg/centros-acopio)

---

## ✨ Funcionalidades

### Públicas
- 📄 **Landing informativa** — Hero con estadísticas en vivo, secciones: Donaciones, Centros de acopio, Voluntariado, Emergencia
- 📋 **Directorio de centros** (`/centros`) — Grid con tarjetas, buscador, filtros por estado/producto/estado del centro, mapa Leaflet interactivo
- ➕ **Registro de centros** (`/registrar`) — Formulario completo con geocodificación automática vía Nominatim
- 👁️ **Vista detalle** (`/centro/{id}`) — Info completa, mapa, botones para compartir (WhatsApp, Telegram, Twitter/X), sección de reportes ciudadanos
- 📊 **Estadísticas** (`/estadisticas`) — Dashboard con centros por estado, productos más solicitados, centros recién registrados

### Administrativas
- 🔐 **Panel admin** (`/admin`) — CRUD completo de centros, revisión de reportes ciudadanos, login protegido
- 📢 **Reportes ciudadanos** — Cualquier persona puede reportar el estado actual de un centro desde la vista detalle

### Técnicas
- 🌐 **API REST** completa con 7 endpoints públicos
- 🗺️ **Mapa interactivo** con Leaflet.js + OpenStreetMap (sin API key)
- 🌓 **Modo oscuro** unificado en todo el sitio
- 📱 **Diseño responsive mobile-first**
- 🔍 **Geocodificación automática** al registrar un centro
- ⚡ **Skeleton loading** + filtros persistentes en URL

---

## 🏗️ Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Backend** | Python 3.12+ · FastAPI |
| **Base de datos** | SQLite + SQLAlchemy 2.0 |
| **Frontend** | HTML5 + CSS3 + JavaScript Vanilla |
| **Mapas** | Leaflet.js + OpenStreetMap |
| **Tests** | pytest + TestClient (FastAPI) |
| **Despliegue** | Docker / Uvicorn |

---

## 📁 Estructura del Proyecto

```
centros-acopios/
├── backend/
│   ├── main.py           # FastAPI: 22 endpoints (vistas HTML + API REST)
│   ├── database.py       # SQLAlchemy engine + session
│   ├── models.py         # ORM: CentroAcopio, ReporteActualizacion
│   └── schemas.py        # Pydantic: Create, Update, Response
├── static/
│   ├── css/
│   │   ├── styles.css    # Componentes: formularios, tarjetas, mapa, botones
│   │   └── landing.css   # Landing page premium (oscuro, glass effect)
│   └── js/
│       ├── app.js        # Fetch, render, filtros, geocoding, registro
│       └── map.js        # Leaflet: marcadores por estado, popups
├── templates/
│   ├── landing.html      # Página principal informativa
│   ├── centros.html      # Directorio con buscador + filtros + mapa
│   ├── registro.html     # Formulario de registro
│   ├── detalle.html      # Vista detalle + reportes + compartir
│   ├── estadisticas.html # Dashboard público
│   ├── base.html         # Layout base con navbar y footer
│   ├── admin.html        # Panel de administración
│   ├── admin_login.html  # Login protegido
│   └── admin_editar.html # Edición de centros
├── tests/
│   └── test_api.py       # 23 tests de API (pytest)
├── Dockerfile
├── requirements.txt
├── pyproject.toml
└── run.py                # Script para desarrollo local
```

---

## 🚀 Inicio Rápido

### Local (sin Docker)

```bash
# 1. Clonar
git clone https://github.com/tu-usuario/centros-acopios.git
cd centros-acopios

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Iniciar servidor
python run.py

# 4. Abrir en el navegador
# http://localhost:8000
```

### Con Docker (build local)

```bash
# Construir imagen
docker build -t centros-acopios .

# Ejecutar contenedor (la DB se borra al reiniciar)
docker run -d -p 8000:8000 --name centros-acopios centros-acopios
```

### Con Docker Compose (recomendado — DB persistente)

```bash
# Iniciar con volumen persistente para la base de datos
docker compose up -d

# Opcional: cambiar el ADMIN_TOKEN
ADMIN_TOKEN=miclave123 docker compose up -d

# Abrir en el navegador
# http://localhost:8000
```

> 💾 Con `docker compose` la base de datos SQLite se guarda en un volumen Docker (`centros_acopio_data`) y **no se pierde al reiniciar el contenedor**.

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
| `GET` | `/api/estadisticas` | Estadísticas: total, por estado, por producto, recientes |
| `POST` | `/api/geocodificar` | Geocodificar dirección vía Nominatim |
| `GET` | `/api/reportes/{id}` | Listar reportes de un centro |
| `POST` | `/api/reportes` | Crear reporte ciudadano |

> 📘 **Documentación interactiva de la API**: [`/docs`](https://centrosacopio.rafnixg.dev/docs) (Swagger UI)

---

## 🧪 Tests

```bash
# Ejecutar todos los tests
python -m pytest tests/ -v

# Con cobertura
python -m pytest tests/ --cov=backend --cov-report=term
```

Actualmente **23 tests** que cubren:

| Grupo | Tests | Descripción |
|-------|-------|-------------|
| Landing | 2 | Página principal carga, estadísticas |
| Directorio | 3 | Páginas internas cargan |
| Centros API | 7 | CRUD, validaciones, auth, 404 |
| Filtros | 3 | Por estado, producto, búsqueda texto |
| Estadísticas | 2 | Vacías y con datos |
| Reportes | 4 | Crear, validar, actualizar estado |
| Estados | 1 | Lista de 24 estados |

---

## 🔐 Panel Administrativo

| Ruta | Descripción |
|------|-------------|
| `/admin/login` | Login con contraseña |
| `/admin` | Panel con tabla de centros + reportes |
| `/admin/editar/{id}` | Editar centro |

**Contraseña por defecto:** `admin123`  
(Configurable vía variable de entorno `ADMIN_TOKEN`)

---

## 🌐 Rutas del Sitio

| Ruta | Descripción |
|------|-------------|
| `/` | Landing informativa (hero + donaciones + centros + voluntariado + emergencia) |
| `/centros` | Directorio completo con buscador, filtros, grid y mapa |
| `/registrar` | Formulario para registrar un centro |
| `/centro/{id}` | Vista detalle con reportes y compartir en redes |
| `/estadisticas` | Dashboard con estadísticas y gráficos |
| `/admin` | Panel administrativo protegido |
| `/privacidad` | Política de privacidad |
| `/terminos` | Términos y condiciones |
| `/docs` | Documentación interactiva de la API (Swagger UI) |

---

## 🤝 Contribuir

1. Haz un fork del proyecto
2. Crea tu rama: `git checkout -b feature/nueva-funcionalidad`
3. Haz tus cambios y escribe tests
4. Asegúrate de que los tests pasen: `python -m pytest tests/ -v`
5. Envía un Pull Request

---

## 📄 Licencia

Código abierto — hecho por venezolanos 🇻🇪

---

## 🙏 Reconocimientos

- [Venevisión — Emergencia Venezuela](https://ayudavenezuela.venevision.com/)
- [Desaparecidos Terremoto Venezuela](https://desaparecidosterremotovenezuela.com/)
- OpenStreetMap y Leaflet.js por los mapas gratuitos