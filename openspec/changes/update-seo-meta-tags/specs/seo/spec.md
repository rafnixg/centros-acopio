## ADDED Requirements

### Requirement: Open Graph tags for social sharing
**Capability**: seo

Every HTML page SHALL include Open Graph meta tags (`og:title`, `og:description`, `og:url`, `og:image`, `og:site_name`, `og:locale`, `og:type`) to enable rich link previews when shared on WhatsApp, Telegram, Facebook, and other platforms.

#### Scenario: Landing page shared on WhatsApp
- **GIVEN** a user shares `https://centrosacopio.rafnixg.dev/` on WhatsApp
- **WHEN** WhatsApp fetches the page
- **THEN** `og:title` is "Centros de Acopio Venezuela — Emergencia Nacional"
- **AND** `og:description` mentions the directory, donations, and volunteers
- **AND** `og:url` is `https://centrosacopio.rafnixg.dev/`
- **AND** `og:type` is "website"

#### Scenario: Centro detail page shared on Telegram
- **GIVEN** a user shares `/centro/42` on Telegram
- **WHEN** Telegram fetches the page
- **THEN** `og:title` contains the center's name (e.g., "Centro de Acopio Parroquial San José")
- **AND** `og:description` includes the city, estado, and center status (e.g., "Medellín, Antioquia, Colombia · 🟢 Activo")
- **AND** `og:url` is the absolute URL of the detail page

### Requirement: Twitter Card meta tags
**Capability**: seo

Every HTML page SHALL include Twitter Card meta tags (`twitter:card`, `twitter:title`, `twitter:description`, `twitter:site`) to enable rich link summaries on Twitter/X.

#### Scenario: Twitter card renders on directorio share
- **GIVEN** a user shares `/centros` on Twitter/X
- **WHEN** Twitter fetches the page
- **THEN** `twitter:card` is "summary"
- **AND** `twitter:title` matches `og:title`

### Requirement: Meta keywords for search engines
**Capability**: seo

Every HTML page SHALL include a `<meta name="keywords">` tag with page-relevant keywords in Spanish to improve search engine understanding.

#### Scenario: Landing page has relevant keywords
- **GIVEN** a search engine crawls the landing page
- **WHEN** it reads the `<head>`
- **THEN** `meta[name="keywords"]` contains terms like "centros de acopio", "Venezuela", "donaciones"

#### Scenario: Detalle page has centro-specific keywords
- **GIVEN** a search engine crawls `/centro/42`
- **WHEN** it reads the `<head>`
- **THEN** `meta[name="keywords"]` includes the center's name, city, and estado

### Requirement: Canonical URL
**Capability**: seo

Every HTML page SHALL include a `<link rel="canonical">` tag pointing to the canonical/absolute URL of the page to prevent duplicate content issues from query parameters.

#### Scenario: Centros page with query params has canonical URL
- **GIVEN** a user visits `/centros?estado=Miranda&q=Caracas`
- **WHEN** the page renders
- **THEN** `<link rel="canonical" href="https://centrosacopio.rafnixg.dev/centros">` is present

### Requirement: Absolute SITE_URL for OG tags
**Capability**: seo

The backend SHALL expose a `SITE_URL` configuration (defaulting to the production URL, overridable via `SITE_URL` environment variable) and pass it as `site_url` to all template contexts for use in absolute URL construction.

#### Scenario: Production default URL
- **GIVEN** the `SITE_URL` env var is not set
- **WHEN** the server starts
- **THEN** `site_url` defaults to `https://centrosacopio.rafnixg.dev`

#### Scenario: Development override
- **GIVEN** `SITE_URL=http://localhost:8000` is set
- **WHEN** the server starts
- **THEN** all canonical and OG URLs use `http://localhost:8000`