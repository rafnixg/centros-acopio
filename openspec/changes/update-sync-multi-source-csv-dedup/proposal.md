# Change: Actualizar sincronización para múltiples fuentes (JSON + CSV) con deduplicación

## Why
Actualmente la sincronización solo consume una fuente JSON (`centrosdeacopiovzla.com/data.json`). Se requiere incorporar una segunda fuente en CSV de Ayuda para Venezuela para ampliar cobertura, evitando registros duplicados cuando un mismo centro exista en ambos orígenes.

## What Changes
- Ampliar el proceso de sincronización para consumir dos fuentes remotas:
- Fuente actual JSON: `https://www.centrosdeacopiovzla.com/data.json`
- Nueva fuente CSV: `https://ayudaparavenezuela.com/api/public/centers/csv`
- Normalizar el esquema de ambas fuentes hacia el modelo interno `CentroAcopio`.
- Aplicar deduplicación inter-fuente antes de insertar nuevos centros, para no duplicar entradas existentes.
- Definir reglas de actualización cuando un centro ya existe en BD y llega con nuevos datos desde cualquiera de las fuentes.
- Exponer en el resultado de sincronización métricas separadas por fuente y métricas globales (insertados, actualizados, duplicados omitidos, errores por fuente).

## Impact
- Affected specs: sincronizacion-centros (nueva capacidad)
- Affected code: `backend/sync.py`, `backend/main.py` (respuesta administrativa de sync), pruebas de integración/unidad relacionadas a sync
- Operational impact: mayor volumen de datos por corrida de sync y nueva dependencia de disponibilidad para endpoint CSV

## Gaps / Clarifications
- El endpoint compartido en el requerimiento (`/api/public/centros/csv`) no responde actualmente; se detectó uso de `/api/public/centers/csv` en los assets públicos del sitio.
- Esta propuesta asume que el endpoint canónico para implementación es `/api/public/centers/csv`.
