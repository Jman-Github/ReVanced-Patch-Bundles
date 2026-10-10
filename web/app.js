/* SPDX-License-Identifier: GPL-3.0-only
 * Adapted from brosssh/revanced-external-bundles, copyright its contributors.
 * Source: https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/resources/static/app.js
 * Changes: static snapshot loading, indexed search, lazy metadata, freshness labels,
 * catalog API import URLs, and GitHub source management. See COPYING.
 */
import { Catalog, catalogOrigins, bundleImportPath, compareReleaseDates, packageFilterMatches, releaseTimestamp } from "./shared/catalog.js";
import { gitHosts } from "./shared/hosts.js";
import {
    Virtualizer,
    measureElement,
    observeWindowOffset,
    observeWindowRect,
    windowScroll
} from "https://esm.sh/@tanstack/virtual-core@3.17.8?bundle";

/* global DOMPurify, marked */

const input = document.getElementById("search");
const packageFilter = document.getElementById("package-filter");
const sourceFilter = document.getElementById("source-filter");
const bundleVersionFilter = document.getElementById("bundle-version-filter");
const bundleTypeFilter = document.getElementById("bundle-type-filter");
const results = document.getElementById("results");
const status = document.getElementById("status");
const toggleAllChangelogs = document.getElementById("toggle-all-changelogs");
const viewToggle = document.getElementById("view-toggle");
const container = document.querySelector(".container");
const filterButtons = document.querySelectorAll(".filter-btn");
const adminAccess = document.getElementById("admin-access");

// Keep the denser list layout as the mobile default; desktop starts in grid view.
if (matchMedia("(max-width: 700px)").matches) {
    results.classList.remove("grid-view");
    container.classList.remove("grid-view-enabled");
    viewToggle.setAttribute("aria-pressed", "false");
    viewToggle.textContent = "Grid view";
}

// Virtualized list: TanStack Virtual renders only the visible rows of cards. Row
// heights are measured from the DOM and a single spacer keeps the document scroll
// height correct, so card positions are stable and no scroll compensation is needed.
const ROW_GAP = 16;
const MIN_COLUMN_WIDTH = 380;

// Parsed markdown/patches reuse: rows are recreated as the viewport moves, so
// re-parsing the same bundle's changelog every time dominates re-render cost.
const renderCache = new Map();
const patchListCache = new WeakMap();
const cardViewStates = new Map();
const RENDER_CACHE_LIMIT = 500;
marked.setOptions({ breaks: true, gfm: true });

function cachedMarkdown(bundleId, key, markdown) {
    const cacheKey = `${bundleId}:${key}`;
    let html = renderCache.get(cacheKey);
    if (html === undefined) {
        html = renderMarkdown(markdown);
        if (renderCache.size >= RENDER_CACHE_LIMIT) renderCache.clear();
        renderCache.set(cacheKey, html);
    }
    return html;
}

function cachedPatchList(patches) {
    let html = patchListCache.get(patches);
    if (html === undefined) {
        html = patches.map(renderPatch).join('');
        patchListCache.set(patches, html);
    }
    return html;
}

function restoreScrollTop(element, scrollTop) {
    element.scrollTop = scrollTop;
    queueMicrotask(() => {
        if (element.isConnected && !element.hidden) element.scrollTop = scrollTop;
    });
}

const track = document.getElementById("v-track");
let filteredBundles = [];
let virtualizer = null;
let rowData = [];
let lastColumns = 1;
let lastVisibleFp = "";

function layoutColumns() {
    if (!results.classList.contains("grid-view")) return 1;
    const width = results.clientWidth;
    return Math.max(1, Math.floor((width + ROW_GAP) / (MIN_COLUMN_WIDTH + ROW_GAP)));
}

function buildRows() {
    const columns = layoutColumns();
    const rows = [];
    for (let i = 0; i < filteredBundles.length; i += columns) {
        rows.push(filteredBundles.slice(i, i + columns));
    }
    return rows;
}

function estimateRowHeight() {
    // Guess only: measured row heights replace this as rows render.
    return results.classList.contains("grid-view") ? 420 : 300;
}

