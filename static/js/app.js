/* ============================================================
   CENTROS DE ACOPIO VENEZUELA — App principal
   ============================================================ */

const API = "/api/centros";

// ---------- Utilidades ----------
function $(sel, ctx = document) { return ctx.querySelector(sel); }

function $$(sel, ctx = document) { return [...ctx.querySelectorAll(sel)]; }

function mostrarToast(msg, tipo = "success") {
    const t = document.getElementById("toast");
    t.textContent = msg;
    t.className = `toast ${tipo} show`;
    clearTimeout(t._timeout);
    t._timeout = setTimeout(() => t.classList.remove("show"), 3500);
}

function formatearFecha(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    return d.toLocaleDateString("es-VE", {
        year: "numeric", month: "long", day: "numeric",
        hour: "2-digit", minute: "2-digit",
    });
}

function badgeClass(estado) {
    const m = { Activo: "badge-activo", Lleno: "badge-lleno", Pausado: "badge-pausado", Cerrado: "badge-cerrado" };
    return m[estado] || "badge-activo";
}

function emojiEstado(estado) {
    const m = { Activo: "🟢", Lleno: "🟡", Pausado: "🔵", Cerrado: "🔴" };
    return m[estado] || "⚪";
}

// ---------- Skeleton Loading ----------
function mostrarSkeleton() {
    const grid = document.getElementById("grid-centros");
    if (!grid) return;
    grid.innerHTML = Array(6).fill(`
        <div class="card-centro skeleton-card" style="pointer-events:none;animation:none;">
            <div class="skeleton skeleton-badge" style="width:70px;height:22px;border-radius:20px;float:right;"></div>
            <div class="skeleton" style="width:70%;height:20px;margin-bottom:12px;"></div>
            <div class="skeleton" style="width:50%;height:14px;margin-bottom:6px;"></div>
            <div class="skeleton" style="width:40%;height:14px;margin-bottom:6px;"></div>
            <div class="skeleton" style="width:30%;height:14px;margin-bottom:12px;"></div>
            <div style="display:flex;gap:6px;margin-top:8px;">
                <div class="skeleton" style="width:60px;height:20px;border-radius:12px;"></div>
                <div class="skeleton" style="width:50px;height:20px;border-radius:12px;"></div>
            </div>
        </div>
    `).join("");
}

// ---------- Sincronizar filtros con URL ----------
function syncFiltersToURL() {
    const params = new URLSearchParams();
    const q = document.getElementById("filtro-q")?.value?.trim();
    const pais = document.getElementById("filtro-pais")?.value;
    const estado = document.getElementById("filtro-estado")?.value;
    const producto = document.getElementById("filtro-producto")?.value;
    const estadoCentro = document.getElementById("filtro-estado-centro")?.value;

    if (q) params.set("q", q);
    if (pais) params.set("pais", pais);
    if (estado) params.set("estado", estado);
    if (producto) params.set("producto", producto);
    if (estadoCentro) params.set("estado_centro", estadoCentro);

    const newUrl = params.toString()
        ? `${window.location.pathname}?${params.toString()}`
        : window.location.pathname;
    window.history.replaceState({}, "", newUrl);
}

function syncFiltersFromURL() {
    const params = new URLSearchParams(window.location.search);
    const qEl = document.getElementById("filtro-q");
    const paisEl = document.getElementById("filtro-pais");
    const estadoEl = document.getElementById("filtro-estado");
    const productoEl = document.getElementById("filtro-producto");
    const estadoCentroEl = document.getElementById("filtro-estado-centro");

    if (qEl && params.has("q")) qEl.value = params.get("q");
    if (paisEl && params.has("pais")) paisEl.value = params.get("pais");
    if (estadoEl && params.has("estado")) estadoEl.value = params.get("estado");
    if (productoEl && params.has("producto")) productoEl.value = params.get("producto");
    if (estadoCentroEl && params.has("estado_centro")) estadoCentroEl.value = params.get("estado_centro");
}

// ---------- Cargar estados por país ----------
async function cargarEstadosPorPais(pais) {
    const estadoSelect = document.getElementById("filtro-estado");
    if (!estadoSelect) return;

    // Si no hay país seleccionado o es Venezuela, usar estados predefinidos
    if (!pais || pais === "Venezuela") {
        try {
            const res = await fetch("/api/estados");
            const estados = await res.json();
            estadoSelect.innerHTML = `<option value="">Todos los estados</option>`
                + estados.map(e => `<option value="${e}">${e}</option>`).join("");
        } catch {
            estadoSelect.innerHTML = `<option value="">Todos los estados</option>`;
        }
        return;
    }

    // Para otros países, mostrar estados disponibles desde la BD
    try {
        const res = await fetch(`/api/centros?pais=${encodeURIComponent(pais)}&limit=1`);
        const centros = await res.json();
        // Obtener estados únicos de los centros de ese país
        const estadosRes = await fetch(`/api/centros?pais=${encodeURIComponent(pais)}`);
        const todos = await estadosRes.json();
        const estadosUnicos = [...new Set(todos.map(c => c.estado))].sort();
        estadoSelect.innerHTML = `<option value="">Todos los estados / regiones</option>`
            + estadosUnicos.map(e => `<option value="${e}">${e}</option>`).join("");
    } catch {
        estadoSelect.innerHTML = `<option value="">Todos los estados / regiones</option>`;
    }
}

