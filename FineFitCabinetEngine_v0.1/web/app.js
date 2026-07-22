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

/* --------------------------------------------------------------- views --- */

function render() {

    if (!state.project) return;

    const project = state.project;

    const cabinets = project.sections.reduce(
        (total, section) => total + section.cabinets.length, 0
    );

    $("#workspace").innerHTML = `
        <div class="panel">
            <div class="panel-head">
                <div>
                    <h2>${escapeHtml(project.project_name)}</h2>
                    <p class="muted mono">${project.project_id} ·
                        utworzono ${escapeHtml(project.created_at)}</p>
                </div>
                <div class="tabs">
                    <button class="tab ${state.tab === "sections" ? "active" : ""}"
                        data-tab="sections">Sekcje i szafki</button>
                    <button class="tab ${state.tab === "cutting" ? "active" : ""}"
                        data-tab="cutting">Lista rozkroju</button>
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

    const pieces = cabinet.parts.reduce(
        (total, part) => total + part.quantity, 0);
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
        xmlns="http://www.w3.org/2000/svg">${svg}</svg>`;
}

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

async function renderCuttingList() {

    $("#tab-content").innerHTML = `<div class="panel"><div class="panel-body">
        <p class="muted">Wczytywanie...</p></div></div>`;

    const data = await api("GET", `${projectUrl()}/cutting-list`);

    const rows = data.rows.map(row => `
        <tr>
            <td>${escapeHtml(row.part_name)}</td>
            <td class="num">${row.length}</td>
            <td class="num">${row.width}</td>
            <td class="num">${row.thickness}</td>
            <td class="num">${row.quantity}</td>
            <td class="num">${row.area.toFixed(3)}</td>
            <td>${escapeHtml(row.material)}</td>
        </tr>
    `).join("");

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
    `;

    $("#export-csv").addEventListener("click", () => exportCsv(data.rows));
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
