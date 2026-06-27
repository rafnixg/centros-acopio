# Plan: Plataforma Nacional de Centros de Acopio — Venezuela

## 1. Objetivo del Proyecto

Crear un sitio web **100% vanilla (FastAPI + HTML + CSS + JavaScript)** que funcione como **directorio nacional de centros de acopio** en Venezuela. Cualquier persona puede:

- **Registrar** un centro de acopio con datos completos (dirección, responsable, contacto, productos que reciben, horarios).
- **Buscar** centros por estado, ciudad, tipo de producto, o nombre.
- **Ver** la información actualizada de cada centro.
- **Reportar** si un centro está lleno, cerrado, o si hay actualizaciones.

---

## 2. Inspiración (Sitios de Referencia)

| Sitio | Inspiración para este proyecto |
|-------|--------------------------------|
| [ayudavenezuela.venevision.com](https://ayudavenezuela.venevision.com/) | Sección **"Centros de acopio"** con tarjetas por ciudad, dirección y horarios. Diseño limpio, navegación por secciones. |
| [desaparecidosterremotovenezuela.com](https://desaparecidosterremotovenezuela.com/) | Plataforma de **registro ciudadano masivo** con cards de personas, filtros, y reporte rápido. UX enfocada en acción inmediata. |

---

## 3. Funcionalidades Principales (MVP)

### 3.1 Registro de Centros de Acopio
Formulario público con los siguientes campos:

| Campo | Tipo | Obligatorio |
|-------|------|-------------|
| Nombre del centro | Texto | ✅ |
| Estado | Select (24 estados) | ✅ |
| Ciudad / Municipio | Texto | ✅ |
| Dirección exacta | Texto largo (con referencia) | ✅ |
| Teléfono(s) de contacto | Texto | ✅ |
| Responsable del centro | Texto | ✅ |
| Horarios de recepción | Texto (ej: "Lun–Vie 9:00–15:00") | ✅ |
| Tipos de productos que reciben | Checkboxes múltiples | ✅ |
| ¿Está activo actualmente? | Sí/No | ✅ |
| Estado del centro | Select: Activo / Pausado / Lleno / Cerrado | ✅ |
| Correo electrónico | Email | ❌ |
| Redes sociales | Texto | ❌ |
| Foto del centro | Imagen (URL) | ❌ |
| Notas adicionales | Texto largo | ❌ |

### 3.2 Tipos de Productos (Checkboxes)
- 🥫 Alimentos no perecederos
- 💧 Agua potable / embotellada
- 🧻 Artículos de higiene personal
- 🩹 Botiquín / primeros auxilios
- 🧹 Productos de limpieza
- 👕 Ropa / frazadas / calzado
- 🍼 Leche / fórmula infantil / pañales
- 🐾 Comida para mascotas
- 📦 Otros (texto libre)

### 3.3 Visualización y Búsqueda
- **Grid de tarjetas** con info resumida del centro
- **Buscador** por texto libre (nombre, ciudad, dirección)
- **Filtros**: por estado, por tipo de producto, por estado del centro (Activo/Pausado/etc.)
- **Vista detalle** de cada centro con toda la info
- **Responsive**: funciona en celulares (crítico para emergencias)

### 3.4 Mapa Interactivo
- Integración con **Leaflet.js** (OSM) para ubicar centros en un mapa de Venezuela
- Marcadores con íconos de colores según estado (Activo = verde, Lleno = amarillo, Cerrado = rojo)
- Popup con nombre del centro al hacer clic

### 3.5 Panel de Administración (Opcional)
- Ruta `/admin` protegida con usuario/contraseña
- CRUD completo de centros
- Moderación (aprobar/rechazar centros reportados)

---

## 4. Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| **Backend** | Python + FastAPI |
| **Base de datos** | SQLite (fácil despliegue, sin servidor) vía SQLAlchemy |
| **Frontend** | HTML5 + CSS3 + JavaScript Vanilla (sin frameworks) |
| **Mapas** | Leaflet.js + OpenStreetMap (gratuito, sin API key) |
| **Estilos** | CSS moderno con variables, grid/flexbox, diseño mobile-first |
| **Despliegue** | Uvicorn + opcional: Docker / Railway / Render / VPS |

---

## 5. Arquitectura del Proyecto

```
centros-acopios/
├── backend/
│   ├── main.py              # App FastAPI, rutas, CORS
│   ├── database.py           # Configuración SQLAlchemy + SQLite
│   ├── models.py             # Modelo ORM (CentroAcopio)
│   └── schemas.py            # Schemas Pydantic (request/response)
├── static/
│   ├── css/
│   │   └── styles.css        # Estilos globales
│   ├── js/
│   │   ├── app.js            # Lógica principal (fetch, render, filtros)
│   │   └── map.js            # Inicialización de Leaflet
│   └── images/               # Favicon, logos, iconos
├── templates/
│   ├── base.html             # Layout base (head, nav, footer)
│   ├── index.html            # Página principal (buscador + grid)
│   ├── registro.html         # Formulario de registro
│   └── detalle.html          # Vista detalle de un centro
├── requirements.txt          # Dependencias Python
└── run.py                    # Script para iniciar el servidor
```

---

## 6. Modelo de Datos (SQLite)

```python
class CentroAcopio(Base):
    id: int (PK, autoincrement)
    nombre: str               # Nombre del centro
    estado: str               # Estado de Venezuela
    ciudad: str               # Ciudad o municipio
    direccion: str            # Dirección exacta + referencias
    telefono: str             # Teléfono(s) de contacto
    responsable: str          # Nombre del responsable
    horarios: str             # Horarios de recepción
    productos: str            # JSON string con checkboxes seleccionados
    activo: bool              # ¿Está activo actualmente?
    estado_centro: str        # Activo / Pausado / Lleno / Cerrado
    email: str | None         # Correo electrónico
    redes: str | None         # Redes sociales
    foto_url: str | None      # URL de imagen
    notas: str | None         # Notas adicionales
    latitud: float | None     # Coordenadas para mapa
    longitud: float | None    # Coordenadas para mapa
    fecha_registro: datetime  # Fecha de creación
    ultima_actualizacion: datetime  # Última modificación
```

---

## 7. Diseño UX/UI (Mockups Conceptuales)

### 7.1 Página Principal (`index.html`)

```
┌─────────────────────────────────────────────┐
│  🏠 CENTROS DE ACOPIO VENEZUELA             │
│  [Buscar por nombre, ciudad...] 🔍          │
│  [Filtrar por estado ▼] [Producto ▼]        │
├─────────────────────────────────────────────┤
│ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│ │ 🏪 Centro │ │ 🏪 Centro │ │ 🏪 Centro │     │
│ │ Caracas   │ │ Valencia  │ │ Maracaibo│     │
│ │ 📍 Direc. │ │ 📍 Direc. │ │ 📍 Direc. │     │
│ │ 📞 0412.. │ │ 📞 0412.. │ │ 📞 0412.. │     │
│ │ 🟢 Activo │ │ 🟡 Lleno  │ │ 🔴 Cerrado│     │
│ │ 🥫💧🧻   │ │ 🥫💧     │ │ —        │     │
│ └──────────┘ └──────────┘ └──────────┘     │
│ ┌──────────┐ ┌──────────┐                   │
│ │ 🏪 Centro │ │ 🏪 Centro │                   │
│ │ ...       │ │ ...       │                   │
│ └──────────┘ └──────────┘                   │
├─────────────────────────────────────────────┤
│  [➕ Registrar nuevo centro de acopio]       │
└─────────────────────────────────────────────┘
```

### 7.2 Formulario de Registro (`registro.html`)

```
┌─────────────────────────────────────────────┐
│  Registrar Centro de Acopio                  │
├─────────────────────────────────────────────┤
│  Nombre del centro: [___________________]    │
│  Estado: [Amazonas ▼]                       │
│  Ciudad: [___________________]              │
│  Dirección: [___________________]           │
│  Teléfono: [___________________]            │
│  Responsable: [___________________]         │
│  Horarios: [___________________]            │
│                                             │
│  Productos que recibe:                      │
│  ☑ Alimentos no perecederos                 │
│  ☑ Agua potable                             │
│  ☐ Artículos de higiene                     │
│  ☐ Botiquín / primeros auxilios             │
│  ☐ Ropa / frazadas                         │
│  ☐ Leche / fórmula infantil                 │
│  ☐ Comida para mascotas                    │
│  ☐ Otros: [_______________]                │
│                                             │
│  Estado del centro: [Activo ▼]              │
│  [✓] Está recibiendo donaciones hoy         │
│                                             │
│  [GUARDAR CENTRO DE ACOPIO]                 │
└─────────────────────────────────────────────┘
```

---

## 8. API REST (FastAPI)

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/centros` | Lista todos los centros (con filtros: `?estado=, ?producto=, ?q=`) |
| `GET` | `/api/centros/{id}` | Detalle de un centro |
| `POST` | `/api/centros` | Registrar un nuevo centro |
| `PUT` | `/api/centros/{id}` | Actualizar un centro |
| `DELETE` | `/api/centros/{id}` | Eliminar un centro |
| `GET` | `/api/estados` | Lista de estados de Venezuela |
| `GET` | `/api/centros/estadisticas` | Stats: total centros, por estado, etc. |

---

## 9. Plan de Implementación (Fases)

### Fase 1 — MVP (Core)
- [x] Proyecto estructurado
- [ ] Backend FastAPI con modelo CRUD + SQLite
- [ ] Formulario de registro funcional
- [ ] Grid de tarjetas con buscador y filtros
- [ ] Diseño responsive mobile-first
- [ ] Despliegue inicial

### Fase 2 — Mejoras
- [ ] Mapa Leaflet con geolocalización de centros
- [ ] Vista detalle de cada centro
- [ ] Compartir centro en WhatsApp / redes
- [ ] Mejoras en UX/UI (animaciones, transiciones)

### Fase 3 — Escalabilidad
- [ ] Panel admin con autenticación
- [ ] Moderación de centros reportados
- [ ] Reportes de centros llenos/cerrados
- [ ] Estadísticas generales (dashboard público)
- [ ] Migración a PostgreSQL (opcional)

---

## 10. Estados de Venezuela (Dropdown)

```python
ESTADOS_VENEZUELA = [
    "Amazonas", "Anzoátegui", "Apure", "Aragua", "Barinas", "Bolívar",
    "Carabobo", "Cojedes", "Delta Amacuro", "Distrito Capital", "Falcón",
    "Guárico", "Lara", "La Guaira", "Mérida", "Miranda", "Monagas",
    "Nueva Esparta", "Portuguesa", "Sucre", "Táchira", "Trujillo",
    "Yaracuy", "Zulia"
]
```

---

## 11. Criterios de Diseño

- **Mobile-first**: más del 80% de los usuarios accederán desde teléfonos
- **Accesibilidad**: contraste suficiente, etiquetas claras, `alt` en imágenes
- **Rendimiento**: cero dependencias JS externas excepto Leaflet
- **Modo oscuro**: soporte CSS con `prefers-color-scheme`
- **Idioma**: 100% español
- **Carga rápida**: evitar librerías pesadas, CSS crítico inline

---

## 12. Próximos Pasos

1. Instalar dependencias: `pip install fastapi uvicorn sqlalchemy`
2. Crear archivos del backend (`main.py`, `database.py`, `models.py`, `schemas.py`)
3. Crear templates HTML (`base.html`, `index.html`, `registro.html`, `detalle.html`)
4. Crear archivos estáticos (`styles.css`, `app.js`, `map.js`)
5. Probar localmente con `uvicorn backend.main:app --reload`
6. Desplegar en Railway / Render / VPS

---

> **Nota:** Este proyecto está inspirado en [ayudavenezuela.venevision.com](https://ayudavenezuela.venevision.com/) y [desaparecidosterremotovenezuela.com](https://desaparecidosterremotovenezuela.com/) pero con un enfoque exclusivo en **centralizar los centros de acopio** para optimizar la logística de ayuda humanitaria en Venezuela.