// ---------- Renderizar tarjetas ----------
function renderCentros(centros) {
    const grid = document.getElementById("grid-centros");
    const empty = document.getElementById("empty-state");

    if (!centros.length) {
        grid.innerHTML = "";
        empty.style.display = "block";
        return;
    }

    empty.style.display = "none";
    grid.innerHTML = centros.map(c => {
        const productos = safeParseJSON(c.productos, []);
        const tags = productos.slice(0, 4).map(p => `<span class="tag">${p}</span>`).join("");
        const extras = productos.length > 4 ? `<span class="tag">+${productos.length - 4}</span>` : "";

        return `
        <div class="card-centro" onclick="irADetalle(${c.id})">
            <span class="badge-estado ${badgeClass(c.estado_centro)}">
                ${emojiEstado(c.estado_centro)} ${c.estado_centro}
            </span>
            <h3>${escapeHtml(c.nombre)}</h3>
            <div class="meta">📍 ${escapeHtml(c.ciudad)}, ${escapeHtml(c.estado)}${c.pais && c.pais !== 'Venezuela' ? `, <strong>${escapeHtml(c.pais)}</strong>` : ''}</div>
            <div class="meta">📞 ${escapeHtml(c.telefono)}</div>
            ${c.horarios ? `<div class="horario">🕐 ${escapeHtml(c.horarios)}</div>` : ""}
            ${tags ? `<div class="productos-tags">${tags}${extras}</div>` : ""}
        </div>`;
    }).join("");
}

