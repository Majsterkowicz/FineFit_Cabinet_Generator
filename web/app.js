"use strict";

const state = {
    config: null,
    projects: [],
    project: null,
    tab: "sections"
};

/* ---------------------------------------------------------------- API --- */

async function api(method, url, body) {

    const response = await fetch(url, {
        method,
        headers: body ? { "Content-Type": "application/json" } : {},
        body: body ? JSON.stringify(body) : undefined
    });

    if (!response.ok) {
        let detail = `Błąd ${response.status}`;
        try {
            const data = await response.json();
            if (typeof data.detail === "string") {
                detail = data.detail;
            } else if (Array.isArray(data.detail)) {
                detail = data.detail.map(item => item.msg).join(", ");
            }
        } catch (error) { /* odpowiedź bez treści JSON */ }
        throw new Error(detail);
    }

    return response.status === 204 ? null : response.json();
}

/* ------------------------------------------------------------ helpers --- */

const $ = selector => document.querySelector(selector);

/* Widok powitalny (pusty workspace) zapamiętany z index.html - jedno źródło
   znaczników, przywracane po zamknięciu/usunięciu aktywnego projektu. */
const EMPTY_WORKSPACE = $("#workspace").innerHTML;

/* Adresy i wyszukiwanie obiektów w bieżącym projekcie.
   cabinet_id jest unikalne w projekcie, więc sekcję odnajdujemy sami
   zamiast przenosić ją przez atrybuty DOM. */

const projectUrl = () => `/api/projects/${state.project.project_id}`;

function findSection(sectionId) {
    return state.project.sections.find(
        section => section.section_id === sectionId);
}

function sectionOfCabinet(cabinetId) {
    return state.project.sections.find(section => section.cabinets.some(
        cabinet => cabinet.cabinet_id === cabinetId));
}

function findCabinet(cabinetId) {
    return sectionOfCabinet(cabinetId).cabinets.find(
        cabinet => cabinet.cabinet_id === cabinetId);
}

function cabinetUrl(cabinetId) {
    const section = sectionOfCabinet(cabinetId);
    return `${projectUrl()}/sections/${section.section_id}` +
        `/cabinets/${cabinetId}`;
}

function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, character => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;",
        '"': "&quot;", "'": "&#39;"
    }[character]));
}

function toast(message, isError) {
    const element = $("#toast");
    element.textContent = message;
    element.classList.toggle("bad", Boolean(isError));
    element.hidden = false;
    clearTimeout(element.timer);
    element.timer = setTimeout(() => { element.hidden = true; }, 2800);
}

function openModal(html) {
    $("#modal").innerHTML = html;
    $("#modal-backdrop").hidden = false;
}

function closeModal() {
    $("#modal-backdrop").hidden = true;
    $("#modal").innerHTML = "";
}

/**
 * Okno z jednym polem tekstowym.
 * submit(value) zgłasza wyjątek, którego komunikat trafia do #modal-error.
 */
function textModal({ title, label, value = "", placeholder = "",
                     button, submit }) {

    openModal(`
        <h2>${escapeHtml(title)}</h2>
        <label for="modal-input">${escapeHtml(label)}</label>
        <input id="modal-input" autofocus value="${escapeHtml(value)}"
            placeholder="${escapeHtml(placeholder)}">
        <div class="error" id="modal-error"></div>
        <div class="modal-actions">
            <button onclick="closeModal()">Anuluj</button>
            <button class="primary" id="modal-save">${escapeHtml(button)}</button>
        </div>
    `);

    const run = async () => {
        try {
            await submit($("#modal-input").value);
            closeModal();
        } catch (error) {
            $("#modal-error").textContent = error.message;
        }
    };

    $("#modal-save").addEventListener("click", run);
    $("#modal-input").addEventListener("keydown", event => {
        if (event.key === "Enter") run();
    });
}

/** confirm -> DELETE -> odświeżenie -> komunikat. */
async function confirmDelete(question, url, message) {

    if (!confirm(question)) return;

    try {
        await api("DELETE", url);
        await refresh();
        toast(message);
    } catch (error) {
        toast(error.message, true);
    }
}

$("#modal-backdrop").addEventListener("click", event => {
    if (event.target.id === "modal-backdrop") closeModal();
});

document.addEventListener("keydown", event => {
    if (event.key === "Escape") closeModal();
});

/* -------------------------------------------------------------- theme --- */

const savedTheme = localStorage.getItem("finefit-theme");
if (savedTheme) document.documentElement.dataset.theme = savedTheme;

$("#theme-toggle").addEventListener("click", () => {
    const next = document.documentElement.dataset.theme === "light"
        ? "dark" : "light";
    document.documentElement.dataset.theme = next;
    localStorage.setItem("finefit-theme", next);
});

/* ------------------------------------------------------------ projects --- */

async function loadProjects() {
    state.projects = await api("GET", "/api/projects");
    renderProjectList();
}

function setProject(project) {
    state.project = project;
    renderProjectList();
    render();
}

