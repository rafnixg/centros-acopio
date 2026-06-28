## MODIFIED Requirements

### Requirement: Campo Estado/Región dinámico según país
**Capability**: registro-centros

The "Estado / Región" field in the registration form SHALL change its widget type depending on the selected country. When "Venezuela" is selected it SHALL display a `<select>` with the list of 24 Venezuelan states. When any other country is selected it SHALL display a free-text `<input type="text">`.

#### Scenario: Default load with Venezuela selected
- **GIVEN** the user navigates to `/registrar`
- **WHEN** the page loads
- **THEN** the "País" field shows "Venezuela" as selected
- **AND** the "Estado / Región" field is a `<select>` dropdown with the 24 Venezuelan states

#### Scenario: Switching from Venezuela to another country
- **GIVEN** the user is on `/registrar`
- **AND** "Venezuela" is the current selection in País
- **WHEN** the user selects "Colombia" from the País dropdown
- **THEN** the "Estado / Región" field changes to a free-text `<input type="text" name="estado">`
- **AND** any previously selected value in the `<select>` is discarded

#### Scenario: Switching back to Venezuela
- **GIVEN** the user is on `/registrar`
- **AND** a non-Venezuelan country is selected
- **AND** the Estado field is a text input with some typed value
- **WHEN** the user switches País back to "Venezuela"
- **THEN** the "Estado / Región" field changes back to a `<select>` with the 24 Venezuelan states
- **AND** the typed value is discarded

#### Scenario: Submitting form with non-Venezuela country
- **GIVEN** the user is on `/registrar`
- **WHEN** the user selects "España" as País
- **AND** types "Madrid" in the Estado text input
- **AND** submits the form
- **THEN** the centro is created with `pais: "España"` and `estado: "Madrid"`

#### Scenario: Selecting Venezuela preserves select behavior
- **GIVEN** the user is on `/registrar`
- **WHEN** "Venezuela" is selected as País
- **THEN** the Estado field is a `<select>` listing Amazonas, Anzoátegui, ..., Zulia
- **AND** the user can pick one of the 24 options
- **AND** the geocoding auto-fill still works via the existing `initGeocoding()`