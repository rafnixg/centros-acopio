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
            <div class="meta">📍 ${escapeHtml(c.ciudad)}, ${escapeHtml(c.estado)}</div>
            <div class="meta">📞 ${escapeHtml(c.telefono)}</div>
            ${c.horarios ? `<div class="horario">🕐 ${escapeHtml(c.horarios)}</div>` : ""}
            ${tags ? `<div class="productos-tags">${tags}${extras}</div>` : ""}
        </div>`;
    }).join("");
}

// ---------- Cargar centros desde API ----------
async function cargarCentros() {
    const grid = document.getElementById("grid-centros");
    grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:2rem;"><div class="spinner"></div></div>`;

    const params = new URLSearchParams();
    const q = document.getElementById("filtro-q")?.value?.trim();
    const estado = document.getElementById("filtro-estado")?.value;
    const producto = document.getElementById("filtro-producto")?.value;
    const estadoCentro = document.getElementById("filtro-estado-centro")?.value;

    if (q) params.set("q", q);
    if (estado) params.set("estado", estado);
    if (producto) params.set("producto", producto);
    if (estadoCentro) params.set("estado_centro", estadoCentro);

    try {
        const res = await fetch(`${API}?${params.toString()}`);
        if (!res.ok) throw new Error("Error al cargar");
        const centros = await res.json();
        renderCentros(centros);
        cargarEstadisticas();
    } catch (e) {
        console.error(e);
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
        document.getElementById("stat-total").textContent = stats.total;
        document.getElementById("stat-activos").textContent = stats.por_estado_centro?.Activo || 0;
        document.getElementById("stat-llenos").textContent = stats.por_estado_centro?.Lleno || 0;
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

    const data = {
        nombre: form.nombre.value.trim(),
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
    }
});