function renderProjectList() {

    $("#project-list").innerHTML = state.projects.map(project => `
        <button class="project-item ${
            state.project && state.project.project_id === project.project_id
                ? "active" : ""
        }" data-id="${project.project_id}">
            <div>${escapeHtml(project.project_name)}</div>
            <div class="id">${project.project_id} ·
                ${project.sections} sekcji · ${project.cabinets} szafek</div>
        </button>
    `).join("") || `<p class="muted">Brak projektów.</p>`;

    document.querySelectorAll(".project-item").forEach(button => {
        button.addEventListener("click", () => openProject(button.dataset.id));
    });
}

async function openProject(projectId) {
    setProject(await api("GET", `/api/projects/${projectId}`));
}

async function refresh() {

    if (!state.project) {
        await loadProjects();
        return;
    }

    // oba żądania są niezależne - pobieramy je równolegle
    const [project, projects] = await Promise.all([
        api("GET", `/api/projects/${state.project.project_id}`),
        api("GET", "/api/projects")
    ]);

    state.projects = projects;
    setProject(project);
}

$("#new-project").addEventListener("click", () => textModal({
    title: "Nowy projekt",
    label: "Nazwa projektu",
    placeholder: "np. Karolina - Kuchnia",
    button: "Utwórz",
    submit: async name => {
        // odpowiedź POST to kompletny projekt - nie pobieramy go ponownie
        const project = await api("POST", "/api/projects", {
            project_name: name
        });
        await loadProjects();
        setProject(project);
        toast("Projekt utworzony");
    }
}));

/* Usuwa aktywny projekt. Nie korzystamy z confirmDelete, bo ono nie czyści
   zaznaczenia - po usunięciu wracamy do widoku powitalnego przez
   setProject(null). */
async function deleteProject() {

    const project = state.project;

    if (!confirm(
        `Usunąć projekt „${project.project_name}" wraz z całą zawartością?`
    )) return;

    try {
        await api("DELETE", `/api/projects/${project.project_id}`);

        await loadProjects();
        setProject(null);
        toast("Projekt usunięty");

    } catch (error) {
        toast(error.message, true);
    }
}

/* --------------------------------------------------------------- views --- */

function render() {

    if (!state.project) {
        $("#workspace").innerHTML = EMPTY_WORKSPACE;
        return;
    }

    const project = state.project;

    const cabinets = countCabinets(project);

    $("#workspace").innerHTML = `
        <div class="panel">
            <div class="panel-head">
                <div>
                    <h2>${escapeHtml(project.project_name)}</h2>
                    <p class="muted mono">${project.project_id} ·
                        utworzono ${escapeHtml(project.created_at)}</p>
                </div>
                <div class="row">
                    <div class="tabs">
                        <button class="tab ${state.tab === "sections" ? "active" : ""}"
                            data-tab="sections">Sekcje i szafki</button>
                        <button class="tab ${state.tab === "cutting" ? "active" : ""}"
                            data-tab="cutting">Lista rozkroju</button>
                    </div>
                    <button class="small" id="print-sheet">Drukuj / PDF</button>
                    <button class="small danger" id="delete-project">
                        Usuń projekt</button>
                </div>
            </div>
            <div class="panel-body">
                <div class="stats">
                    <div class="stat"><div class="key">Sekcje</div>
                        <div class="value">${project.sections.length}</div></div>
                    <div class="stat"><div class="key">Szafki</div>
                        <div class="value">${cabinets}</div></div>
                    <div class="stat"><div class="key">Formatki</div>
                        <div class="value">${countParts(project)}</div></div>
                </div>
            </div>
        </div>
        <div id="tab-content"></div>
    `;

    document.querySelectorAll(".tab").forEach(button => {
        button.addEventListener("click", () => {
            state.tab = button.dataset.tab;
            render();
        });
    });

    $("#delete-project").addEventListener("click", deleteProject);
    $("#print-sheet").addEventListener("click", printProductionSheet);

    if (state.tab === "sections") renderSections();
    else renderCuttingList();
}

function countParts(project) {
    let total = 0;
    for (const section of project.sections) {
        for (const cabinet of section.cabinets) {
            for (const part of cabinet.parts) total += part.quantity;
        }
    }
    return total;
}

const countCabinets = project => project.sections.reduce(
    (total, section) => total + section.cabinets.length, 0);

const countCabinetParts = cabinet => cabinet.parts.reduce(
    (total, part) => total + part.quantity, 0);

