## MODIFIED Requirements

### Requirement: Separar estadísticas por país y por estado venezolano
**Capability**: estadisticas

The statistics page SHALL display "Centros por País" and "Centros por Estado (Venezuela)" as two distinct visualizations. The "por estado" chart SHALL only include entries that match the predefined list of Venezuelan states, excluding country names that leak into the data.

#### Scenario: Page shows two separate location charts
- **GIVEN** the user navigates to `/estadisticas`
- **WHEN** the page loads
- **THEN** there is a "🌍 Centros por País" section showing a donut chart with countries like Colombia, USA, España, Venezuela
- **AND** there is a separate "📍 Centros por Estado (Venezuela)" section showing only Venezuelan states (Amazonas, Zulia, etc.)

#### Scenario: Country names filtered from estado chart
- **GIVEN** the API returns `por_estado` containing mixed entries like `{"Estados Unidos": 78, "Zulia": 63, "Colombia": 70, "Mérida": 42}`
- **WHEN** the page renders
- **THEN** "Estados Unidos" and "Colombia" appear ONLY in the "Por País" chart
- **AND** "Zulia" and "Mérida" appear ONLY in the "Por Estado (Venezuela)" chart

#### Scenario: Non-Venezuelan states without country match fall to estado chart
- **GIVEN** a centro has `pais: "Francia"` and `estado: "Île-de-France"`
- **WHEN** rendering the stats page
- **THEN** "Francia" appears in the "Por País" chart
- **AND** "Île-de-France" appears in the "Por Estado" chart only if it's NOT in the Venezuelan states list

### Requirement: Donut charts for country and estado visualizations
**Capability**: estadisticas

The "Por País" and "Por Estado (Venezuela)" charts SHALL render as CSS-based donut charts using `conic-gradient`. The donut chart SHALL include a legend below it. Items with very small counts (less than 3% of total) SHALL be grouped into an "Otros" slice.

#### Scenario: Donut chart renders correctly
- **GIVEN** the stats page loaded with data
- **WHEN** the "Por País" section is visible
- **THEN** a donut chart is rendered with colored slices proportional to each country's count
- **AND** a legend lists each color, label, and count below the chart

#### Scenario: Small items grouped into "Otros"
- **GIVEN** 22 countries are present in the data
- **WHEN** the donut is rendered
- **THEN** countries with less than 3% of total are grouped into a single "Otros" slice
- **AND** the legend shows "Otros" with the combined count

### Requirement: Updated page layout
**Capability**: estadisticas

The statistics page layout SHALL change from a 2-column grid to a responsive 3-column (desktop) / 1-column (mobile) grid.

#### Scenario: Desktop layout shows 3 columns
- **GIVEN** the user is on a desktop viewport (>900px)
- **WHEN** the stats page loads
- **THEN** "🌍 Por País", "📍 Por Estado (Venezuela)", and "📦 Productos" appear in a 3-column grid

#### Scenario: Mobile layout shows stacked cards
- **GIVEN** the user is on a mobile viewport (<600px)
- **WHEN** the stats page loads
- **THEN** all sections stack vertically in a single column