## ADDED Requirements

### Requirement: Sincronización multi-fuente de centros de acopio
**Capability**: sincronizacion-centros

El sistema SHALL consumir y consolidar centros de acopio desde múltiples fuentes remotas en una sola corrida de sincronización, incluyendo al menos la fuente JSON actual y la fuente CSV de Ayuda para Venezuela.

#### Scenario: Corrida exitosa con ambas fuentes disponibles
- **GIVEN** que la corrida de sincronización inicia por scheduler o por `/admin/sync`
- **AND** ambas fuentes remotas responden exitosamente
- **WHEN** el sistema procesa los registros remotos
- **THEN** consolida datos de ambas fuentes en una colección unificada
- **AND** continúa con deduplicación y upsert sobre la base local

#### Scenario: Falla parcial de una fuente
- **GIVEN** que una de las fuentes remotas no está disponible o retorna error
- **WHEN** la sincronización se ejecuta
- **THEN** el sistema continúa procesando la otra fuente disponible
- **AND** retorna un resultado con error parcial y métricas de la fuente fallida

### Requirement: Deduplicación inter-fuente y contra base existente
**Capability**: sincronizacion-centros

El sistema SHALL evitar inserciones duplicadas cuando un mismo centro exista en más de una fuente o ya esté presente en la base local.

#### Scenario: Mismo centro presente en JSON y CSV
- **GIVEN** que JSON y CSV contienen el mismo centro con variaciones menores de formato
- **WHEN** el sistema compara registros normalizados
- **THEN** detecta una sola entidad canónica
- **AND** evita crear registros duplicados

#### Scenario: Centro ya existente en base local
- **GIVEN** que un centro equivalente ya existe en la base local
- **WHEN** llega nuevamente desde cualquier fuente
- **THEN** el sistema no inserta un nuevo registro
- **AND** actualiza solo campos permitidos según estrategia de enriquecimiento

### Requirement: Normalización de datos CSV a esquema interno
**Capability**: sincronizacion-centros

El sistema SHALL transformar el CSV remoto al esquema interno de `CentroAcopio`, incluyendo mapeo de productos, estado de actividad y campos de contacto/ubicación.

#### Scenario: Registro CSV con `supply_types` múltiples
- **GIVEN** un registro CSV con `supply_types` delimitado por `|`
- **WHEN** el sistema normaliza el registro
- **THEN** convierte cada tipo al catálogo interno de productos
- **AND** persiste el resultado en formato JSON string compatible con la aplicación

#### Scenario: Registro CSV inactivo
- **GIVEN** un registro CSV con `is_active = false`
- **WHEN** el registro se transforma a modelo interno
- **THEN** el centro se persiste con `activo = false`
- **AND** mantiene trazabilidad del origen en notas/responsable

### Requirement: Resumen de sincronización con métricas por fuente
**Capability**: sincronizacion-centros

El sistema SHALL retornar un resumen estructurado de sincronización con métricas globales y por fuente para facilitar monitoreo y diagnóstico.

#### Scenario: Resumen exitoso con deduplicación
- **GIVEN** una corrida completada sin errores fatales
- **WHEN** el proceso termina
- **THEN** el resultado incluye al menos `insertados`, `actualizados`, `total` y `duplicados_omitidos`
- **AND** desglosa métricas por fuente (`json`, `csv`)

#### Scenario: Resumen con error parcial
- **GIVEN** que una fuente falló durante la corrida
- **WHEN** el proceso finaliza con degradación parcial
- **THEN** el resumen incluye el detalle del error por fuente
- **AND** conserva métricas válidas de la fuente procesada exitosamente