function renderSections() {

    const project = state.project;

    const sections = project.sections.map(section => `
        <div class="panel">
            <div class="panel-head">
                <div>
                    <h3>${section.section_number}. ${escapeHtml(section.section_name)}</h3>
                    <p class="muted mono">${section.section_id} ·
                        ${section.cabinets.length} szafek</p>
                </div>
                <div class="row">
                    <button class="small" data-add-cabinet="${section.section_id}">
                        + Szafka</button>
                    <button class="small" data-rename="${section.section_id}">
                        Zmień nazwę</button>
                    <button class="small danger" data-del-section="${section.section_id}">
                        Usuń</button>
                </div>
            </div>
            <div class="panel-body">
                ${section.cabinets.length
                    ? `<div class="elevation">${drawElevation(section)}</div>`
                    : ""}
                <div class="cards" style="margin-top:12px">
                    ${section.cabinets.map(cabinetCard).join("")
                      || `<p class="muted">Sekcja nie zawiera jeszcze szafek.</p>`}
                </div>
            </div>
        </div>
    `).join("");

    $("#tab-content").innerHTML = `
        <div class="panel">
            <div class="panel-head">
                <h2>Sekcje</h2>
                <button class="primary small" id="add-section">+ Dodaj sekcję</button>
            </div>
        </div>
        ${sections || `<div class="empty"><h2>Brak sekcji</h2>
            <p class="muted">Dodaj pierwszą sekcję, aby rozpocząć.</p></div>`}
    `;

    $("#add-section").addEventListener("click", sectionModal);

    bind("add-cabinet", sectionId => cabinetModal(sectionId, null));
    bind("rename", renameSectionModal);
    bind("del-section", deleteSection);
    bind("edit-cabinet", cabinetId => cabinetModal(null, cabinetId));
    bind("del-cabinet", deleteCabinet);
}

/** Podpina obsługę kliknięcia do wszystkich [data-<name>] i przekazuje ich wartość. */
function bind(name, handler) {
    document.querySelectorAll(`[data-${name}]`).forEach(button => {
        button.addEventListener("click",
            () => handler(button.getAttribute(`data-${name}`)));
    });
}

function cabinetCard(cabinet) {

    const pieces = countCabinetParts(cabinet);
    const id = cabinet.cabinet_id;

    return `
        <div class="card">
            <div class="row spread">
                <span class="label">${cabinet.cabinet_label}</span>
                <span class="badge">${escapeHtml(cabinet.cabinet_type)}</span>
            </div>
            <p class="muted mono" style="margin:6px 0">
                ${cabinet.width} × ${cabinet.height} × ${cabinet.depth} mm</p>
            <p class="muted">${cabinet.shelves} półek ·
                ${cabinet.fronts} frontów · ${pieces} formatek</p>
            <div class="row" style="margin-top:10px">
                <button class="small" data-edit-cabinet="${id}">Edytuj</button>
                <button class="small danger" data-del-cabinet="${id}">Usuń</button>
            </div>
        </div>
    `;
}

/* ---------------------------------------------------------- elevation --- */

function drawElevation(section) {

    const cabinets = section.cabinets;
    if (!cabinets.length) return "";

    const gap = 4;
    const padding = 34;

    const totalWidth = cabinets.reduce((sum, c) => sum + c.width, 0)
        + gap * (cabinets.length - 1);
    const maxHeight = Math.max(...cabinets.map(c => c.height));

    const scale = Math.min(
        (1000 - padding * 2) / totalWidth,
        320 / maxHeight
    );

    const canvasWidth = totalWidth * scale + padding * 2;
    const canvasHeight = maxHeight * scale + padding * 2;
    const baseline = canvasHeight - padding;

    // init() pobiera konfigurację zanim cokolwiek się wyrenderuje
    const frontGap = state.config.front_gap;
    const thickness = state.config.board_thickness;

    let x = padding;
    let svg = "";
    let previousHeight = null;

    for (const cabinet of cabinets) {

        const w = cabinet.width * scale;
        const h = cabinet.height * scale;
        const y = baseline - h;

        svg += `<rect class="body-line" x="${x}" y="${y}"
            width="${w}" height="${h}" rx="1"/>`;

        // półki
        const inner = cabinet.height - 2 * thickness;
        for (let i = 1; i <= cabinet.shelves; i++) {
            const shelfY = baseline - (thickness + inner * i /
                (cabinet.shelves + 1)) * scale;
            svg += `<line class="shelf-line" x1="${x + 2}" y1="${shelfY}"
                x2="${x + w - 2}" y2="${shelfY}"/>`;
        }

        // fronty
        if (cabinet.fronts > 0) {
            const frontWidth =
                (cabinet.width - (cabinet.fronts - 1) * frontGap)
                / cabinet.fronts;
            for (let i = 0; i < cabinet.fronts; i++) {
                const fx = x + i * (frontWidth + frontGap) * scale;
                svg += `<rect class="front-face" x="${fx + 1}" y="${y + 1}"
                    width="${frontWidth * scale - 2}" height="${h - 2}" rx="1"/>`;
            }
        }

        svg += `<text class="cab-text" x="${x + w / 2}" y="${baseline + 14}"
            text-anchor="middle">${cabinet.cabinet_label}</text>`;
        svg += `<text class="dim-text" x="${x + w / 2}" y="${baseline + 26}"
            text-anchor="middle">${cabinet.width}</text>`;
        // wysokość opisujemy tylko przy zmianie, aby opisy się nie nakładały
        if (cabinet.height !== previousHeight) {
            svg += `<text class="dim-text" x="${x - 4}" y="${y + 10}"
                text-anchor="end">${cabinet.height}</text>`;
            previousHeight = cabinet.height;
        }

        x += w + gap * scale;
    }

    svg += `<line class="shelf-line" x1="${padding - 8}" y1="${baseline}"
        x2="${canvasWidth - padding + 8}" y2="${baseline}"/>`;

    return `<svg viewBox="0 0 ${canvasWidth} ${canvasHeight}"
        width="${canvasWidth}" height="${canvasHeight}"
        xmlns="http://www.w3.org/2000/svg">${ELEVATION_STYLE}${svg}</svg>`;
}