function renderVisible() {
    if (!virtualizer || rowData.length === 0) return;

    const items = virtualizer.getVirtualItems();
    const fp = items.map(v => `${v.index}:${Math.round(v.start)}`).join(",");
    if (fp === lastVisibleFp) {
        track.style.height = `${virtualizer.getTotalSize()}px`;
        return;
    }
    lastVisibleFp = fp;

    track.style.height = `${virtualizer.getTotalSize()}px`;
    const fragment = document.createDocumentFragment();
    const columns = layoutColumns();
    for (const item of items) {
        const rowEl = document.createElement("div");
        rowEl.className = "virtual-row";
        rowEl.dataset.index = String(item.index);
        rowEl.style.transform = `translateY(${item.start - virtualizer.options.scrollMargin}px)`;
        rowEl.style.gridTemplateColumns = `repeat(${columns}, minmax(0, 1fr))`;
        for (const card of rowData[item.index]) {
            renderBundle(card, rowEl);
        }
        fragment.appendChild(rowEl);
    }
    track.replaceChildren(fragment);
    virtualizer.measureElement(null);
    for (const rowEl of track.children) virtualizer.measureElement(rowEl);
    updateAllChangelogsButton();
}

function clearVirtualizer() {
    if (virtualizer) virtualizer.cleanup();
    virtualizer = null;
    rowData = [];
    lastVisibleFp = "";
    track.replaceChildren();
    track.style.height = "0px";
}


function currentAnchorBundleIndex() {
    if (!virtualizer) return null;
    const trackTop = track.getBoundingClientRect().top + window.scrollY;
    if (window.scrollY < trackTop) return null;
    const visibleRow = virtualizer.getVirtualItems()
        .find(item => item.end >= window.scrollY);
    return (visibleRow?.index ?? 0) * lastColumns;
}

function setupVirtualizer(anchorBundleIndex = null) {
    rowData = buildRows();
    lastColumns = layoutColumns();
    if (virtualizer) virtualizer.cleanup();
    virtualizer = new Virtualizer({
        count: rowData.length,
        getScrollElement: () => window,
        estimateSize: () => estimateRowHeight(),
        initialOffset: () => window.scrollY,
        scrollMargin: track.getBoundingClientRect().top + window.scrollY,
        overscan: 2,
        gap: ROW_GAP,
        observeElementRect: observeWindowRect,
        observeElementOffset: observeWindowOffset,
        scrollToFn: windowScroll,
        measureElement,
        onChange: () => renderVisible()
    });
    // The vanilla core does not attach its scroll/resize observers until
    // _willUpdate is invoked; without it no viewport rows ever render.
    virtualizer._willUpdate();
    lastVisibleFp = "";
    renderVisible();
    if (anchorBundleIndex !== null && rowData.length > 0) {
        virtualizer.scrollToIndex(
            Math.min(Math.floor(anchorBundleIndex / lastColumns), rowData.length - 1),
            { align: "start" }
        );
    }
}

let currentFilter = "release";
let currentSearchQuery = "";
let currentPackageFilter = "";
let currentSourceUrl = "";
let currentBundleVersion = "";
let currentBundleType = "";
let latestBundles = [];
let allBundles = [];
let sourceVersions = [];
let allChangelogsExpanded = true;
let catalog, siteConfig, summaries = [], searchSequence = 0;
let refreshingCatalog = false;
const renderAfterInput = debounce(() => { void renderFilteredBundles(); }, 150);
adminAccess.textContent = "Manage sources";
adminAccess.addEventListener("click", () => {
    window.open("https://github.com/" + (siteConfig?.repository || "Jman-Github/Patch-Bundle-Registry") +
        "/blob/" + (siteConfig?.data_branch || "bundles") + "/config/sources.json",
        "_blank", "noopener,noreferrer");
});
void loadBundles();

input.addEventListener("input", () => {
    currentSearchQuery = input.value.trim().toLowerCase();
    renderAfterInput();
});

packageFilter.addEventListener("input", () => {
    currentPackageFilter = packageFilter.value.trim().toLowerCase();
    renderAfterInput();
});

sourceFilter.addEventListener("change", () => selectSource(sourceFilter.value));

bundleVersionFilter.addEventListener("change", () => selectBundleVersion(bundleVersionFilter.value));

bundleTypeFilter.addEventListener("change", () => {
    currentBundleType = bundleTypeFilter.value;
    resetBundleSelection();
    populateVersionOptions();
    renderFilteredBundles();
});

filterButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        filterButtons.forEach(button => button.classList.remove("active"));
        btn.classList.add("active");
        currentFilter = btn.dataset.filter;
        resetBundleSelection();
        populateVersionOptions();
        renderFilteredBundles();
    });
});

