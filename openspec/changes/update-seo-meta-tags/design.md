# Design: SEO and Open Graph improvements

## Architecture decisions

### Where to define default OG tags

Put default tags in `base.html` inside a `{% block og_tags %}` block. Child templates override it via `{% block og_tags %}{% endblock %}`. This way:
- Most pages inherit sensible defaults.
- `detalle.html` sets centro-specific tags.
- `landing.html` sets its own hero-style tags.

### Absolute URLs for OG tags

Open Graph requires absolute URLs for `og:url` and `og:image`. We'll add a `SITE_URL` variable:
- Default: `https://centrosacopio.rafnixg.dev` (matching the existing WhatsApp share URL in detalle.html).
- Override via `SITE_URL` environment variable.
- Passed to all templates as `site_url`.

### `og:image`

Use a simple SVG-based favicon-style image or the flag emoji as a fallback. Since we don't have a dedicated social image:
- `og:image` = emoji favicon approach using `data:image/svg+xml` (same as current favicon).
- A `SITE_URL + "/static/images/og-image.png"` path can be added later when a real image is designed.

### Twitter cards

Use `twitter:card` = `summary` (not `summary_large_image` since we lack a real image). The description + title will render well.

### Keywords strategy

Per-page keywords that match the page content:
- Landing: "centros de acopio Venezuela, donaciones Venezuela, ayuda humanitaria, emergencia"
- Directorio: "centros de acopio directorio, donar Venezuela, centros activos"
- Detalle: generated from the center's name, estado, ciudad, productos

### Canonical URL

Set on every page using `site_url + request.url.path` to prevent duplicate content from query params.

## Template block design

```html
{% block og_tags %}
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:url" content="{{ site_url }}{{ request.url.path }}">
<meta property="og:image" content="{{ site_url }}/static/images/og-image.png">
<meta property="og:site_name" content="Centros de Acopio Venezuela">
<meta property="twitter:card" content="summary">
<meta name="twitter:title" content="...">
<meta name="twitter:description" content="...">
{% endblock %}
```

## Files to change

| File | Change |
|------|--------|
| `backend/main.py` | Add `SITE_URL` constant, pass `site_url` to all `TemplateResponse` calls |
| `templates/base.html` | Add `keywords`, `block og_tags`, `canonical` |
| `templates/detalle.html` | Override `og_tags` with centro data |
| `templates/landing.html` | Override `og_tags` + add `keywords` |