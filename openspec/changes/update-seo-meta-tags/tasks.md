## 1. Add `SITE_URL` to backend config
- [x] In `backend/main.py`, add `SITE_URL = os.environ.get("SITE_URL", "https://centrosacopio.rafnixg.dev")`
- [x] Add `site_url=SITE_URL` to every `TemplateResponse` call across all routes

## 2. Update `base.html` with SEO foundation
- [x] Add `<meta name="keywords">` with general keywords
- [x] Wrap OG tags in `{% block og_tags %}` so child templates can override
- [x] Add `og:url`, `og:site_name`, `og:image` (SVG emoji favicon or placeholder)
- [x] Add `twitter:card`, `twitter:title`, `twitter:description`, `twitter:site`
- [x] Add `<link rel="canonical" href="{{ site_url }}{{ request.url.path }}">`

## 3. Update `detalle.html` with centro-specific OG tags
- [x] Override `{% block og_tags %}` with centro-specific tags
- [x] `og:title` = `{{ centro.nombre }} — Centros de Acopio Venezuela`
- [x] `og:description` = centro name + ciudad + estado + status
- [x] `og:url` = absolute centro URL
- [x] `twitter:title` and `twitter:description` matching OG tags
- [x] `keywords` = centro name, city, estado

## 4. Update `landing.html` with enhanced SEO
- [x] Override OG tags with more descriptive, CTA-driven content
- [x] Add `keywords` with hero terms
- [x] Add `<link rel="canonical" href="{{ site_url }}/">`

## 5. Verify behavior
- [x] Test: All pages have `og:title`, `og:description`, `og:url`, `og:image`, `twitter:card`
- [x] Test: Centro detail page shows correct centro name in OG tags
- [x] Test: Canonical URL present and correct on all pages
- [ ] Test: `SITE_URL` env var overrides default URL
- [ ] Test: No functional/visual regressions on any page