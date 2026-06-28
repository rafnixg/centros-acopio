# Design: Donut charts with CSS conic-gradient

## Why CSS donut charts instead of a charting library?

- **Zero dependencies** — No Chart.js, D3, or any external library. The project intentionally avoids JS frameworks.
- **Lightweight** — A single `renderDonutChart()` function vs. 50KB+ of a charting library.
- **Dark mode compatible** — CSS variables already handle theming; the donut uses `var(--bg)` for the center hole and `var(--text)` for labels.
- **Responsive** — The donut is a percentage-based conic-gradient, so it scales automatically.

## Donut chart technique

```css
/* Structure: a square div with conic-gradient background + a pseudo-element for the hole */
.donut {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: conic-gradient(
    var(--color-1) 0deg 30deg,
    var(--color-2) 30deg 100deg,
    ...
  );
  position: relative;
}
.donut::after {
  content: '';
  position: absolute;
  width: 65%;
  height: 65%;
  background: var(--bg);
  border-radius: 50%;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}
```

## Color palette

Use a fixed set of 12 distinguishable CSS colors for slices, cycling through them:
`#e74c3c, #3498db, #2ecc71, #f39c12, #9b59b6, #1abc9c, #e67e22, #34495e, #16a085, #c0392b, #2980b9, #27ae60`

For "Otros" use a muted `#95a5a6`.

## Data grouping logic

Items with < 3% of the total value are grouped into "Otros". The slice percentage for each group is computed as `(count / total) * 360` in degrees.

## Mobile adaptation

On screens < 600px, the donut stacks above its legend. On desktop, donut and legend sit side-by-side within the card.

## Implementation plan

1. Add `renderDonutChart()` as a standalone function in the inline script (no external JS file changes since this is only used on the stats page).
2. No backend changes: the `/api/estadisticas` endpoint already returns everything needed.
3. Filtering: use the `ESTADOS_VENEZUELA` array (already passed via Jinja2 context as `estados`) to separate Venezuelan states from country names in `por_estado`.