# Change: Update map markers when filters are applied on /centros

## Why
Currently on `/centros`, the map initializes once with ALL centers, but when the user applies filters (search, estado, producto, etc.), only the grid of cards updates — the map stays unchanged. This is confusing because the map still shows centers that don't match the current filter, making it inconsistent with the grid results.

## What Changes
- **`static/js/map.js`** — Export `cargarMarcadores` so it can be called externally; no longer assumes it only runs once
- **`static/js/app.js`** — After fetching filtered centers in `cargarCentros()`, also update the map markers via `cargarMarcadores(centros)`
- **`templates/centros.html`** — Adjust the inline script so the map initialization passes the filtered dataset instead of always reloading all centers

## Impact
- Affected specs: mapa-interactivo (new capability spec)
- Affected code: `static/js/map.js`, `static/js/app.js`, `templates/centros.html`