/* Styl elewacji zawarty w samym SVG - jedno źródło dla ekranu i druku.
   var(--x, fallback): na ekranie kolory motywu, w oknie druku (bez motywu)
   jasne wartości zapasowe. Dzięki temu nie ma kopii w style.css/PRINT_CSS. */
const ELEVATION_STYLE = `<style>
    .body-line { fill: none; stroke: var(--text, #14161b); stroke-width: 1.5; }
    .front-face { fill: var(--accent-soft, #f0f0f0);
        stroke: var(--accent, #14161b); stroke-width: 1; }
    .shelf-line { stroke: var(--muted, #888); stroke-width: 1;
        stroke-dasharray: 4 3; }
    .dim-text { fill: var(--muted, #555); font-size: 10px;
        font-family: ui-monospace, monospace; }
    .cab-text { fill: var(--text, #14161b); font-size: 11px;
        font-family: ui-monospace, monospace; }
</style>`;

/* -------------------------------------------------------------- modals --- */

function sectionModal() {
    textModal({
        title: "Nowa sekcja",
        label: "Nazwa sekcji",
        placeholder: "np. Ściana lewa",
        button: "Dodaj",
        submit: async name => {
            await api("POST", `${projectUrl()}/sections`,
                { section_name: name });
            await refresh();
            toast("Sekcja dodana");
        }
    });
}

function renameSectionModal(sectionId) {

    const section = findSection(sectionId);

    textModal({
        title: "Zmień nazwę sekcji",
        label: "Nazwa sekcji",
        value: section.section_name,
        button: "Zapisz",
        submit: async name => {
            await api("PATCH", `${projectUrl()}/sections/${sectionId}`,
                { section_name: name });
            await refresh();
            toast("Nazwa zmieniona");
        }
    });
}

function deleteSection(sectionId) {
    return confirmDelete(
        "Usunąć sekcję wraz z szafkami?",
        `${projectUrl()}/sections/${sectionId}`,
        "Sekcja usunięta"
    );
}

function deleteCabinet(cabinetId) {
    return confirmDelete(
        "Usunąć szafkę?",
        cabinetUrl(cabinetId),
        "Szafka usunięta"
    );
}


function cabinetModal(sectionId, cabinetId) {

    // przy edycji sekcję wyznacza sama szafka
    const cabinet = cabinetId ? findCabinet(cabinetId) : null;
    const section = cabinet
        ? sectionOfCabinet(cabinetId)
        : findSection(sectionId);

    const types = state.config.cabinet_types;
    const current = cabinet || types[0];

    openModal(`
        <h2>${cabinet ? `Edycja szafki ${cabinet.cabinet_label}`
            : `Nowa szafka w sekcji ${section.section_number}`}</h2>
        <label for="cabinet-type">Typ szafki</label>
        <select id="cabinet-type">
            ${types.map(type => `<option value="${type.name}"
                ${current.cabinet_type === type.name ? "selected" : ""}>
                ${type.name}</option>`).join("")}
        </select>
        <div class="grid" style="margin-top:14px">
            <div><label for="width">Szerokość</label>
                <input id="width" type="number" value="${current.width}"></div>
            <div><label for="height">Wysokość</label>
                <input id="height" type="number" value="${current.height}"></div>
            <div><label for="depth">Głębokość</label>
                <input id="depth" type="number" value="${current.depth}"></div>
            <div><label for="shelves">Półki</label>
                <input id="shelves" type="number" value="${current.shelves}"></div>
            <div><label for="fronts">Fronty</label>
                <input id="fronts" type="number" value="${current.fronts}"></div>
        </div>
        <p class="muted" style="margin-top:12px">
            Formatki zostaną wygenerowane automatycznie.</p>
        <div class="error" id="modal-error"></div>
        <div class="modal-actions">
            <button onclick="closeModal()">Anuluj</button>
            <button class="primary" id="modal-save">
                ${cabinet ? "Zapisz" : "Dodaj"}</button>
        </div>
    `);

    // zmiana typu podstawia wymiary domyślne (tylko przy tworzeniu)
    $("#cabinet-type").addEventListener("change", event => {
        if (cabinet) return;
        const type = types.find(item => item.name === event.target.value);
        $("#width").value = type.width;
        $("#height").value = type.height;
        $("#depth").value = type.depth;
        $("#shelves").value = type.shelves;
        $("#fronts").value = type.fronts;
    });

    $("#modal-save").addEventListener("click", async () => {

        const payload = {
            cabinet_type: $("#cabinet-type").value,
            width: Number($("#width").value),
            height: Number($("#height").value),
            depth: Number($("#depth").value),
            shelves: Number($("#shelves").value),
            fronts: Number($("#fronts").value)
        };

        try {
            if (cabinet) await api("PUT", cabinetUrl(cabinetId), payload);
            else await api("POST",
                `${projectUrl()}/sections/${section.section_id}/cabinets`,
                payload);
            closeModal();
            await refresh();
            toast(cabinet ? "Szafka zaktualizowana" : "Szafka dodana");
        } catch (error) {
            $("#modal-error").textContent = error.message;
        }
    });
}

