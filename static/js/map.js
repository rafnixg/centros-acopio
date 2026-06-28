/* ============================================================
   CENTROS DE ACOPIO VENEZUELA — Mapa Leaflet
   ============================================================ */

let mapa = null;
let markersLayer = null;

// Centro aproximado de Venezuela
const CENTRO_VENEZUELA = [8.0, -66.0];
const ZOOM_DEFAULT = 6;

function colorMarker(estado) {
    switch (estado) {
        case "Activo": return "green";
        case "Lleno": return "orange";
        case "Pausado": return "blue";
        case "Cerrado": return "red";
        default: return "grey";
    }
}

function initMapa(centros) {
    // Si ya existe el mapa, solo recargamos marcadores
    if (mapa) {
        cargarMarcadores(centros);
        return;
    }

    mapa = L.map("mapa").setView(CENTRO_VENEZUELA, ZOOM_DEFAULT);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://openstreetmap.org/copyright">OSM</a>',
        maxZoom: 18,
    }).addTo(mapa);

    markersLayer = L.layerGroup().addTo(mapa);
    cargarMarcadores(centros);
}

function cargarMarcadores(centros) {
    if (!markersLayer) return;
    markersLayer.clearLayers();

    const bounds = [];
    let count = 0;

    centros.forEach(c => {
        if (c.latitud && c.longitud) {
            const color = colorMarker(c.estado_centro);
            const icon = L.divIcon({
                className: "custom-marker",
                html: `<div style="
                    width: 24px; height: 24px;
                    background: ${color};
                    border: 3px solid white;
                    border-radius: 50%;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.4);
                "></div>`,
                iconSize: [24, 24],
                iconAnchor: [12, 12],
            });

            const marker = L.marker([c.latitud, c.longitud], { icon })
                .bindPopup(`
                    <strong>${escapeHtml(c.nombre)}</strong><br>
                    📍 ${escapeHtml(c.ciudad)}, ${escapeHtml(c.estado)}${c.pais && c.pais !== 'Venezuela' ? `, ${escapeHtml(c.pais)}` : ''}<br>
                    📞 ${escapeHtml(c.telefono)}<br>
                    🕐 ${c.horarios || "No indicado"}<br>
                    <span style="display:inline-block;padding:2px 8px;border-radius:10px;font-size:12px;font-weight:600;background:${
                        c.estado_centro === "Activo" ? "#d4edda" :
                        c.estado_centro === "Lleno" ? "#fff3cd" :
                        c.estado_centro === "Cerrado" ? "#f8d7da" : "#cce5ff"
                    };color:${
                        c.estado_centro === "Activo" ? "#155724" :
                        c.estado_centro === "Lleno" ? "#856404" :
                        c.estado_centro === "Cerrado" ? "#721c24" : "#004085"
                    }">${c.estado_centro}</span>
                    <br><a href="/centro/${c.id}" style="display:inline-block;margin-top:4px;color:#457b9d;font-weight:600;">Ver detalle →</a>
                `);

            markersLayer.addLayer(marker);
            bounds.push([c.latitud, c.longitud]);
            count++;
        }
    });

    // Ajustar vista si hay marcadores con coordenadas
    if (bounds.length > 0) {
        mapa.fitBounds(bounds, { padding: [30, 30] });
        if (mapa.getZoom() > 15) mapa.setZoom(15);
    } else {
        mapa.setView(CENTRO_VENEZUELA, ZOOM_DEFAULT);
    }
}

function escapeHtml(text) {
    if (!text) return "";
    const d = document.createElement("div");
    d.textContent = text;
    return d.innerHTML;
}