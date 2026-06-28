# Change: Improve SEO and social sharing meta tags across all pages

## Why
Currently the site has minimal SEO and Open Graph tags. Key issues:
1. **No `og:image`** — Social shares (WhatsApp, Telegram, Twitter) show no preview image.
2. **No `twitter:card`** — Twitter/X link shares lack rich card formatting.
3. **No `keywords` meta** — Missing opportunity for search engine relevance.
4. **`/centro/{id}` detail page has static OG tags** — The most-shared pages on social media show generic "Centros de Acopio Venezuela" instead of the specific center's name, estado, and location.
5. **No `canonical` URL** — Pages accessible via multiple URLs risk duplicate content issues.
6. **No `og:url`** — Social platforms can't reliably determine the canonical share URL.

## What Changes
- **`templates/base.html`** — Add `keywords`, `og:site_name`, `twitter:card`, `twitter:site`, and wrap OG tags in a `block og_tags` so child templates can override them.
- **`templates/detalle.html`** — Override `og_tags` block with centro-specific `og:title`, `og:description`, `og:url`, `twitter:title`, `twitter:description`. Description includes center name, estado/ciudad, and status.
- **`templates/landing.html`** — Add `keywords`, `twitter:card`, `canonical` pointing to `/`.
- **Backend (`main.py`)** — Add a `SITE_URL` config (from env var or default) for building absolute URLs in OG tags. Pass `site_url` to all TemplateResponses.

## Impact
- Affected spec: seo (new capability)
- Affected code: `templates/base.html`, `templates/detalle.html`, `templates/landing.html`, `backend/main.py`
- No API changes
- Low risk — only meta tag additions, no visual/functional changes