/* -------------------------------------------------------- cutting list --- */

/* Jeden wiersz listy rozkroju - wspólny dla widoku ekranu i arkusza druku. */
const cuttingRow = row => `
    <tr><td>${escapeHtml(row.part_name)}</td>
        <td class="num">${row.length}</td><td class="num">${row.width}</td>
        <td class="num">${row.thickness}</td><td class="num">${row.quantity}</td>
        <td class="num">${row.area.toFixed(3)}</td>
        <td>${escapeHtml(row.material)}</td></tr>`;

async function renderCuttingList() {

    $("#tab-content").innerHTML = `<div class="panel"><div class="panel-body">
        <p class="muted">Wczytywanie...</p></div></div>`;

    // lista rozkroju i wycena są niezależne - pobieramy je równolegle
    const [data, pricing] = await Promise.all([
        api("GET", `${projectUrl()}/cutting-list`),
        api("GET", `${projectUrl()}/pricing`)
    ]);

    const rows = data.rows.map(cuttingRow).join("");

    $("#tab-content").innerHTML = `
        <div class="panel">
            <div class="panel-head">
                <h2>Lista rozkroju</h2>
                <button class="small" id="export-csv">Eksport CSV</button>
            </div>
            <div class="panel-body">
                <div class="stats" style="margin-bottom:14px">
                    <div class="stat"><div class="key">Formatek</div>
                        <div class="value">${data.summary.total_parts}</div></div>
                    <div class="stat"><div class="key">Powierzchnia</div>
                        <div class="value">${data.summary.total_area} m²</div></div>
                    <div class="stat"><div class="key">Obrzeże</div>
                        <div class="value">${data.summary.edging_length} m</div></div>
                </div>
                <div class="table-scroll">
                    <table>
                        <thead><tr>
                            <th>Element</th><th class="num">Długość</th>
                            <th class="num">Szerokość</th><th class="num">Grubość</th>
                            <th class="num">Szt.</th><th class="num">m²</th>
                            <th>Materiał</th>
                        </tr></thead>
                        <tbody>${rows || `<tr><td colspan="7">
                            <span class="muted">Brak formatek.</span></td></tr>`}</tbody>
                    </table>
                </div>
            </div>
        </div>
        ${pricingPanel(pricing)}
    `;

    $("#export-csv").addEventListener("click", () => exportCsv(data.rows));
    $("#edit-prices").addEventListener("click", () => pricesModal(pricing));
}

/* Panel wyceny - materiał, obrzeże i okucia w jednej tabeli kosztów.
   Ceny są orientacyjne (konfiguracja src/config.py). */
function pricingPanel(pricing) {

    const money = value => `${value.toFixed(2)} ${pricing.currency}`;

    const line = (name, detail, unitPrice, cost) => `
        <tr>
            <td>${escapeHtml(name)}</td>
            <td class="num">${detail}</td>
            <td class="num">${unitPrice}</td>
            <td class="num">${money(cost)}</td>
        </tr>`;

    const rows = [
        ...pricing.materials.map(item => line(
            item.material, `${item.area} m²`,
            `${item.unit_price} /m²`, item.cost)),
        line("Obrzeże", `${pricing.edging.length} m`,
            `${pricing.edging.unit_price} /m`, pricing.edging.cost),
        ...pricing.hardware.map(item => line(
            item.name, `${item.quantity} szt.`,
            `${item.unit_price} /szt.`, item.cost)),
    ].join("");

    return `
        <div class="panel">
            <div class="panel-head">
                <h2>Wycena</h2>
                <div class="row">
                    <span class="badge">${money(pricing.total)}</span>
                    <button class="small" id="edit-prices">Edytuj ceny</button>
                </div>
            </div>
            <div class="panel-body">
                <div class="table-scroll">
                    <table>
                        <thead><tr>
                            <th>Pozycja</th><th class="num">Ilość</th>
                            <th class="num">Cena jedn.</th>
                            <th class="num">Koszt</th>
                        </tr></thead>
                        <tbody>
                            ${rows}
                            <tr class="total-row">
                                <td colspan="3"><strong>Razem</strong></td>
                                <td class="num"><strong>${money(pricing.total)}</strong></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <p class="muted" style="margin-top:10px">
                    Ceny orientacyjne. Konfiguracja w src/config.py.</p>
            </div>
        </div>
    `;
}