const toggleAllChangelogsAction = () => {
    const cards = [...results.querySelectorAll(".bundle-item")];
    allChangelogsExpanded = !allChangelogsExpanded;
    for (const state of cardViewStates.values()) state.section = undefined;
    cards.forEach(card => card.setActiveSection?.(
        allChangelogsExpanded ? "changelog" : null,
        false,
        false
    ));
    updateAllChangelogsButton();
};

toggleAllChangelogs.addEventListener("click", toggleAllChangelogsAction);

viewToggle.addEventListener("click", () => {
    const anchorBundleIndex = currentAnchorBundleIndex();
    const gridEnabled = results.classList.toggle("grid-view");
    container.classList.toggle("grid-view-enabled", gridEnabled);
    viewToggle.setAttribute("aria-pressed", String(gridEnabled));
    viewToggle.textContent = gridEnabled ? "List view" : "Grid view";
    // Rebuild the row grouping while keeping the first visible bundle anchored.
    setupVirtualizer(anchorBundleIndex);
    updateStatus();
});

addEventListener("resize", () => {
    const columns = layoutColumns();
    if (columns !== lastColumns) setupVirtualizer(currentAnchorBundleIndex());
});

async function openCatalog() {
    let failure;
    for (const origin of catalogOrigins(siteConfig,new URL("./database/",location.href).href)) {
        try { return await new Catalog(origin,fetch,false).initialize(); }
        catch(error) { failure = error; }
    }
    throw failure;
}

async function loadBundles(refreshedCatalog = null) {
    status.textContent = "Loading bundles...";
    status.classList.add("loading");
    try {
        siteConfig = await (await fetch("./config.json")).json();
        const nextCatalog = refreshedCatalog ||
            await openCatalog();
        const nextSummaries = await nextCatalog.bundles();
        catalog = nextCatalog;
        scheduleCatalogRefresh();
        summaries = nextSummaries;
        renderCache.clear();
        latestBundles = summaries.filter(bundle => bundle.is_latest).map(transformBundle)
            .sort((a, b) => (b.repoStars ?? -1) - (a.repoStars ?? -1) ||
                a.sourceUrl.localeCompare(b.sourceUrl));
        sourceVersions = summaries.filter(bundle => bundle.source.url === currentSourceUrl)
            .sort(compareReleaseDates);
        if (!sourceVersions.some(bundle => bundle.version === currentBundleVersion)) currentBundleVersion = "";
        allBundles = currentBundleVersion
            ? sourceVersions.filter(bundle => bundle.version === currentBundleVersion).map(transformBundle)
            : latestBundles;
        populateSourceOptions();
        reconcileSourceSelection();
        setVersionControlsEnabled(Boolean(currentSourceUrl));
        populateVersionOptions();
        populateBundleTypeOptions();
        await renderFilteredBundles({ resetScroll: !refreshedCatalog });
        return true;
    } catch (error) {
        console.error(error);
        status.textContent = "Failed to load bundles: " + error.message;
        return false;
    } finally { status.classList.remove("loading"); }
}

let catalogRefreshTimer;
function scheduleCatalogRefresh() {
    clearTimeout(catalogRefreshTimer);
    catalogRefreshTimer = setTimeout(async () => {
        if (document.hidden || refreshingCatalog) { scheduleCatalogRefresh(); return; }
        refreshingCatalog = true;
        try {
            const next = await openCatalog();
            if (next.manifest.generation !== catalog.manifest.generation) await loadBundles(next);
        } catch { /* Preserve the current view during a transient origin failure. */ }
        finally { refreshingCatalog = false; scheduleCatalogRefresh(); }
    },15000);
}

async function recoverGeneration(error) {
    if (!error.generationUnavailable || refreshingCatalog) return false;
    refreshingCatalog = true;
    try {
        const nextCatalog = await openCatalog();
        if (nextCatalog.manifest.generation === catalog.manifest.generation) return false;
        return await loadBundles(nextCatalog);
    } catch { return false; }
    finally { refreshingCatalog = false; }
}

async function selectSource(sourceUrl) {
    currentSourceUrl = sourceUrl;
    sourceVersions = summaries.filter(bundle => bundle.source.url === sourceUrl)
        .sort(compareReleaseDates);
    resetBundleSelection();
    setVersionControlsEnabled(Boolean(sourceUrl));
    populateVersionOptions();
    populateBundleTypeOptions();
    await renderFilteredBundles();
}

async function selectBundleVersion(version) {
    currentBundleVersion = version;
    allBundles = version ? sourceVersions.filter(bundle => bundle.version === version).map(transformBundle) : latestBundles;
    await renderFilteredBundles();
}

