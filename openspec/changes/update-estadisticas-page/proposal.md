# Change: Revamp statistics page with country/state separation and donut charts

## Why
The current `/estadisticas` page mixes countries and Venezuelan states together in a single "Centros por Estado" chart, which is confusing. For example, "Estados Unidos: 78" and "Zulia: 63" appear in the same list. The page also uses basic horizontal bars with no visual variety.

## What Changes
- **`templates/estadisticas.html`** — Restructure layout into a 3-column grid: "Por País" (donut), "Por Estado Venezuela" (donut), "Productos más solicitados" (horizontal bars). Inject `ESTADOS_VENEZUELA` as a JS variable from the template context.
- **`static/js/app.js`** (inline script in the template) — Add a reusable `renderDonutChart(containerId, data, labelKey, valueKey, colorFn)` function that renders CSS conic-gradient donut charts. Filter `por_estado` data to show only Venezuelan states (using `ESTADOS_VENEZUELA` list). Show top items + "Otros" grouping for readability.
- The page layout changes from 2-column grid to 3-column grid on desktop (stacking on mobile).

## Impact
- Affected spec: estadisticas (new capability)
- Affected code: `templates/estadisticas.html` only (template + inline script)
- No backend changes needed — the existing `/api/estadisticas` endpoint already returns `por_pais`, `por_estado`, `por_producto`, `por_estado_centro`
- `ESTADOS_VENEZUELA` already passed to the template as `estados`