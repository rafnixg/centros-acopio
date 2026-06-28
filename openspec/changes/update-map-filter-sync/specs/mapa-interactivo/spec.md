## MODIFIED Requirements

### Requirement: Sincronización de mapa con filtros
**Capability**: mapa-interactivo

The map on `/centros` SHALL update its markers to reflect only the centers that match the current active filters (text search, país, estado, producto, estado del centro), keeping the map in sync with the grid of cards at all times.

#### Scenario: Map updates when text search is applied
- **GIVEN** the user is on the `/centros` page
- **AND** the map shows markers for all centers
- **WHEN** the user types a search query in the search box
- **THEN** the grid updates with matching centers
- **AND** the map removes markers for centers that don't match
- **AND** the map centers on the remaining markers (or resets to default Venezuela view if none remain)

#### Scenario: Map updates when a state filter is applied
- **GIVEN** the user is on the `/centros` page
- **AND** the map shows markers for all centers
- **WHEN** the user selects a specific estado (state) from the dropdown
- **THEN** the grid updates with matching centers
- **AND** the map markers filter to only that state

#### Scenario: Map updates when multiple filters are combined
- **GIVEN** the user is on the `/centros` page
- **WHEN** the user selects a product filter AND a center status filter simultaneously
- **THEN** both the grid and the map reflect the combined filter results

#### Scenario: No matching centers
- **GIVEN** the user is on the `/centros` page
- **WHEN** filters result in zero matching centers
- **THEN** the grid shows the empty state
- **AND** the map clears all markers and resets to default Venezuela view

### Requirement: Refactor map initialization to use filtered data
**Capability**: mapa-interactivo

The map SHALL be re-initializable with a filtered dataset without needing a full page reload.

#### Scenario: First load shows all centers
- **GIVEN** the user navigates to `/centros` with no filter parameters
- **WHEN** the page loads
- **THEN** the map initializes with all centers that have coordinates

#### Scenario: Page load with URL filter parameters
- **GIVEN** the user navigates to `/centros?estado=Miranda&producto=Alimentos%20no%20perecederos`
- **WHEN** the page loads
- **THEN** the grid loads with pre-applied filters
- **AND** the map shows only centers matching those filters