function transformPatch(patch) {
    return { name: patch.name, description: patch.description,
        compatiblePackages: patch.packages.map(pkg => ({ name: pkg.name, versions: pkg.versions })) };
}

async function bundlePatches(bundle) {
    if (!bundle.loadedPatches) {
        const result = await catalog.patchRows({ bundle_id: bundle.id, all: true, include_unverified: true });
        bundle.loadedPatches = result.rows.map(transformPatch);
    }
    return bundle.loadedPatches;
}

function sourceOptionLabel(bundle) {
    const parts = sourceName(bundle.sourceUrl, bundle.ownerName, bundle.repoName).split('/');
    if (parts.length >= 2) {
        return `${parts.slice(0, -1).join('/')} / ${parts[parts.length - 1]}`;
    }
    return parts[0];
}

function populateSourceOptions() {
    const sources = new Map();
    for (const summary of summaries) {
        const bundle = transformBundle(summary);
        if (!sources.has(bundle.sourceUrl)) {
            let host = '';
            try { host = new URL(bundle.sourceUrl).hostname; } catch { /* keep empty */ }
            sources.set(bundle.sourceUrl, { base: sourceOptionLabel(bundle), host });
        }
    }

    // A namespace/repo shared across hosts is ambiguous, so tag every option with that
    // base with its host.
    const baseHosts = new Map();
    for (const { base, host } of sources.values()) {
        const hosts = baseHosts.get(base) || new Set();
        if (host) hosts.add(host);
        baseHosts.set(base, hosts);
    }

    const options = [new Option("All sources", "")];
    [...sources.entries()]
        .sort((left, right) => left[1].base.localeCompare(right[1].base))
        .forEach(([url, { base, host }]) => {
            const label = baseHosts.get(base).size > 1 ? `${base} (${host})` : base;
            options.push(new Option(label, url));
        });
    sourceFilter.replaceChildren(...options);
}

function reconcileSourceSelection() {
    if (currentSourceUrl && !summaries.some(bundle => bundle.source.url === currentSourceUrl)) {
        currentSourceUrl = "";
        sourceVersions = [];
        resetBundleSelection();
        setVersionControlsEnabled(false);
        populateVersionOptions();
    }
    sourceFilter.value = currentSourceUrl;
}

function populateBundleTypeOptions() {
    const selectedType = currentBundleType;
    const types = new Set(latestBundles.map(bundle => bundle.bundleType).filter(Boolean));
    sourceVersions.forEach(bundle => {
        if (bundle.bundle_type) types.add(bundle.bundle_type);
    });

    const options = [new Option("All types", "")];
    [...types].sort().forEach(type => options.push(new Option(type, type)));
    bundleTypeFilter.replaceChildren(...options);
    bundleTypeFilter.value = selectedType;
}

function populateVersionOptions() {
    const options = [new Option("All versions", "")];
    const versions = new Map();
    sourceVersions
        .filter(bundle => currentFilter === "all" || bundle.is_prerelease === (currentFilter === "prerelease"))
        .filter(bundle => !currentBundleType || bundle.bundle_type === currentBundleType)
        .forEach(bundle => {
            if (!versions.has(bundle.version)) versions.set(bundle.version, bundle.is_prerelease);
        });
    versions.forEach((isPrerelease, version) => {
        options.push(new Option(`${version} · ${isPrerelease ? "Prerelease" : "Release"}`, version));
    });

    bundleVersionFilter.replaceChildren(...options);
    bundleVersionFilter.value = currentBundleVersion;
}

function setVersionControlsEnabled(enabled) {
    bundleVersionFilter.disabled = !enabled;
}

function resetBundleSelection() {
    currentBundleVersion = "";
    bundleVersionFilter.value = "";
    allBundles = latestBundles;
}

