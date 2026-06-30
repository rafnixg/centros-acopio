## 1. Implementación backend de sincronización multi-fuente
- [x] 1.1 Extraer la lógica actual de sync para soportar múltiples proveedores de datos (JSON actual + CSV nuevo) sin duplicar flujo de persistencia.
- [x] 1.2 Implementar parser/normalizador del CSV remoto (`/api/public/centers/csv`) hacia el esquema de `CentroAcopio`.
- [x] 1.3 Implementar normalización canónica de claves (nombre/pais/estado/ciudad) para comparar centros con tolerancia a formato.
- [x] 1.4 Implementar deduplicación inter-fuente en memoria antes del upsert a BD.
- [x] 1.5 Actualizar lógica de upsert para reportar `insertados`, `actualizados` y `duplicados_omitidos`.

## 2. Robustez operativa y observabilidad
- [x] 2.1 Manejar fallas por fuente de forma aislada (degradación parcial en vez de falla total de la corrida).
- [x] 2.2 Extender resumen de `sync_from_remote` con métricas por fuente (`json`, `csv`) y globales.
- [x] 2.3 Asegurar que el endpoint administrativo `/admin/sync` refleje el nuevo resumen detallado.

## 3. Validación
- [x] 3.1 Agregar pruebas unitarias para normalización y deduplicación (variaciones de acentos, casing y espacios).
- [x] 3.2 Agregar pruebas para parsing de `supply_types` del CSV y mapeo de productos al formato interno.
- [x] 3.3 Agregar pruebas de integración del sync con datasets mixtos (JSON+CSV) verificando no duplicación.
- [x] 3.4 Ejecutar suite de pruebas (`pytest`) y validar que no hay regresiones en endpoints existentes.
