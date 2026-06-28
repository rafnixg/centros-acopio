# Change: Make Estado/Región an `<input>` for non-Venezuela countries in the registration form

## Why
Currently the `/registrar` form always shows a `<select>` with Venezuela's states for the "Estado / Región" field. For non-Venezuelan countries (e.g. Colombia, Spain, USA), this is confusing and incorrect — users must pick from a list of Venezuelan states that don't apply. The field should behave as a free-text `<input type="text">` for any country other than Venezuela, and only show the state `<select>` when Venezuela is selected.

## What Changes
- **`templates/registro.html`** — Change the static `<select name="estado">` to a container `<div id="estado-container">` that will be dynamically swapped client-side.
- **`static/js/app.js`** — Add a new function `gestionarCampoEstado(pais)` that:
  - If `pais === "Venezuela"` → renders the `<select>` with the 24 states (like today).
  - If `pais` is any other value → renders an `<input type="text" name="estado">` for free-text entry.
  - On page load, defaults to the `Venezuela` `<select>` (since Venezuela is preselected).
- Wire the `#pais` `<select>` change event to call `gestionarCampoEstado()`.

## Impact
- Affected capability: registro-centros (new spec)
- Affected code: `templates/registro.html`, `static/js/app.js`
- No backend changes needed (the model already accepts any string for `estado`)
- No API changes needed