// ---------- Cargar centros desde API ----------
async function cargarCentros() {
    mostrarSkeleton();

    const params = new URLSearchParams();
    const q = document.getElementById("filtro-q")?.value?.trim();
    const pais = document.getElementById("filtro-pais")?.value;
    const estado = document.getElementById("filtro-estado")?.value;
    const producto = document.getElementById("filtro-producto")?.value;
    const estadoCentro = document.getElementById("filtro-estado-centro")?.value;

    if (q) params.set("q", q);
    if (pais) params.set("pais", pais);
    if (estado) params.set("estado", estado);
    if (producto) params.set("producto", producto);
    if (estadoCentro) params.set("estado_centro", estadoCentro);

    syncFiltersToURL();

    try {
        const res = await fetch(`${API}?${params.toString()}`);
        if (!res.ok) throw new Error("Error al cargar");
        const centros = await res.json();
        renderCentros(centros);
        cargarEstadisticas();

        // Sincronizar mapa: inicia si es primera vez, actualiza marcadores siempre
        if (typeof initMapa === "function") initMapa();
        if (typeof cargarMarcadores === "function") cargarMarcadores(centros);
    } catch (e) {
        console.error(e);
        const grid = document.getElementById("grid-centros");
        grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1">
            <div class="emoji">⚠️</div>
            <p>Error al cargar los centros. Intenta de nuevo.</p>
        </div>`;
    }
}

// ---------- Estadísticas ----------
async function cargarEstadisticas() {
    try {
        const res = await fetch("/api/estadisticas");
        const stats = await res.json();
        const elTotal = document.getElementById("stat-total");
        const elActivos = document.getElementById("stat-activos");
        const elLlenos = document.getElementById("stat-llenos");
        if (elTotal) elTotal.textContent = stats.total;
        if (elActivos) elActivos.textContent = stats.por_estado_centro?.Activo || 0;
        if (elLlenos) elLlenos.textContent = stats.por_estado_centro?.Lleno || 0;
    } catch (e) { /* silencioso */ }
}

// ---------- Registro de centro ----------
async function enviarRegistro(e) {
    e.preventDefault();
    const form = e.target;
    const btn = form.querySelector("button[type='submit']");
    btn.disabled = true;
    btn.innerHTML = "⏳ Guardando...";

    const productos = $$("input[name='productos']:checked").map(cb => cb.value);
    const otros = document.getElementById("producto-otros")?.value?.trim();
    if (otros) productos.push(`Otros: ${otros}`);

    const latitud = form.latitud?.value ? parseFloat(form.latitud.value) : null;
    const longitud = form.longitud?.value ? parseFloat(form.longitud.value) : null;

    const data = {
        nombre: form.nombre.value.trim(),
        pais: form.pais?.value || "Venezuela",
        estado: form.estado.value,
        ciudad: form.ciudad.value.trim(),
        direccion: form.direccion.value.trim(),
        telefono: form.telefono.value.trim(),
        responsable: form.responsable.value.trim(),
        horarios: form.horarios.value.trim(),
        productos: JSON.stringify(productos),
        activo: form.activo?.checked ?? true,
        estado_centro: form.estado_centro.value,
        email: form.email?.value?.trim() || "",
        redes: form.redes?.value?.trim() || "",
        notas: form.notas?.value?.trim() || "",
        latitud: latitud,
        longitud: longitud,
    };

    try {
        const res = await fetch(API, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Error al guardar");
        }

        const centro = await res.json();
        mostrarToast("✅ Centro registrado con éxito!", "success");
        form.reset();
        setTimeout(() => { window.location.href = `/centro/${centro.id}`; }, 1200);
    } catch (e) {
        console.error(e);
        mostrarToast("❌ " + e.message, "error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = "💾 Guardar Centro de Acopio";
    }
}

// ---------- Gestión dinámica de Estado/Región según país ----------
function gestionarCampoEstado(pais) {
    const container = document.getElementById("estado-container");
    if (!container) return;

    if (pais === "Venezuela") {
        container.innerHTML = `<select name="estado" id="estado" required>
            <option value="">Selecciona un estado...</option>
            ${(window.ESTADOS_VENEZUELA || []).map(e => `<option value="${e}">${e}</option>`).join("")}
        </select>`;
    } else {
        container.innerHTML = `<input type="text" name="estado" id="estado" required
            placeholder="Ej: Madrid, Antioquia, Texas...">`;
    }
}

// ---------- Geocodificación automática ----------
let geocodingTimer = null;

function initGeocoding() {
    const dirInput = document.getElementById("direccion");
    const ciudadInput = document.getElementById("ciudad");
    const estadoSelect = document.getElementById("estado");
    const latInput = document.querySelector("input[name='latitud']");
    const lngInput = document.querySelector("input[name='longitud']");

    if (!dirInput || !latInput) return;

    async function autoGeocode() {
        const dir = dirInput.value.trim();
        const ciudad = ciudadInput?.value?.trim();
        const estado = estadoSelect?.value;

        if (!dir && !ciudad) return;

        clearTimeout(geocodingTimer);
        geocodingTimer = setTimeout(async () => {
            try {
                const res = await fetch("/api/geocodificar", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ direccion: dir, ciudad, estado }),
                });
                const data = await res.json();
                if (data.latitud && data.longitud) {
                    latInput.value = data.latitud.toFixed(4);
                    lngInput.value = data.longitud.toFixed(4);
                }
            } catch (e) { /* silencioso */ }
        }, 800);
    }

    dirInput.addEventListener("input", autoGeocode);
    if (ciudadInput) ciudadInput.addEventListener("input", autoGeocode);
    if (estadoSelect) estadoSelect.addEventListener("change", autoGeocode);
}

// ---------- Navegación ----------
function irADetalle(id) {
    window.location.href = `/centro/${id}`;
}

// ---------- Helpers ----------
function safeParseJSON(str, fallback) {
    try { return JSON.parse(str); } catch { return fallback; }
}

function escapeHtml(text) {
    if (!text) return "";
    const d = document.createElement("div");
    d.textContent = text;
    return d.innerHTML;
}

// ---------- Inicialización ----------
document.addEventListener("DOMContentLoaded", () => {
    // Página principal
    const grid = document.getElementById("grid-centros");
    if (grid) {
        // Cargar estados cuando cambia el país
        const filtroPais = document.getElementById("filtro-pais");
        if (filtroPais) {
            filtroPais.addEventListener("change", () => {
                cargarEstadosPorPais(filtroPais.value);
                cargarCentros();
            });
        }

        syncFiltersFromURL();

        // Cargar estados según el país inicial de la URL
        if (filtroPais) {
            cargarEstadosPorPais(filtroPais.value);
        }

        cargarCentros();

        // Filtros con debounce
        const filtroQ = document.getElementById("filtro-q");
        if (filtroQ) {
            let timer;
            filtroQ.addEventListener("input", () => {
                clearTimeout(timer);
                timer = setTimeout(cargarCentros, 300);
            });
        }

        $$("#filtro-estado, #filtro-producto, #filtro-estado-centro").forEach(el => {
            if (el) el.addEventListener("change", cargarCentros);
        });
    }

    // Formulario de registro
    const formRegistro = document.getElementById("form-registro");
    if (formRegistro) {
        formRegistro.addEventListener("submit", enviarRegistro);
        initGeocoding();

        // Campo Estado/Región dinámico según país
        const paisSelect = document.getElementById("pais");
        if (paisSelect) {
            gestionarCampoEstado(paisSelect.value);
            paisSelect.addEventListener("change", () => gestionarCampoEstado(paisSelect.value));
        }
    }
});