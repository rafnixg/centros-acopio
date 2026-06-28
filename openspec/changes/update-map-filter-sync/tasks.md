## 1. Refactor `map.js` to support re-calling with filtered data
- [x] Remove the global `initMapa` call assumption — make `cargarMarcadores` callable multiple times from outside
- [x] Ensure `initMapa` handles being called multiple times gracefully (reuse existing map instance)
- [x] Verify map centers/re-centers properly after each marker update

## 2. Integrate map update into `cargarCentros()` in `app.js`
- [x] After `renderCentros(centros)` in the `cargarCentros` function, call `cargarMarcadores(centros)` to update map markers
- [x] Ensure `initMapa` has been called at least once before calling `cargarMarcadores` (lazy initialization guard)

## 3. Adjust `templates/centros.html` to avoid double-fetch
- [x] Remove the separate `fetch("/api/centros")` + `initMapa(centros)` block in the DOMContentLoaded script
- [x] Instead, initialize the map empty and let the first `cargarCentros()` call populate both grid and map
- [x] Or alternatively, have the map init happen inside `cargarCentros` after the first API call

## 4. Verify behavior
- [x] Test that map updates on text search
- [x] Test that map updates when any filter dropdown changes
- [x] Test with URL filter params on page load
- [x] Test edge case: no centers match → map clears and resets
- [x] Test edge case: centers without coordinates are excluded from map but still shown in grid