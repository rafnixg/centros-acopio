## 1. Add `SITE_URL` to backend config
- [ ] In `backend/main.py`, add `SITE_URL = os.environ.get("SITE_URL", "https://centrosacopio.rafnixg.dev")`
- [ ] Add `site_url=SITE_URL` to every `TemplateResponse` call across all routes

## 2. Update `base.html` with SEO foundation
- [ ] Add `<meta name="keywords">` with general keywords
- [ ] Wrap OG tags in `{% block og_tags %}` so child templates can override
- [ ] Add `og:url`, `og:site_name`, `og:image` (SVG emoji favicon or placeholder)
- [ ] Add `twitter:card`, `twitter:title`, `twitter:description`, `twitter:site`
- [ ] Add `<link rel="canonical" href="{{ site_url }}{{ request.url.path }}">`

## 3. Update `detalle.html` with centro-specific OG tags
- [ ] Override `{% block og_tags %}` with centro-specific tags
- [ ] `og:title` = `{{ centro.nombre }} — Centros de Acopio Venezuela`
- [ ] `og:description` = `"{{ centro.nombre }} en {{ centro.ciudad }}, {{ centro.estado }}{% if centro.pais != 'Venezuela' %}, {{ centro.pais }}{% endif %} · {{ centro.estado_centro | emoji }} {{ centro.estado_centro }}"` (may need a simple helper)
- [ ] `og:url` = absolute centro URL
- [ ] `twitter:title` and `twitter:description` matching OG tags
- [ ] `keywords` = centro name, city, estado

## 4. Update `landing.html` with enhanced SEO
- [ ] Override `{% block og_tags %}` with landing-specific tags (more descriptive, CTA-driven)
- [ ] Add `keywords` with hero terms
- [ ] Add `<link rel="canonical" href="{{ site_url }}/">`

## 5. Verify behavior
- [ ] Test: All pages have `og:title`, `og:description`, `og:url`, `og:image`, `twitter:card`
- [ ] Test: Centro detail page shows correct centro name in OG tags
- [ ] Test: Canonical URL present and correct on all pages
- [ ] Test: `SITE_URL` env var overrides default URL
- [ ] Test: No functional/visual regressions on any page