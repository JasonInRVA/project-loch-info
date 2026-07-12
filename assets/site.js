async function loadManifest() {
  const response = await fetch("docs/manifest.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Unable to load manifest: ${response.status}`);
  }
  return response.json();
}

function formatSize(bytes) {
  if (bytes >= 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }
  if (bytes >= 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${bytes} bytes`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function setText(id, value) {
  const node = document.getElementById(id);
  if (node) {
    node.textContent = value;
  }
}

function renderRecord(record) {
  const duplicateNote = record.is_duplicate
    ? `<span class="dup-pill">Same SHA-256 as ${record.duplicate_count - 1} other archived copy${record.duplicate_count === 2 ? "" : "ies"}</span>`
    : "";
  const sensitiveNote = record.sensitive_source_handling
    ? `<p class="meta-note"><strong>Access handling:</strong> ${escapeHtml(record.sensitive_source_handling)}</p>`
    : "";
  const officialNote = record.official_source_note
    ? `<p class="meta-note"><strong>Official source note:</strong> ${escapeHtml(record.official_source_note)}</p>`
    : "";

  return `
    <article class="record-card">
      <span class="record-kicker">${escapeHtml(record.date)} · ${escapeHtml(record.agency)}</span>
      <h3>${escapeHtml(record.title)}</h3>
      <div class="record-flags">
        <span class="status-pill status-${escapeHtml(record.status)}">${escapeHtml(record.status)}</span>
        <span class="type-pill">${escapeHtml(record.record_type)}</span>
        ${duplicateNote}
      </div>
      <p class="record-summary">${escapeHtml(record.description)}</p>
      <div class="record-meta">
        <div>
          <span class="field-label">Originator</span>
          <span>${escapeHtml(record.originator)}</span>
        </div>
        <div>
          <span class="field-label">Pages</span>
          <span>${record.page_count}</span>
        </div>
        <div>
          <span class="field-label">File size</span>
          <span>${formatSize(record.file_size_bytes)}</span>
        </div>
        <div>
          <span class="field-label">SHA-256</span>
          <code>${escapeHtml(record.sha256)}</code>
        </div>
      </div>
      <div class="record-links">
        <span class="source-pair">
          <a href="${escapeHtml(record.archived_path)}">Archived copy</a>
          <span>(</span>
          <a href="${escapeHtml(record.official_source_url)}">Official source</a>
          <span>)</span>
        </span>
      </div>
      ${officialNote}
      ${sensitiveNote}
    </article>
  `;
}

function populateSelect(select, values, allLabel) {
  if (!select) {
    return;
  }
  select.innerHTML = "";
  const allOption = document.createElement("option");
  allOption.value = "all";
  allOption.textContent = allLabel;
  select.appendChild(allOption);
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });
}

function wireLibrary(containerId, records, { defaultAgency = "all", defaultYear = "all" } = {}) {
  const container = document.getElementById(containerId);
  if (!container) {
    return;
  }

  const root = container.closest(".library-shell") || document;
  const agencySelect = root.querySelector("[data-filter='agency']");
  const yearSelect = root.querySelector("[data-filter='year']");
  const resultCount = root.querySelector("[data-role='result-count']");
  const recordHost = root.querySelector("[data-role='record-host']");

  const agencies = [...new Set(records.map((record) => record.agency))].sort();
  const years = [...new Set(records.map((record) => record.year))].sort().reverse();

  populateSelect(agencySelect, agencies, "All agencies");
  populateSelect(yearSelect, years, "All years");

  if (agencySelect) {
    agencySelect.value = defaultAgency;
  }
  if (yearSelect) {
    yearSelect.value = defaultYear;
  }

  const render = () => {
    const filtered = records.filter((record) => {
      const agencyOk = !agencySelect || agencySelect.value === "all" || record.agency === agencySelect.value;
      const yearOk = !yearSelect || yearSelect.value === "all" || record.year === yearSelect.value;
      return agencyOk && yearOk;
    });

    if (resultCount) {
      resultCount.textContent = `${filtered.length} document${filtered.length === 1 ? "" : "s"}`;
    }

    if (!recordHost) {
      return;
    }

    if (!filtered.length) {
      recordHost.innerHTML = '<div class="empty-state">No documents match the selected agency and year.</div>';
      return;
    }

    recordHost.innerHTML = filtered.map(renderRecord).join("");
  };

  agencySelect?.addEventListener("change", render);
  yearSelect?.addEventListener("change", render);
  render();
}

function populateSummary(records) {
  const currentCount = records.filter((record) => record.status === "current").length;
  const duplicateCount = records.filter((record) => record.is_duplicate).length;
  const uniqueHashes = new Set(records.map((record) => record.sha256)).size;

  setText("total-documents", String(records.length));
  setText("current-documents", String(currentCount));
  setText("unique-hashes", String(uniqueHashes));
  setText("duplicate-documents", String(duplicateCount));
}

async function boot() {
  try {
    const manifest = await loadManifest();
    populateSummary(manifest);
    wireLibrary("index-library", manifest);
    wireLibrary("full-library", manifest);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    document.querySelectorAll("[data-role='record-host']").forEach((node) => {
      node.innerHTML = `<div class="empty-state">${escapeHtml(message)}</div>`;
    });
  }
}

boot();