function installAvatarFallback(card, label) {
    const image = card.querySelector(".owner-avatar");
    if (!image) return;
    const initial = escapeHtml(label.trim()[0] || "?").toUpperCase();
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="#eee" width="100" height="100"/><text x="50" y="50" font-size="40" text-anchor="middle" dy=".3em" fill="#999">${initial}</text></svg>`;
    if (!image.getAttribute("src")) image.src = `data:image/svg+xml,${encodeURIComponent(svg)}`;
    image.addEventListener("error", () => {
        image.src = `data:image/svg+xml,${encodeURIComponent(svg)}`;
    }, { once: true });
}

function transformBundle(bundle) {
    const metadata = bundle.source?.source_metadatum || {};
    return {
        id: bundle.id, bundleType: bundle.bundle_type, createdAt: bundle.created_at,
        description: bundle.description, downloadUrl: bundle.download_url,
        signatureDownloadUrl: bundle.signature_download_url === "N/A" ? null : bundle.signature_download_url,
        isPrerelease: bundle.is_prerelease, version: bundle.version,
        sourceUrl: bundle.source?.url || "",
        ownerName: metadata.owner_name || "", ownerAvatarUrl: metadata.owner_avatar_url || "",
        repoName: metadata.repo_name || "", repoDescription: metadata.repo_description || "",
        repoStars: metadata.repo_stars,
        isRepoArchived: metadata.is_repo_archived, patches: [],
        patchCount: bundle.patch_count,
        hasPatches: bundle.patch_list_available, metadataStatus: bundle.metadata_status,
        metadataVersion: bundle.patch_metadata_version
    };
}

async function renderFilteredBundles({ resetScroll = true } = {}) {
    const sequence = ++searchSequence;
    const search = currentSearchQuery, packageQuery = currentPackageFilter;
    let patchMatches = new Map();
    if (search || packageQuery) {
        status.textContent = "Searching bundles and patches...";
        try {
            const candidates = allBundles.filter(bundle =>
                (!currentSourceUrl || bundle.sourceUrl === currentSourceUrl) &&
                (!currentBundleType || bundle.bundleType === currentBundleType));
            let cursor = 0;
            do {
                const page = await catalog.patchRows({ q: packageQuery ? "" : search, bundle_ids: candidates.map(b => b.id),
                    page_cursor: cursor, include_unverified: true });
                if (sequence !== searchSequence) return;
                for (const patch of page.rows) {
                    if (packageQuery && !packageFilterMatches(patch.packages, packageQuery))
                        continue;
                    if (!patchMatches.has(patch.bundle_id)) patchMatches.set(patch.bundle_id, []);
                    patchMatches.get(patch.bundle_id).push(transformPatch(patch));
                }
                cursor = page.next_cursor;
            } while (cursor !== null);
        } catch (error) {
            if (sequence === searchSequence && await recoverGeneration(error)) return;
            if (sequence === searchSequence) status.textContent = "Search failed: " + error.message;
            return;
        }
    }
    if (sequence !== searchSequence) return;
    const previousBundles = filteredBundles;
    filteredBundles = allBundles.filter(bundle => {
        if (currentFilter === "release" && bundle.isPrerelease) return false;
        if (currentFilter === "prerelease" && !bundle.isPrerelease) return false;
        if (currentSourceUrl && bundle.sourceUrl !== currentSourceUrl) return false;
        if (currentBundleVersion && bundle.version !== currentBundleVersion) return false;
        if (currentBundleType && bundle.bundleType !== currentBundleType) return false;
        const text = [bundle.sourceUrl, bundle.ownerName, bundle.repoName, bundle.repoDescription,
            bundle.version, bundle.description].filter(Boolean).join(" ").toLowerCase();
        const patchTextMatches = (patchMatches.get(bundle.id) || []).some(patch =>
            ((patch.name || "") + " " + (patch.description || "")).toLowerCase().includes(search));
        return (!search || text.includes(search) || patchTextMatches) &&
            (!packageQuery || patchMatches.has(bundle.id));
    }).map(bundle => patchMatches.has(bundle.id) ?
        { ...bundle, patches: patchMatches.get(bundle.id), filteredPatches: true } : bundle);
    if (!filteredBundles.length) {
        clearVirtualizer(); updateAllChangelogsButton();
        status.textContent = "No bundles found for the selected filters";
        return;
    }
    if (resetScroll) document.scrollingElement.scrollTop = 0;
    if (!resetScroll && virtualizer && lastColumns === layoutColumns() &&
        previousBundles.length === filteredBundles.length &&
        previousBundles.every((bundle, index) => bundle.id === filteredBundles[index].id)) {
        // Progress-only snapshots keep the same rows. Retain their measurements
        // so refreshing card contents does not move the reader to another row.
        rowData = buildRows();
        lastVisibleFp = "";
        renderVisible();
    } else setupVirtualizer();
    updateStatus();
}

function updateStatus() {
    const count = filteredBundles.length;
    if (count > 0) {
        status.textContent = `Showing ${count} bundle${count === 1 ? "" : "s"}`;
    }
}

function renderBundle(bundle, target) {
    const card = document.createElement("article");
    card.className = "bundle-item";

    const metadataWarning = bundle.metadataStatus !== "verified"
        ? `<div class="v3-warning">Patch metadata: ${escapeHtml(bundle.metadataStatus)}${bundle.metadataVersion ? " · " + escapeHtml(bundle.metadataVersion) : ""}. Compatibility is unverified for this artifact.</div>` : "";
    const v3WarningHtml = bundle.bundleType === "ReVanced:V3"
        ? `<div class="v3-warning">
                ⚠️ It will not be usable in URV and the patches list can be empty.
           </div>`
        : '';
    const tagUrl = releaseTagUrl(bundle);
    const versionHtml = tagUrl
        ? `<a class="version-text" href="${escapeHtml(tagUrl)}" target="_blank" rel="noopener">${escapeHtml(bundle.version)}</a>`
        : `<span class="version-text">${escapeHtml(bundle.version)}</span>`;

    // Show the tracked namespace/repo from the source URL; after an upstream rename the
    // metadata names diverge from what is actually tracked, so both are shown.
    const trackedParts = sourceName(bundle.sourceUrl, bundle.ownerName, bundle.repoName).split('/');
    const trackedNamespace = trackedParts.length >= 2 ? trackedParts.slice(0, -1).join('/') : bundle.ownerName;
    const trackedRepo = trackedParts.length >= 2 ? trackedParts[trackedParts.length - 1] : bundle.repoName;
    const trackedName = `${trackedNamespace}/${trackedRepo}`;
    const currentName = bundle.ownerName && bundle.repoName ? `${bundle.ownerName}/${bundle.repoName}` : '';
    const repoLinkText = currentName && currentName !== trackedName
        ? `${escapeHtml(trackedName)} <span class="renamed-name">(${escapeHtml(currentName)})</span>`
        : escapeHtml(trackedName);

    card.innerHTML = `
        ${v3WarningHtml}
        ${metadataWarning}

        <div class="bundle-header">
            <a href="${escapeHtml(bundle.sourceUrl)}" target="_blank" rel="noopener" class="owner-avatar-link" aria-label="Open ${escapeHtml(bundle.ownerName || 'source')} repository">
                <img src="${escapeHtml(bundle.ownerAvatarUrl)}"
                     alt="${escapeHtml(bundle.ownerName)}"
                     class="owner-avatar"
                     loading="lazy"
                     decoding="async">
            </a>
            <div class="bundle-header-content">
                <div class="repo-info">
                    <a href="${escapeHtml(bundle.sourceUrl)}" target="_blank" rel="noopener" class="repo-name">
                        ${repoLinkText}
                    </a>
                    <span>•</span>
                    <span class="stars">${(bundle.repoStars == null ? "—" : bundle.repoStars.toLocaleString())}</span>
                </div>
                ${bundle.repoDescription ? `<div class="bundle-description">${cachedMarkdown(bundle.id, 'desc', bundle.repoDescription)}</div>` : ''}
                <div class="bundle-version">
                    ${versionHtml}
                    <span class="bundle-badge ${bundle.isPrerelease ? 'badge-prerelease' : 'badge-release'}">
                        ${bundle.isPrerelease ? 'Prerelease' : 'Release'}
                    </span>
                    <span class="bundle-badge badge-type">${escapeHtml(bundle.bundleType)}</span>
                    ${bundle.isRepoArchived ? `<span class="bundle-badge badge-archived">Archived</span>` : ''}
                    <span class="created-date">${formatDate(bundle.createdAt)}</span>
                </div>
            </div>
        </div>

        <div class="bundle-meta">
            <a href="${escapeHtml(bundle.downloadUrl)}" target="_blank" rel="noopener">
                Download bundle
            </a>
            ${bundle.signatureDownloadUrl ? `
                <span>•</span>
                <a href="${escapeHtml(bundle.signatureDownloadUrl)}" target="_blank" rel="noopener">
                    Download signature
                </a>
            ` : ''}
            <span>•</span>
            <button class="copy-btn" ${bundle.bundleType === "ReVanced:V3" ? 'disabled' : ''} data-url="${bundleImportPath(bundle, Boolean(currentBundleVersion))}">
                ${currentBundleVersion ? "Copy this version URL" : "Copy remote bundle URL"}
            </button>
        </div>

        ${(bundle.description || bundle.hasPatches) ? `
            <div class="card-toggles">
                ${bundle.description ? `
                    <button class="card-toggle" type="button" data-toggle-changelog data-expanded="false">Show changelog</button>
                ` : ''}
                ${bundle.hasPatches ? `
                    <button class="card-toggle" type="button" data-toggle-patches data-expanded="false">Show patches (${bundle.filteredPatches ? bundle.patches.length : (bundle.metadataStatus === "verified" ? bundle.patchCount : "unverified")})</button>
                ` : ''}
            </div>
            <div class="card-content">
                ${bundle.description ? `<div class="changelog-content" data-changelog hidden></div>` : ''}
                ${bundle.hasPatches ? `<div class="patches-content" data-patches-content hidden></div>` : ''}
            </div>
        ` : ''}
    `;

    installAvatarFallback(card, bundle.ownerName || trackedName);
    target.appendChild(card);

    const copyBtn = card.querySelector(".copy-btn");
    const copyButtonLabel = copyBtn.textContent.trim();
    let copyFeedbackTimeout;
    const showCopyFeedback = (text, copied = false) => {
        clearTimeout(copyFeedbackTimeout);
        copyBtn.textContent = text;
        copyBtn.classList.toggle("copied", copied);
        copyFeedbackTimeout = setTimeout(() => {
            copyBtn.textContent = copyButtonLabel;
            copyBtn.classList.remove("copied");
        }, 1500);
    };
    copyBtn.addEventListener("click", async () => {
        // The copied value must be absolute: it is pasted into the patched-app
        // manager, which resolves it from the device, not from this page.
        const url = new URL(copyBtn.dataset.url, siteConfig.api).href;
        try {
            await navigator.clipboard.writeText(url);
            showCopyFeedback("Copied!", true);
        } catch (err) {
            console.error("Failed to copy:", err);
            showCopyFeedback("Failed!");
        }
    });

    const cardContent = card.querySelector(".card-content");
    const changelogBtn = card.querySelector("[data-toggle-changelog]");
    const changelogContainer = card.querySelector("[data-changelog]");
    const patchesBtn = card.querySelector("[data-toggle-patches]");
    const patchesContainer = card.querySelector("[data-patches-content]");
    const viewState = cardViewStates.get(bundle.id) || {
        section: undefined,
        changelogScrollTop: 0,
        patchesScrollTop: 0
    };

    const setActiveSection = (section, refreshGlobal = true, persist = true) => {
        const showChangelog = section === "changelog";
        const showPatches = section === "patches";

        if (changelogBtn && changelogContainer) {
            changelogContainer.hidden = !showChangelog;
            if (showChangelog && !changelogContainer.hasChildNodes()) {
                changelogContainer.innerHTML = cachedMarkdown(bundle.id, 'changelog', bundle.description);
                void catalog.file("bundles/" + bundle.id + ".json").then(full => {
                    if (changelogContainer.isConnected)
                        changelogContainer.innerHTML = cachedMarkdown(bundle.id, "full-changelog", full.description);
                }).catch(async error => {
                    if (await recoverGeneration(error)) return;
                    if (changelogContainer.isConnected) changelogContainer.textContent = error.message;
                });
            }
            if (showChangelog) restoreScrollTop(changelogContainer, viewState.changelogScrollTop);
            changelogBtn.dataset.expanded = String(showChangelog);
            changelogBtn.textContent = showChangelog ? "Hide changelog" : "Show changelog";
        }

        if (patchesBtn && patchesContainer) {
            patchesContainer.hidden = !showPatches;
            if (showPatches && !patchesContainer.hasChildNodes()) {
                patchesContainer.textContent = "Loading patches...";
                void (bundle.filteredPatches ? Promise.resolve(bundle.patches) : bundlePatches(bundle))
                    .then(patches => {
                        if (patchesContainer.isConnected)
                            patchesContainer.innerHTML = cachedPatchList(patches);
                    }).catch(async error => {
                        if (await recoverGeneration(error)) return;
                        if (patchesContainer.isConnected) patchesContainer.textContent = error.message;
                    });
            }
            if (showPatches) restoreScrollTop(patchesContainer, viewState.patchesScrollTop);
            patchesBtn.dataset.expanded = String(showPatches);
            patchesBtn.textContent = showPatches ? "Hide patches" : `Show patches (${bundle.filteredPatches ? bundle.patches.length : (bundle.metadataStatus === "verified" ? bundle.patchCount : "unverified")})`;
        }

        if (cardContent) cardContent.classList.toggle("active", !!section);
        if (persist) {
            viewState.section = section;
            cardViewStates.set(bundle.id, viewState);
        }
        // Row heights are re-measured automatically: virtualizer.measureElement
        // registers each row with a ResizeObserver, so expanding a changelog or
        // patch list corrects the virtual layout without a manual pass.
        if (refreshGlobal) updateAllChangelogsButton();
    };

    card.setActiveSection = setActiveSection;
    let initialSection = viewState.section;
    if (initialSection === undefined) {
        initialSection = allChangelogsExpanded && changelogBtn ? "changelog" : null;
    }
    if (initialSection === "changelog" && !changelogBtn) initialSection = null;
    if (initialSection === "patches" && !patchesBtn) initialSection = null;
    setActiveSection(initialSection, false, false);

    changelogContainer?.addEventListener("scroll", () => {
        viewState.changelogScrollTop = changelogContainer.scrollTop;
        cardViewStates.set(bundle.id, viewState);
    }, { passive: true });
    patchesContainer?.addEventListener("scroll", () => {
        viewState.patchesScrollTop = patchesContainer.scrollTop;
        cardViewStates.set(bundle.id, viewState);
    }, { passive: true });

    changelogBtn?.addEventListener("click", () => {
        setActiveSection(changelogBtn.dataset.expanded === "true" ? null : "changelog");
    });

    patchesBtn?.addEventListener("click", () => {
        setActiveSection(patchesBtn.dataset.expanded === "true" ? null : "patches");
    });
}

function updateAllChangelogsButton() {
    const hasChangelogs = filteredBundles.some(bundle => bundle.description);
    toggleAllChangelogs.disabled = !hasChangelogs;
    toggleAllChangelogs.textContent = allChangelogsExpanded ? "Hide all changelogs" : "Show all changelogs";
}

function renderPatch(patch) {
    const packages = (patch.compatiblePackages || []).map(pkg => {
        const versionsText = pkg.versions?.filter(Boolean).join(', ') || 'all versions';
        return `<span class="package-tag">
            <span class="package-name">${escapeHtml(pkg.name)}</span>
            <span class="package-versions">${escapeHtml(versionsText)}</span>
        </span>`;
    }).join('');

    return `<div class="patch-item">
        <div class="patch-name">${escapeHtml(patch.name || 'Unnamed patch')}</div>
        ${patch.description ? `<div class="patch-description">${escapeHtml(patch.description)}</div>` : ''}
        ${packages ? `<div class="patch-packages">${packages}</div>` : ''}
    </div>`;
}

function sourceName(sourceUrl, ownerName, repoName) {
    try {
        const path = new URL(sourceUrl).pathname.replace(/^\/+|\/+$/g, '');
        return path || [ownerName, repoName].filter(Boolean).join('/');
    } catch {
        return [ownerName, repoName].filter(Boolean).join('/') || sourceUrl;
    }
}

function releaseTagUrl(bundle) {
    try {
        const source = new URL(bundle.sourceUrl);
        const repositoryUrl = `${source.origin}${source.pathname.replace(/\/+$/, '')}`;
        const tag = encodeURIComponent(bundle.version);

        if (gitHosts[source.host] === 'gitlab') {
            return `${repositoryUrl}/-/releases/${tag}`;
        }
        if (['github', 'gitea'].includes(gitHosts[source.host])) {
            return `${repositoryUrl}/releases/tag/${tag}`;
        }

        const download = new URL(bundle.downloadUrl);
        const downloadPrefix = `${source.pathname.replace(/\/+$/, '')}/releases/download/`;
        if (download.origin === source.origin && download.pathname.startsWith(downloadPrefix)) {
            const downloadedTag = download.pathname.slice(downloadPrefix.length).split('/')[0];
            if (downloadedTag) return `${repositoryUrl}/releases/tag/${downloadedTag}`;
        }
    } catch {
        // Keep the version as plain text when the API URLs cannot identify a release page.
    }

    return null;
}

function debounce(callback, delay) {
    let timeout;
    return () => {
        clearTimeout(timeout);
        timeout = setTimeout(callback, delay);
    };
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function renderMarkdown(text) {
    if (!text) return '';
    return DOMPurify.sanitize(marked.parse(text));
}

function formatDate(dateString) {
    try {
        if (!dateString) return "";
        const date = new Date(releaseTimestamp(dateString));
        if (Number.isNaN(date.getTime())) return "";
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);

        if (diffMins < 60) {
            return `${diffMins} minute${diffMins !== 1 ? 's' : ''} ago`;
        } else if (diffHours < 24) {
            return `${diffHours} hour${diffHours !== 1 ? 's' : ''} ago`;
        } else if (diffDays < 7) {
            return `${diffDays} day${diffDays !== 1 ? 's' : ''} ago`;
        } else {
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric'
            });
        }
    } catch (e) {
        return dateString;
    }
}
