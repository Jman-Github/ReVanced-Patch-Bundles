import { gitHosts } from "./hosts.js";

export class CatalogError extends Error {
  constructor(message, status = 400) { super(message); this.status = status; }
}
export function normalizeSource(value) {
  let url;
  try { url = new URL(value.includes("://") ? value : "https://" + value); }
  catch { throw new CatalogError("Invalid source URL"); }
  let host = url.hostname.toLowerCase();
  let path;
  try { path = decodeURIComponent(url.pathname).replace(/^\/+|\/+$/g, "").replace(/\.git$/, ""); }
  catch { throw new CatalogError("Invalid encoded source URL"); }
  if (host === "api.github.com") { host = "github.com"; path = path.replace(/^repos\//, ""); }
  const kind = gitHosts[host === "github.com" && url.hostname === "api.github.com" ?
    "github.com" : url.host.toLowerCase()];
  if (kind === "gitlab") path = path.replace(/^api\/v4\/projects\//, "").split("/-/")[0];
  if (kind === "github") path = path.replace(/^api\/v3\/repos\//, "").replace(/^repos\//, "");
  if (kind === "gitea") path = path.replace(/^api\/v1\/repos\//, "");
  let parts = path.split("/");
  if (!kind || parts.length < 2 ||
      parts.some(p => !p || p === "." || p === ".."))
    throw new CatalogError("Expected a repository URL on a configured Git host");
  if (kind !== "gitlab") parts = parts.slice(0, 2);
  if (!["http:", "https:"].includes(url.protocol) || url.username || url.password)
    throw new CatalogError("Expected a repository URL without credentials");
  return (host === "github.com" ? "https://github.com" : url.origin) + "/" + parts.join("/");
}
export function catalogOrigins(config, fallback) {
  if (!config.live_data) return [fallback];
  const repo = config.repository.split("/").map(encodeURIComponent).join("/");
  return ["https://raw.githubusercontent.com/" + repo + "/" +
    encodeURIComponent(config.data_branch) + "/" + (config.database_path ?? "database") + "/", fallback];
}
export function bundleImportPath(bundle, pinned = false) {
  const params = new URLSearchParams({ source_url: bundle.sourceUrl,
    version: pinned ? bundle.version : "latest",
    channel: bundle.isPrerelease ? "prerelease" : "stable" });
  return "/api/v3/bundle?" + params;
}
export function releaseTimestamp(value) {
  let date = String(value ?? "");
  // Legacy snapshots store UTC dates without a timezone suffix.
  if (/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?$/.test(date)) date += "Z";
  const parsed = Date.parse(date);
  return Number.isFinite(parsed) ? parsed : -Infinity;
}
export function compareReleaseDates(a, b) {
  const left = releaseTimestamp(a.created_at), right = releaseTimestamp(b.created_at);
  return left === right ? 0 : right - left;
}
export function pagination(args = {}, maximum = 100) {
  const limit = Number(args.limit ?? 25), offset = Number(args.offset ?? 0);
  if (!Number.isInteger(limit) || limit < 1 || limit > maximum ||
      !Number.isInteger(offset) || offset < 0 || offset > 10000)
    throw new CatalogError("limit must be 1–" + maximum + "; offset must be 0–10000");
  return { limit, offset };
}
let regexMatcher = () => { throw new CatalogError("Regex filters are available through the API"); };
export function configureRegexMatcher(matcher) { regexMatcher = matcher; }
let aggregateMatcher = () => { throw new CatalogError("Aggregate filters are available through the API"); };
export function configureAggregateMatcher(matcher) { aggregateMatcher = matcher; }
let textComparator = (a,b) => a < b ? -1 : a > b ? 1 : 0;
export function configureTextComparator(compare) { textComparator = compare; }
export function isTimestampField(row, key) {
  // GraphQL follows the upstream column types: release and repository dates
  // are text; only refresh-job dates are timestamps. REST keeps date sorting.
  const kind = row?.__kind ?? row?.__aggregateKind;
  return kind ? kind === "refresh_jobs" &&
    ["started_at", "completed_at"].includes(key) : key.endsWith("_at");
}
export function compareValues(left, right, timestamp = false) {
  if (timestamp) { left = Date.parse(left); right = Date.parse(right); }
  if (typeof left === "string" && typeof right === "string") return textComparator(left,right);
  return left < right ? -1 : left > right ? 1 : 0;
}
let caseFolder = value => value.toLowerCase();
export function configureCaseFolder(folder) { caseFolder = folder; }
function like(value, pattern, insensitive) {
  if (value == null) return false;
  pattern = String(pattern);
  if (pattern.length > 512) throw new CatalogError("Search pattern too long");
  const text = Array.from(insensitive ? caseFolder(String(value)) : String(value));
  const glob = [];
  const characters = Array.from(insensitive ? caseFolder(pattern) : pattern);
  for (let position = 0; position < characters.length; position++) {
    if (characters[position] === "\\") {
      if (++position === characters.length) throw new CatalogError("Incomplete LIKE escape");
      glob.push({ literal: characters[position] });
    } else glob.push({ value: characters[position] });
  }
  // SQL wildcards with bounded greedy matching; avoid regex backtracking.
  let i = 0, j = 0, star = -1, checkpoint = 0;
  while (i < text.length) {
    if (glob[j]?.value === "%") { star = j++; checkpoint = i; }
    else if (glob[j]?.value === "_" || (glob[j]?.literal ?? glob[j]?.value) === text[i]) { i++; j++; }
    else if (star >= 0) { j = star + 1; i = ++checkpoint; }
    else return false;
  }
  while (glob[j]?.value === "%") j++;
  return j === glob.length;
}
function combineConditions(items, predicate, disjunction = false) {
  let unknown = false;
  for (const item of items) {
    const result = predicate(item);
    if (result === disjunction) return disjunction;
    if (result == null) unknown = true;
  }
  return unknown ? null : !disjunction;
}
export function matches(row, where = {}, depth = 0) {
  return filterResult(row, where, depth) === true;
}
export function filterResult(row, where, depth = 0) {
  if (!where || typeof where !== "object" || Array.isArray(where) || depth > 12)
    throw new CatalogError("Invalid or excessively nested filter");
  // Keep SQL UNKNOWN until the complete condition has been evaluated. Collapsing
  // a missing value to false early would make NOT include it incorrectly.
  return combineConditions(Object.entries(where), ([key, condition]) => {
    if (key === "_and" || key === "_or") {
      if (!Array.isArray(condition)) throw new CatalogError("Logical filters must be arrays");
      return combineConditions(condition, c => filterResult(row, c, depth + 1), key === "_or");
    }
    if (key === "_not") {
      const result = filterResult(row, condition, depth + 1);
      return result == null ? null : !result;
    }
    if (condition == null) return true;
    if (key.endsWith("_aggregate") && Array.isArray(row[key.slice(0,-10)]))
      return aggregateMatcher(row[key.slice(0,-10)], condition);
    if (!(key in row)) throw new CatalogError("Unsupported filter field: " + key);
    const rawValue = row[key];
    const timestamp = isTimestampField(row, key) && typeof rawValue === "string" &&
      Number.isFinite(Date.parse(rawValue));
    const value = timestamp ? Date.parse(rawValue) : rawValue;
    // Relationship predicates use EXISTS: unknown comparisons in a related
    // row cannot satisfy the relation, and an empty relation is false.
    if (Array.isArray(value)) return value.some(v => matches(v, condition, depth + 1));
    if (value && typeof value === "object") return matches(value, condition, depth + 1);
    return combineConditions(Object.entries(condition ?? {}), ([op, input]) => {
      const expected = timestamp && input != null && op !== "_is_null" ?
        Array.isArray(input) ? input.map(v => Date.parse(v)) : Date.parse(input) : input;
      switch (op) {
        case "_eq": return value == null || expected == null ? null : value === expected;
        case "_neq": return value == null || expected == null ? null : value !== expected;
        case "_in": case "_nin": {
          const found = !expected.length ? false : value == null ? null :
            expected.includes(value) ? true : expected.includes(null) ? null : false;
          return op === "_in" || found == null ? found : !found;
        }
        case "_is_null": return (value == null) === expected;
        case "_ilike": case "_like":
          return value == null || expected == null ? null : like(value, expected, op === "_ilike");
        case "_nlike": case "_nilike":
          return value == null || expected == null ? null : !like(value, expected, op === "_nilike");
        case "_regex": case "_iregex": case "_nregex": case "_niregex":
        case "_similar": case "_nsimilar": {
          if (value == null || expected == null) return null;
          const found = regexMatcher(String(value), expected, op);
          return op.startsWith("_n") ? !found : found;
        }
        case "_gt": return value == null || expected == null ? null : compareValues(value, expected) > 0;
        case "_gte": return value == null || expected == null ? null : compareValues(value, expected) >= 0;
        case "_lt": return value == null || expected == null ? null : compareValues(value, expected) < 0;
        case "_lte": return value == null || expected == null ? null : compareValues(value, expected) <= 0;
        default: throw new CatalogError("Unsupported filter operator: " + op);
      }
    });
  });
}
function sortKeys(order, prefix = []) {
  return (Array.isArray(order) ? order : [order]).flatMap(part =>
    Object.entries(part ?? {}).flatMap(([key, direction]) =>
      typeof direction === "object" ? sortKeys(direction, [...prefix, key]) :
        [{ path: [...prefix, key], direction }]));
}
export function selectRows(rows, args = {}, maximum = 100) {
  const { limit, offset } = pagination(args, maximum);
  let result = rows.filter(row => matches(row, args.where ?? {}));
  const keys = sortKeys(args.order_by ?? { id: "asc" });
  if (keys.some(k => !["asc", "desc", "asc_nulls_first", "asc_nulls_last",
                      "desc_nulls_first", "desc_nulls_last"].includes(k.direction)))
    throw new CatalogError("Invalid order direction");
  result = result.slice().sort((a, b) => {
    for (const { path, direction } of keys) {
      const leftValue = path.reduce((v, k) => v?.[k], a);
      const rightValue = path.reduce((v, k) => v?.[k], b);
      const parent = path.slice(0, -1).reduce((v, k) => v?.[k], a);
      const timestamp = isTimestampField(parent, path.at(-1));
      const left = timestamp && leftValue != null ? Date.parse(leftValue) : leftValue;
      const right = timestamp && rightValue != null ? Date.parse(rightValue) : rightValue;
      if (left == null && right == null) continue;
      const ascending = direction.startsWith("asc");
      const nullsFirst = direction.endsWith("nulls_first") ||
        (!ascending && !direction.endsWith("nulls_last"));
      if (left == null || right == null) return left == null ? (nullsFirst ? -1 : 1) :
        (nullsFirst ? 1 : -1);
      const compared = compareValues(left,right);
      if (compared) return ascending ? compared : -compared;
    }
    return String(a.id ?? a.name).localeCompare(String(b.id ?? b.name));
  });
  if (args.distinct_on?.length) {
    const seen = new Set();
    result = result.filter(row => {
      const key = JSON.stringify(args.distinct_on.map(field => row[field]));
      if (seen.has(key)) return false;
      seen.add(key); return true;
    });
  }
  return { data: result.slice(offset, offset + limit), total: result.length, limit, offset };
}
export function packageFilterMatches(packages, query) {
  const value = query.trim().toLowerCase();
  const [name, version] = value.split("@", 2);
  return packages.some(pkg => version !== undefined ?
    pkg.name.toLowerCase().includes(name) &&
      (!version || !pkg.versions.length || pkg.versions.some(v => String(v).toLowerCase() === version)) :
    pkg.name.toLowerCase().includes(value) ||
      pkg.versions.some(v => String(v).toLowerCase().includes(value)));
}
export function patchPackages(patch) {
  return patch.packages.flatMap(p => (p.versions.length ? p.versions : [null]).map(version =>
    ({ package: { name: p.name, version }, patch_id: patch.id })));
}
export class Catalog {
  constructor(base, fetcher = fetch, enforceBudget = true) {
    this.enforceBudget = enforceBudget;
    this.base = base.endsWith("/") ? base : base + "/";
    this.fetcher = (...args) => fetcher.call(globalThis, ...args);
    this.loaded = new Map();
    this.bytes = 0;
    this.requests = 0;
  }
  async initialize() {
    const response = await this.fetcher(new URL("manifest.json", this.base), { cache: "no-cache" });
    if (!response.ok) throw new CatalogError("Catalog manifest unavailable", 503);
    const manifest = await response.json();
    if (manifest.schema_version !== 1 ||
        !/^snapshots\/[a-f0-9]{24}$/.test(manifest.snapshot) ||
        manifest.snapshot !== "snapshots/" + manifest.generation)
      throw new CatalogError("Invalid catalog generation", 503);
    if (manifest.snapshot_ref !== undefined && !/^[a-f0-9]{40}$/.test(manifest.snapshot_ref))
      throw new CatalogError("Invalid catalog snapshot reference",503);
    this.manifest = manifest;
    this.snapshotBase = new URL(this.base);
    // The branch manifest can outlive retention at HEAD. Commit URLs keep
    // lazy reads available even after that generation is pruned from the branch.
    if (manifest.snapshot_ref && this.snapshotBase.hostname === "raw.githubusercontent.com") {
      const parts = this.snapshotBase.pathname.split("/");
      if (parts.length < 5) throw new CatalogError("Invalid GitHub catalog origin",503);
      parts[3] = manifest.snapshot_ref;
      this.snapshotBase.pathname = parts.join("/");
    }
    return this;
  }
  async file(name) {
    if (!this.loaded.has(name)) {
      const metadata = this.manifest.files[name];
      if (!metadata || name.includes("..") || name.startsWith("/"))
        throw new CatalogError("Unknown catalog index", 503);
      this.requests++;
      this.bytes += metadata.bytes;
      if (this.enforceBudget && (this.requests > 36 || this.bytes > 12 * 1024 * 1024))
        throw new CatalogError("Query exceeds catalog budget; narrow the source or package filter", 422);
      this.loaded.set(name, (async () => {
        const response = await this.fetcher(new URL(this.manifest.snapshot + "/" + name, this.snapshotBase));
        if (!response.ok) {
          const error = new CatalogError("Catalog generation unavailable; retry shortly", 503);
          error.generationUnavailable = response.status === 404 || response.status === 410;
          throw error;
        }
        const bytes = new Uint8Array(await response.arrayBuffer());
        if (bytes.length !== metadata.bytes) throw new CatalogError("Catalog size mismatch", 503);
        const hash = [...new Uint8Array(await crypto.subtle.digest("SHA-256", bytes))]
          .map(n => n.toString(16).padStart(2, "0")).join("");
        if (hash !== metadata.sha256) throw new CatalogError("Catalog integrity mismatch", 503);
        return JSON.parse(new TextDecoder().decode(bytes));
      })());
    }
    try { return await this.loaded.get(name); }
    catch (error) { this.loaded.delete(name); throw error; }
  }
  async sources() { return this.file("sources.json"); }
  async bundles() {
    const sources = new Map((await this.sources()).map(source => [source.id, source]));
    return (await this.file("bundles.json"))
      .filter(bundle => sources.get(bundle.source_id)?.enabled !== false).map(bundle => ({
      ...bundle, source: sources.get(bundle.source_id)
    }));
  }
  async patchRows({ q = "", package: packageName, bundle_id: bundleId, bundle_ids: bundleIds, page_cursor = 0,
                    page_count = 12, all = false, include_unverified = false, patch_id: patchId, patch_ids: patchIds } = {}) {
    const index = await this.file("patch-index.json");
    let pages = index.pages;
    function intersect(candidate) {
      const selected = new Set(candidate ?? []);
      pages = pages.filter(page => selected.has(page));
    }
    if (patchId != null && index.patch_ids) intersect(index.patch_ids[String(patchId)]);
    if (patchIds && index.patch_ids)
      intersect(patchIds.flatMap(id => index.patch_ids[String(id)] ?? []));
    if (bundleId) intersect(index.bundles[bundleId]);
    if (bundleIds) intersect(bundleIds.flatMap(id => index.bundles[id] ?? []));
    if (packageName) intersect(index.packages[packageName]);
    q = q.toLowerCase();
    if (q.length > 512) throw new CatalogError("Search text too long");
    const characters = Array.from(q);
    if (characters.length >= 3) {
      const buckets = new Map();
      for (let i = 0; i < characters.length - 2; i++) {
        const gram = characters.slice(i, i + 3).join("");
        const bucket = gram.codePointAt(0) % 16;
        if (!buckets.has(bucket)) buckets.set(bucket, await this.file("search/" + bucket + ".json"));
        intersect(buckets.get(bucket)[gram]);
      }
    }
    if (all && pages.length > 24)
      throw new CatalogError("Patch query spans too many shards; filter by bundle or package", 422);
    if (!Number.isInteger(+page_cursor) || +page_cursor < 0 || +page_cursor > pages.length)
      throw new CatalogError("Invalid page_cursor");
    const selected = all ? pages : pages.slice(+page_cursor, +page_cursor + page_count);
    const bundles = new Map((await this.bundles()).map(b => [b.id, b]));
    const rows = (await Promise.all(selected.map(page => this.file(page)))).flat()
      .filter(p => bundles.has(p.bundle_id) && (!patchIds || patchIds.includes(p.legacy_id)) &&
        (include_unverified || p.metadata_status === "verified") &&
        (!q || ((p.name ?? "") + " " + (p.description ?? "")).toLowerCase().includes(q)) &&
        (!bundleId || p.bundle_id === bundleId) &&
        (!bundleIds || bundleIds.includes(p.bundle_id)) &&
        (!packageName || p.packages.some(pkg => pkg.name === packageName)))
      .map(p => ({ ...p, bundle: bundles.get(p.bundle_id), patch_packages: patchPackages(p) }));
    const next = +page_cursor + selected.length;
    return { rows, next_cursor: next < pages.length ? next : null,
             candidate_pages: pages.length };
  }
}
