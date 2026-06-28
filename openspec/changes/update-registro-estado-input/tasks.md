## 1. Prepare template for dynamic Estado field
- [x] In `templates/registro.html`, replace the hardcoded `<select name="estado" id="estado">` with a placeholder `<div id="estado-container">` that gets populated by JS
- [x] Keep the original select markup as a JS template string inside app.js (or as a client-side template)

## 2. Add `gestionarCampoEstado(pais)` function in `app.js`
- [x] Create function that accepts a `pais` string
- [x] If `pais === "Venezuela"` → populate `#estado-container` with a `<select name="estado" id="estado" required>` and all 24 state `<option>` elements
- [x] If `pais` is any other value or empty → populate `#estado-container` with an `<input type="text" name="estado" id="estado" required placeholder="Ej: Madrid, Antioquia, Texas...">`
- [x] Ensure the field retains the `required` attribute and the `id="estado"` (so `initGeocoding()` still works)

## 3. Wire the País change event on the registration page
- [x] In the `DOMContentLoaded` init section for `#form-registro`, add an event listener on `#pais` that calls `gestionarCampoEstado(paisSelect.value)`
- [x] Call `gestionarCampoEstado("Venezuela")` on page load as default

## 4. Verify behavior
- [x] Test: /registrar loads with Venezuela selected → Estado field is a `<select>` with states
- [x] Test: Change País to another country → Estado switches to `<input type="text">`
- [x] Test: Switch back to Venezuela → Estado switches back to `<select>`
- [x] Test: Submit form with non-Venezuela country and custom estado text
- [ ] Test: Submit form with Venezuela and a selected state
- [ ] Test: Geocoding auto-fill still works (depends on `#estado` id existing)