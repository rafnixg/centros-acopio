## Context
La sincronización actual importa centros desde un único JSON remoto y detecta existentes por coincidencia exacta de `nombre + ciudad + estado`. Al integrar una segunda fuente CSV, este criterio exacto puede ser insuficiente por variaciones de formato (mayúsculas, espacios, acentos, alias de ciudad) y por diferencias de completitud entre fuentes.

## Goals / Non-Goals
- Goals:
- Incorporar una segunda fuente remota CSV dentro del mismo ciclo de sincronización.
- Evitar duplicados entre fuentes y contra la base existente.
- Mantener idempotencia: múltiples corridas seguidas no deben incrementar duplicados.
- Preservar y actualizar datos útiles sin degradar información existente.

- Non-Goals:
- No rediseñar modelo relacional ni crear tablas nuevas para historial de fuentes en esta iteración.
- No implementar reconciliación avanzada asistida por geocoding inverso o fuzzy matching pesado.
- No cambiar flujos de UI; el foco es backend sync y su resumen administrativo.

## Decisions
- Decision: Pipeline por etapas en una sola corrida
  - Etapas: fetch JSON -> normalización JSON -> fetch CSV -> normalización CSV -> dedup in-memory inter-fuente -> upsert contra BD.
  - Rationale: facilita trazabilidad y contabilidad por fuente.

- Decision: Clave de deduplicación canónica determinística
  - Canonical key primaria: normalización de `nombre`, `pais`, `estado`, `ciudad`.
  - Canonical key secundaria/fallback: si existe coordenada válida, permitir match por proximidad exacta de lat/long redondeada + ciudad/estado.
  - Rationale: reduce falsos duplicados por ruido menor de texto y mejora matching para nombres ligeramente distintos con misma ubicación.

- Decision: Estrategia de enriquecimiento conservadora
  - Al detectar centro existente, actualizar solo campos vacíos o claramente mejores (p.ej. teléfono/horario/productos/notas/coords) sin borrar valores válidos previos.
  - Rationale: minimizar regresiones de calidad de datos.

- Decision: Telemetría de sync por fuente
  - Mantener contadores por fuente (`json`, `csv`) y globales, incluyendo `duplicados_omitidos`.
  - Rationale: observabilidad para validar aporte de la nueva fuente y detectar problemas de parsing.

## Risks / Trade-offs
- Riesgo: Deduplicación demasiado estricta (pierde centros distintos con nombres parecidos).
  - Mitigación: usar clave compuesta (nombre+ubicación) y fallback por coords solo como complemento.

- Riesgo: Deduplicación demasiado laxa (duplica centros iguales con pequeñas variaciones).
  - Mitigación: normalización robusta (trim, lower, colapso espacios, remoción de acentos).

- Riesgo: Inestabilidad externa del endpoint CSV.
  - Mitigación: manejo de error aislado por fuente; si CSV falla, JSON sigue sincronizando y se reporta error parcial.

## Migration Plan
1. Introducir funciones de extracción/normalización por fuente.
2. Introducir función de canonicalización y deduplicación in-memory.
3. Integrar merge final y upsert contra BD.
4. Extender respuesta de sync y logging con métricas por fuente.
5. Agregar tests unitarios de normalización + deduplicación y tests de integración de sync parcial.

## Open Questions
- Confirmar endpoint final del CSV para producción (`/api/public/centers/csv` vs `/api/public/centros/csv`).
- Confirmar precedencia de fuente cuando ambos registros aportan valores distintos en un mismo campo (JSON vs CSV).
