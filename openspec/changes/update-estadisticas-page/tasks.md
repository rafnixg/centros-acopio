## 1. Pass `ESTADOS_VENEZUELA` to the template context
- [x] In `templates/estadisticas.html`, add a `<script>` block in `head_extra` (or inline at top) that sets `window.ESTADOS_VENEZUELA = {{ estados | tojson }};`

## 2. Add `renderDonutChart()` function in the inline script
- [x] Create function `renderDonutChart(containerId, data, valueKey, labelKey, colors)` that:
  - Computes total, filters out items < 3% into "Otros"
  - Builds a `conic-gradient` CSS string with proportional angles
  - Renders the donut div + legend into the container
- [x] Use a palette of 12 distinguishable colors, cycling for items > 12
- [x] "Otros" slice gets muted `#95a5a6`

## 3. Restructure the stats page layout
- [x] Change the 2-column grid to 3-column grid (`grid-template-columns: 1fr 1fr 1fr`)
- [x] Add a third card: "🌍 Centros por País"
- [x] Rename existing "📍 Centros por Estado" to "📍 Centros por Estado (Venezuela)"
- [x] Keep "📦 Productos más solicitados" in the third column
- [x] Ensure responsive: 3 columns → 2 columns → 1 column on mobile

## 4. Wire data into the new layout
- [x] Filter `por_estado` entries: only include keys that exist in `ESTADOS_VENEZUELA`
- [x] Separate `por_pais` entries for their own chart
- [x] Keep "📦 Productos" as horizontal bars (current rendering logic)
- [x] Keep the stats-bar (total / activos / llenos / pausados / cerrados / reportes)
- [x] Keep "🆕 Centros registrados recientemente" section below the 3-column grid

## 5. Verify behavior
- [x] Test: Page loads, donut charts render with correct slices
- [x] Test: No Venezuelan states appear in "Por País" chart
- [x] Test: No country names appear in "Por Estado (Venezuela)" chart
- [x] Test: Small items grouped into "Otros"
- [x] Test: Legend shows correct labels and counts
- [x] Test: Responsive layout (3 columns → 2 → 1)
- [ ] Test: Dark mode — donut hole matches background
- [ ] Test: Productos section still renders with horizontal bars