function exportCsv(rows) {

    const header = "Element;Dlugosc;Szerokosc;Grubosc;Sztuk;m2;Material";

    const body = rows.map(row => [
        row.part_name, row.length, row.width, row.thickness,
        row.quantity, row.area, row.material
    ].join(";")).join("\n");

    const blob = new Blob(["﻿" + header + "\n" + body],
        { type: "text/csv;charset=utf-8" });

    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${state.project.project_id}_rozkroj.csv`;
    link.click();
    URL.revokeObjectURL(link.href);
}

/* --------------------------------------------------- production sheet --- */

/* Arkusz produkcyjny: elewacje + lista rozkroju + BOM + wycena na jednej
   drukowalnej stronie. Otwieramy dedykowany dokument (jasny motyw, własny
   arkusz stylów) i uruchamiamy okno druku - użytkownik zapisuje jako PDF. */
async function printProductionSheet() {

    try {
        // lista rozkroju i wycena są niezależne - pobieramy równolegle
        const [cutting, pricing] = await Promise.all([
            api("GET", `${projectUrl()}/cutting-list`),
            api("GET", `${projectUrl()}/pricing`),
        ]);

        const html = productionSheetHtml({
            project: state.project, cutting, pricing,
        });

        const printWindow = window.open("", "_blank");

        if (!printWindow) {
            toast("Zezwól na wyskakujące okna, aby wydrukować.", true);
            return;
        }

        printWindow.document.write(html);
        printWindow.document.close();

    } catch (error) {
        toast(error.message, true);
    }
}

/* Czysta funkcja (dane -> HTML), aby układ dało się sprawdzić bez przeglądarki. */
function productionSheetHtml({ project, cutting, pricing }) {

    const date = new Date().toLocaleDateString("pl-PL");

    const cabinetsCount = countCabinets(project);

    const sections = [...project.sections]
        .sort((a, b) => a.section_number - b.section_number)
        .map(sheetSection).join("");

    const cuttingRows = cutting.rows.map(cuttingRow).join("");

    const bomRows = cutting.summary.materials.map(entry => `
        <tr><td>${escapeHtml(entry.material)}</td>
            <td class="num">${entry.quantity}</td>
            <td class="num">${entry.area} m²</td></tr>`).join("");

    const money = value => `${value.toFixed(2)} ${pricing.currency}`;

    const priceRows = [
        ...pricing.materials.map(item =>
            priceRow(item.material, `${item.area} m²`, money(item.cost))),
        priceRow("Obrzeże", `${pricing.edging.length} m`, money(pricing.edging.cost)),
        ...pricing.hardware.map(item =>
            priceRow(item.name, `${item.quantity} szt.`, money(item.cost))),
    ].join("");

    return `<!doctype html>
<html lang="pl"><head><meta charset="utf-8">
<title>Arkusz produkcyjny ${escapeHtml(project.project_id)}</title>
<style>${PRINT_CSS}</style></head>
<body onload="window.focus();window.print()">

    <header class="sheet-head">
        <h1>Arkusz produkcyjny</h1>
        <div class="sheet-meta">
            <div class="pid">${escapeHtml(project.project_id)}</div>
            <div>${escapeHtml(project.project_name)}</div>
            <div class="muted">${date}</div>
        </div>
    </header>

    <p class="totals">Sekcje: ${project.sections.length} ·
        Szafki: ${cabinetsCount} · Formatki: ${countParts(project)}</p>

    ${sections || `<p class="muted">Projekt nie zawiera sekcji.</p>`}

    <h2>Lista rozkroju</h2>
    <table><thead><tr>
        <th>Element</th><th class="num">Dł.</th><th class="num">Szer.</th>
        <th class="num">Gr.</th><th class="num">Szt.</th><th class="num">m²</th>
        <th>Materiał</th></tr></thead>
        <tbody>${cuttingRows || emptyRow(7)}</tbody></table>

    <h2>Zestawienie materiałów (BOM)</h2>
    <table><thead><tr>
        <th>Materiał</th><th class="num">Szt.</th><th class="num">Powierzchnia</th>
        </tr></thead><tbody>${bomRows || emptyRow(3)}</tbody></table>
    <p class="muted">Powierzchnia razem: ${cutting.summary.total_area} m² ·
        Obrzeże: ${cutting.summary.edging_length} m</p>

    <h2>Wycena</h2>
    <table><thead><tr>
        <th>Pozycja</th><th class="num">Ilość</th><th class="num">Koszt</th>
        </tr></thead><tbody>${priceRows}
        <tr class="total"><td colspan="2"><strong>Razem</strong></td>
        <td class="num"><strong>${money(pricing.total)}</strong></td></tr>
        </tbody></table>

</body></html>`;
}

function sheetSection(section) {

    const cabinets = section.cabinets.map(cabinet => `
        <tr><td>${escapeHtml(cabinet.cabinet_label)}</td>
            <td>${escapeHtml(cabinet.cabinet_type)}</td>
            <td class="num">${cabinet.width}×${cabinet.height}×${cabinet.depth}</td>
            <td class="num">${cabinet.shelves}</td>
            <td class="num">${cabinet.fronts}</td>
            <td class="num">${countCabinetParts(cabinet)}</td></tr>`).join("");

    return `<div class="section">
        <h2>${section.section_number}. ${escapeHtml(section.section_name)}</h2>
        ${section.cabinets.length
            ? `<div class="elevation">${drawElevation(section)}</div>` : ""}
        <table><thead><tr>
            <th>Nr</th><th>Typ</th><th class="num">Wymiary [mm]</th>
            <th class="num">Półki</th><th class="num">Fronty</th>
            <th class="num">Formatki</th></tr></thead>
            <tbody>${cabinets || emptyRow(6)}</tbody></table>
    </div>`;
}

const priceRow = (name, detail, cost) => `
    <tr><td>${escapeHtml(name)}</td>
        <td class="num">${detail}</td><td class="num">${cost}</td></tr>`;

const emptyRow = cols =>
    `<tr><td colspan="${cols}" class="muted">Brak danych.</td></tr>`;

/* Jasny, samodzielny arkusz stylów druku - nie korzysta ze style.css. */
const PRINT_CSS = `
    * { box-sizing: border-box; }
    body { font: 12px/1.4 -apple-system, Arial, sans-serif; color: #000;
        margin: 0; padding: 0; }
    h1 { font-size: 20px; margin: 0; }
    h2 { font-size: 14px; margin: 16px 0 6px; border-bottom: 1px solid #000;
        padding-bottom: 2px; }
    .sheet-head { display: flex; justify-content: space-between;
        align-items: flex-start; border-bottom: 2px solid #000;
        padding-bottom: 8px; }
    .sheet-meta { text-align: right; }
    .sheet-meta .pid { font-weight: 700; font-family: monospace; }
    .muted { color: #555; }
    .totals { margin: 8px 0 4px; color: #333; }
    .section { page-break-inside: avoid; margin-top: 10px; }
    .elevation { text-align: center; margin: 6px 0; }
    svg { max-width: 100%; height: auto; }
    table { width: 100%; border-collapse: collapse; margin: 4px 0; }
    th, td { border: 1px solid #999; padding: 3px 6px; text-align: left; }
    th { background: #eee; font-weight: 600; }
    .num { text-align: right; font-variant-numeric: tabular-nums; }
    tr { page-break-inside: avoid; }
    tr.total td { border-top: 2px solid #000; }
    thead { display: table-header-group; }
    /* kolory linii elewacji niesie samo SVG (ELEVATION_STYLE) */
    @page { size: A4; margin: 14mm; }
`;

/* ----------------------------------------------------------- settings --- */

const numberField = (id, label, value) => `
    <div><label for="${id}">${escapeHtml(label)}</label>
        <input id="${id}" type="number" step="any" value="${value}"></div>`;

const textField = (id, label, value) => `
    <div><label for="${id}">${escapeHtml(label)}</label>
        <input id="${id}" value="${escapeHtml(value)}"></div>`;

const num = id => Number($("#" + id).value);

/* Ustawienia globalne (konstrukcja, materiały, ceny domyślne, typy szafek).
   Zmiana nie dotyka istniejących projektów - ich ceny to migawka. */
async function settingsModal() {

    const s = await api("GET", "/api/settings");
    const c = s.construction;
    const m = s.materials;
    const h = s.hardware;

    openModal(`
        <h2>Ustawienia</h2>

        <h3>Konstrukcja (mm)</h3>
        <div class="grid">
            ${numberField("c-board", "Grubość płyty", c.board_thickness)}
            ${numberField("c-back", "Grubość pleców", c.back_thickness)}
            ${numberField("c-setback", "Cofnięcie półki", c.shelf_setback)}
            ${numberField("c-gap", "Szczelina frontu", c.front_gap)}
            ${numberField("c-edge", "Grubość obrzeża", c.edge_thickness)}
        </div>

        <h3 style="margin-top:16px">Materiały i ceny</h3>
        <div class="grid">
            ${textField("m-board-name", "Płyta - nazwa", m.board.name)}
            ${numberField("m-board-price", "Płyta - cena/m²", m.board.price)}
            ${textField("m-back-name", "Plecy - nazwa", m.back.name)}
            ${numberField("m-back-price", "Plecy - cena/m²", m.back.price)}
            ${textField("m-front-name", "Front - nazwa", m.front.name)}
            ${numberField("m-front-price", "Front - cena/m²", m.front.price)}
        </div>

        <h3 style="margin-top:16px">Obrzeże, okucia, waluta</h3>
        <div class="grid">
            ${numberField("edging", "Obrzeże - cena/m", s.edging_price)}
            ${numberField("hw-hinges", "Zawiasy / front", h.hinges_per_front)}
            ${numberField("hw-hinge", "Zawias - cena/szt.", h.hinge_price)}
            ${numberField("hw-handle", "Uchwyt - cena/szt.", h.handle_price)}
            ${textField("currency", "Waluta", s.currency)}
        </div>

        <h3 style="margin-top:16px">Typy szafek</h3>
        <p class="muted mono" style="font-size:11px">nazwa · szer · wys · głęb · półki · fronty</p>
        <div id="types-list"></div>
        <button class="small" id="add-type" type="button">+ Typ</button>

        <div class="error" id="modal-error"></div>
        <div class="modal-actions">
            <button onclick="closeModal()">Anuluj</button>
            <button class="primary" id="modal-save">Zapisz</button>
        </div>
    `);

    const types = Object.entries(s.cabinet_types)
        .map(([name, dims]) => ({ name, ...dims }));
    $("#types-list").innerHTML = types.map(typeRow).join("");

    // jeden delegowany listener zamiast przepinania po każdym dodaniu wiersza
    $("#types-list").addEventListener("click", event => {
        const del = event.target.closest(".t-del");
        if (del) del.closest(".type-row").remove();
    });

    $("#add-type").addEventListener("click", () => {
        $("#types-list").insertAdjacentHTML("beforeend", typeRow());
    });

    $("#modal-save").addEventListener("click", saveSettings);
}

function typeRow(type = {}) {
    const v = { width: 600, height: 720, depth: 560, shelves: 1, fronts: 2, ...type };
    const cell = (cls, val, num = true) =>
        `<input class="${cls}" ${num ? 'type="number"' : ""} value="${escapeHtml(String(val))}">`;
    return `<div class="type-row">
        ${cell("t-name", v.name || "", false)}
        ${cell("t-width", v.width)}${cell("t-height", v.height)}
        ${cell("t-depth", v.depth)}${cell("t-shelves", v.shelves)}
        ${cell("t-fronts", v.fronts)}
        <button class="small danger t-del" type="button">×</button>
    </div>`;
}

async function saveSettings() {

    const cabinet_types = {};
    document.querySelectorAll(".type-row").forEach(row => {
        const pick = cls => Number(row.querySelector(cls).value);
        const name = row.querySelector(".t-name").value.trim();
        if (!name) return;
        cabinet_types[name] = {
            width: pick(".t-width"), height: pick(".t-height"),
            depth: pick(".t-depth"), shelves: pick(".t-shelves"),
            fronts: pick(".t-fronts"),
        };
    });

    const settings = {
        construction: {
            board_thickness: num("c-board"), back_thickness: num("c-back"),
            shelf_setback: num("c-setback"), front_gap: num("c-gap"),
            edge_thickness: num("c-edge"),
        },
        materials: {
            board: { name: $("#m-board-name").value, price: num("m-board-price") },
            back: { name: $("#m-back-name").value, price: num("m-back-price") },
            front: { name: $("#m-front-name").value, price: num("m-front-price") },
        },
        edging_price: num("edging"),
        hardware: {
            hinges_per_front: num("hw-hinges"),
            hinge_price: num("hw-hinge"), handle_price: num("hw-handle"),
        },
        currency: $("#currency").value,
        cabinet_types,
    };

    try {
        await api("PUT", "/api/settings", settings);
        state.config = await api("GET", "/api/config");  // typy szafek dla kreatora
        closeModal();
        if (state.project) render();
        toast("Ustawienia zapisane");
    } catch (error) {
        $("#modal-error").textContent = error.message;
    }
}

/* Ceny konkretnego projektu (migawka). Edycja nie dotyka innych projektów. */
function pricesModal(pricing) {

    // nazwy materiałów odczytujemy po indeksie - bez przenoszenia ich przez DOM
    const names = Object.keys(pricing.material_prices);

    const materialRows = names.map((name, index) => numberField(
        `mp-${index}`, `${name} - cena/m²`, pricing.material_prices[name])
    ).join("");

    openModal(`
        <h2>Ceny projektu</h2>
        <p class="muted">Zmiana dotyczy tylko tego projektu.</p>

        <h3>Materiały</h3>
        <div class="grid">${materialRows}</div>

        <h3 style="margin-top:16px">Obrzeże, okucia, waluta</h3>
        <div class="grid">
            ${numberField("p-edging", "Obrzeże - cena/m", pricing.edging_price)}
            ${numberField("p-hinges", "Zawiasy / front", pricing.hinges_per_front)}
            ${numberField("p-hinge", "Zawias - cena/szt.", pricing.hardware_prices.hinge)}
            ${numberField("p-handle", "Uchwyt - cena/szt.", pricing.hardware_prices.handle)}
            ${textField("p-currency", "Waluta", pricing.currency)}
        </div>

        <div class="error" id="modal-error"></div>
        <div class="modal-actions">
            <button onclick="closeModal()">Anuluj</button>
            <button class="primary" id="modal-save">Zapisz</button>
        </div>
    `);

    $("#modal-save").addEventListener("click", async () => {

        const material_prices = {};
        names.forEach((name, index) => {
            material_prices[name] = num(`mp-${index}`);
        });

        const payload = {
            currency: $("#p-currency").value,
            material_prices,
            edging_price: num("p-edging"),
            hinges_per_front: num("p-hinges"),
            hardware_prices: { hinge: num("p-hinge"), handle: num("p-handle") },
        };

        try {
            await api("PUT", `${projectUrl()}/prices`, payload);
            closeModal();
            renderCuttingList();
            toast("Ceny zapisane");
        } catch (error) {
            $("#modal-error").textContent = error.message;
        }
    });
}

$("#settings-btn").addEventListener("click", settingsModal);

/* ---------------------------------------------------------------- init --- */

window.closeModal = closeModal;

(async function init() {
    try {
        state.config = await api("GET", "/api/config");
        await loadProjects();
    } catch (error) {
        toast(error.message, true);
    }
})();
