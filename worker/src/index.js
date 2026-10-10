import site from "../../config/site.json" with { type: "json" };
import { Catalog, CatalogError, catalogOrigins, compareReleaseDates, normalizeSource, pagination, selectRows } from "../../shared/catalog.js";
import { runGraphQL, withPostgresLocale } from "./graphql.js";
import { openapi } from "./openapi.js";
import { liveJobs, mergeJobs } from "./jobs.js";
export { RefreshStatus } from "./jobs.js";
export { CatalogSubscriptions } from "./subscriptions.js";

const MAX_RESPONSE = 2 * 1024 * 1024;
async function limitedText(response, maximum) {
  if (+response.headers.get("content-length") > maximum)
    throw new CatalogError("Payload exceeds size limit", 413);
  const reader = response.body?.getReader();
  if (!reader) return "";
  let length = 0;
  const chunks = [];
  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      length += value.length;
      if (length > maximum) throw new CatalogError("Payload exceeds size limit", 413);
      chunks.push(value);
    }
  } finally {
    await reader.cancel();
  }
  const bytes = new Uint8Array(length);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  return new TextDecoder().decode(bytes);
}
function corsHeaders(request, env) {
  const allowed = (env.CORS_ORIGINS ?? site.website).split(",").map(s => s.trim());
  const origin = request.headers.get("Origin");
  const headers = { "Vary": "Origin", "Access-Control-Expose-Headers": "ETag, X-Catalog-Generation" };
  if (origin && allowed.includes(origin)) headers["Access-Control-Allow-Origin"] = origin;
  return headers;
}
async function jsonResponse(request, env, data, status, generation, cacheable = true) {
  let body = JSON.stringify(data);
  if (new TextEncoder().encode(body).length > MAX_RESPONSE) {
    status = 422; body = JSON.stringify({ error: "Response too large; reduce the query limit" });
    cacheable = false;
  }
  const headers = { ...corsHeaders(request, env), "Content-Type": "application/json; charset=utf-8",
    "X-Content-Type-Options": "nosniff",
    "Cache-Control": cacheable && status === 200 ? "public, max-age=60" : "no-store" };
  if (generation) headers["X-Catalog-Generation"] = generation;
  const hash = [...new Uint8Array(await crypto.subtle.digest("SHA-256",
    new TextEncoder().encode((generation ?? "") + body)))]
    .map(n => n.toString(16).padStart(2, "0")).join("");
  headers.ETag = '"' + hash + '"';
  if (status === 200 && request.headers.get("If-None-Match") === headers.ETag)
    return new Response(null, { status: 304, headers });
  return new Response(body, { status, headers });
}
function cacheFetcher(env, context) {
  let cacheReads = 0;
  return async url => {
    // Cache API calls share the Free plan's 50-call quota with fetch.
    // At most 37 fetches plus five match/put pairs = 47 calls on a cold cache.
    const cache = /\/manifest\.json$/.test(String(url)) ? null :
      cacheReads++ < 5 ? globalThis.caches?.default : null;
    const key = new Request(url);
    const cached = cache && await cache.match(key);
    if (cached) return cached;
    const upstream = await (env.FETCH?.fetch?.bind(env.FETCH) ?? env.FETCH ?? fetch)(url, {
      redirect: "manual", signal: AbortSignal.timeout(10000), cache: "no-store"
    });
    if (!upstream.ok) return upstream;
    const immutable = /\/snapshots\/[a-f0-9]{24}\//.test(String(url));
    const text = await limitedText(upstream, 12 * 1024 * 1024);
    const response = new Response(text, { headers: {
      "Content-Type": "application/json",
      "Cache-Control": immutable ? "public, max-age=31536000, immutable" : "public, max-age=60"
    } });
    if (cache && context?.waitUntil) context.waitUntil(cache.put(key, response.clone()));
    return response;
  };
}
function channel(value) {
  value = value.trim().toLowerCase();
  const aliases = { any: "latest", latest: "latest", stable: "stable", dev: "dev", prerelease: "dev" };
  if (!Object.hasOwn(aliases, value)) throw new CatalogError("channel must be any, latest, stable, dev, or prerelease");
  return aliases[value];
}
function dto(bundle) {
  return { created_at: String(bundle.created_at ?? "").split("Z")[0], description: bundle.description,
    version: bundle.version, download_url: bundle.download_url,
    signature_download_url: bundle.signature_download_url === "N/A" ? "" : (bundle.signature_download_url ?? ""),
    bundle_type: bundle.bundle_type,
    source: { url: bundle.source.url, host: bundle.source.host,
      namespace: bundle.source.namespace, repo: bundle.source.repo },
    file_hash: bundle.file_hash, need_patches_update: bundle.need_patches_update,
    metadata_status: bundle.metadata_status, patcher_runtime: bundle.patcher_runtime };
}
function legacyDto(bundle) {
  return { created_at: String(bundle.created_at ?? "").split("Z")[0],
    description: bundle.description ?? "", version: bundle.version,
    download_url: bundle.download_url, signature_download_url:
      bundle.signature_download_url === "N/A" ? "" : (bundle.signature_download_url ?? "") };
}
function filteredBundles(bundles, params) {
  const q = (params.get("q") ?? "").toLowerCase();
  const source = params.get("source") ?? params.get("source_url");
  const canonical = source?.includes("/") ? normalizeSource(source).toLowerCase() : null;
  const selectedChannel = params.has("channel") ? channel(params.get("channel")) : null;
  return bundles.filter(b =>
    (!q || (b.description + " " + b.version + " " + b.source.url + " " +
      b.source.aliases.join(" ")).toLowerCase().includes(q)) &&
    (!source || b.source_id === source || b.source.aliases.includes(source) ||
      b.source.url.toLowerCase() === canonical) &&
    (!params.has("ecosystem") || b.ecosystem === params.get("ecosystem")) &&
    (!params.has("version") || b.version === params.get("version")) &&
    (!params.has("package") || b.packages.includes(params.get("package"))) &&
    (!selectedChannel || b.channels.includes(selectedChannel)) &&
    (!params.has("metadata_status") || b.metadata_status === params.get("metadata_status")));
}
function restArgs(params, fields) {
  const args = pagination(Object.fromEntries(params));
  if (params.has("sort")) {
    const sort = params.get("sort");
    if (!fields.includes(sort)) throw new CatalogError("Unsupported sort field");
    const direction = params.get("order") ?? "asc";
    args.order_by = { [sort]: direction };
  }
  return args;
}
async function rest(catalog, url) {
  const path = url.pathname.replace(/\/$/, "");
  const params = url.searchParams;
  if (path === "/health") return { ok: true, generation: catalog.manifest.generation,
                                  counts: catalog.manifest.counts };
  if (path === "/api/v3/bundle") {
    const sourceUrl = params.get("source_url");
    const version = params.get("version")?.trim();
    if (!sourceUrl || !version) throw new CatalogError("source_url and version are required");
    const source = normalizeSource(sourceUrl).toLowerCase();
    const latest = version.toLowerCase() === "latest";
    const mode = params.get("channel")?.trim() || "any";
    if (latest && !params.get("channel")?.trim())
      throw new CatalogError("channel is required for version=latest");
    const selectedChannel = channel(mode);
    const bundles = (await catalog.bundles()).filter(b => b.source.url.toLowerCase() === source &&
      (latest ? b.is_latest : b.version === version) &&
      (mode === "any" || selectedChannel === "latest" ||
        (selectedChannel === "stable" ? !b.is_prerelease : b.is_prerelease)));
    bundles.sort((a, b) =>
      compareReleaseDates(a, b) ||
      Number(b.channels.length > 0) - Number(a.channels.length > 0));
    if (!bundles.length) throw new CatalogError("No cached bundle matches source and version", 404);
    return dto({ ...bundles[0], ...(await catalog.file("bundles/" + bundles[0].id + ".json")),
                 source: bundles[0].source });
  }
  const numeric = path.match(/^\/api\/v1\/bundle\/([0-9]+)$/);
  if (numeric) {
    const bundle = (await catalog.bundles()).find(b => b.legacy_id === Number(numeric[1]));
    if (!bundle) throw new CatalogError("Bundle not found", 404);
    return legacyDto({ ...bundle, ...(await catalog.file("bundles/" + bundle.id + ".json")) });
  }
  const compatibility = path.match(/^\/api\/v[12]\/bundle\/([^/]+)\/([^/]+)\/([^/]+)$/);
  if (compatibility) {
    const owner = decodeURIComponent(compatibility[1]), repo = decodeURIComponent(compatibility[2]);
    const version = decodeURIComponent(compatibility[3]);
    const v2 = path.startsWith("/api/v2/");
    if (v2 && version !== "latest") throw new CatalogError("Endpoint not found", 404);
    if (v2 && !params.has("channel")) throw new CatalogError("channel is required");
    const mode = v2 ? channel(params.get("channel").trim().toLowerCase()) :
      params.get("prerelease") === "true" ? "dev" : "stable";
    // Reference v1/v2 lookups join repository metadata, regardless of host.
    // In particular, renamed repositories use their recorded current name.
    const bundles = (await catalog.bundles()).filter(bundle => {
      const metadata = bundle.source.source_metadatum ?? {};
      return (metadata.owner_name ?? bundle.source.namespace) === owner &&
        (metadata.repo_name ?? bundle.source.repo) === repo &&
        (version === "latest" ? bundle.is_latest &&
          (mode === "latest" || bundle.is_prerelease === (mode === "dev")) :
          bundle.version === version);
    });
    if (version === "latest") bundles.sort(compareReleaseDates);
    if (!bundles.length) throw new CatalogError("Bundle not found", 404);
    const bundle = bundles[0];
    return legacyDto({ ...bundle, ...(await catalog.file("bundles/" + bundle.id + ".json")) });
  }
  const normalized = path.replace(/^\/api\/v1/, "");
  if (normalized === "/sources") {
    const q = (params.get("q") ?? "").toLowerCase();
    const source = params.get("source_url");
    const rows = (await catalog.sources()).filter(s =>
      (!source || s.url.toLowerCase() === normalizeSource(source).toLowerCase()) &&
      (!q || (s.url + " " + s.aliases.join(" ")).toLowerCase().includes(q)));
    return selectRows(rows, restArgs(params, ["id", "url", "repo"]));
  }
  if (normalized === "/bundles" || normalized === "/releases") {
    const rows = filteredBundles(await catalog.bundles(), params);
    return selectRows(rows, restArgs(params, ["id", "version", "created_at", "patch_count"]));
  }
  if (normalized === "/packages") {
    const q = (params.get("q") ?? "").toLowerCase();
    const rows = (await catalog.file("packages.json")).filter(p => !q || p.name.toLowerCase().includes(q));
    return selectRows(rows, restArgs(params, ["name"]));
  }
  if (normalized === "/availability") return catalog.file("availability.json");
  const patchesMatch = normalized.match(/^\/bundles\/([a-f0-9]{24})\/patches$/);
  if (normalized === "/patches" || patchesMatch) {
    const bundleId = patchesMatch?.[1] ?? params.get("bundle_id");
    const eligibleBundles = filteredBundles(await catalog.bundles(), new URLSearchParams(
      [...params].filter(([key]) => ["source", "source_url", "ecosystem", "channel"].includes(key))));
    const result = await catalog.patchRows({ q: params.get("q") ?? "",
      bundle_ids: eligibleBundles.map(b => b.id),
      package: params.get("package"), bundle_id: bundleId,
      page_cursor: params.get("page_cursor") ?? 0,
      include_unverified: params.get("include_unverified") === "true" });
    let rows = result.rows;
    if (params.has("app_version")) rows = rows.filter(p =>
      p.packages.some(pkg => (!params.has("package") || pkg.name === params.get("package")) &&
        (!pkg.versions.length || pkg.versions.includes(params.get("app_version")))));
    return { ...selectRows(rows, restArgs(params, ["id", "name"])),
             next_cursor: result.next_cursor, candidate_pages: result.candidate_pages };
  }
  const detail = normalized.match(/^\/(sources|bundles)\/([a-f0-9]+)$/);
  if (detail) {
    const rows = detail[1] === "sources" ? await catalog.sources() : await catalog.bundles();
    const row = rows.find(r => r.id === detail[2]);
    if (!row) throw new CatalogError("Record not found", 404);
    return detail[1] === "bundles" ? {
      ...row, ...(await catalog.file("bundles/" + row.id + ".json")), source: row.source
    } : row;
  }
  throw new CatalogError("Endpoint not found", 404);
}
async function createCatalog(env, context) {
  const base = env.DATA_BASE_URL ?? site.website + "/" + site.database_path + "/";
  const parsedBase = new URL(base);
  if (parsedBase.protocol !== "https:" && !["localhost", "127.0.0.1"].includes(parsedBase.hostname))
    throw new CatalogError("Invalid data origin configuration", 503);
  const origins = env.DATA_BASE_URL ? [base] : catalogOrigins(site,base);
  let failure;
  for (const origin of origins) {
    try {
      const catalog = await new Catalog(origin,cacheFetcher(env,context)).initialize();
      catalog.regexLocale = env.POSTGRES_LOCALE ?? site.postgres_locale;
      if (env.REFRESH_STATUS || env.JOBS_FETCH) catalog.liveJobs = () => liveJobs(env);
      return catalog;
    } catch(error) { failure = error; }
  }
  throw failure;
}
export async function executeCatalogQuery(env, context, payload, options = {}) {
  const result = await runGraphQL(await createCatalog({...env,LIVE_SUBSCRIPTION:true},context),payload,options);
  if (new TextEncoder().encode(JSON.stringify(result)).length > MAX_RESPONSE)
    throw new CatalogError("Response too large; reduce the query limit",422);
  return result;
}
export default {
  async fetch(request, env = {}, context) {
    const url = new URL(request.url);
    let generation;
    try {
      if (url.href.length > 12000) throw new CatalogError("Request URL too long", 414);
      if (request.method === "OPTIONS") {
        return new Response(null, { status: 204, headers: {
          ...corsHeaders(request, env), "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type, If-None-Match", "Access-Control-Max-Age": "86400"
        } });
      }
      const graphql = ["/graphql", "/v1/graphql", "/hasura/v1/graphql"].includes(url.pathname);
      if (graphql && request.headers.get("Upgrade")?.toLowerCase() === "websocket") {
        const origin = request.headers.get("Origin");
        const allowed = (env.CORS_ORIGINS ?? site.website).split(",").map(s => s.trim());
        if (origin && !allowed.includes(origin)) throw new CatalogError("Origin not allowed",403);
        if (!env.SUBSCRIPTIONS) throw new CatalogError("Subscriptions unavailable",503);
        // Isolate each connection so alarm work scales with connected clients.
        return env.SUBSCRIPTIONS.get(env.SUBSCRIPTIONS.idFromName("connection-" + crypto.randomUUID())).fetch(request);
      }
      if (!["GET", "POST"].includes(request.method) || (request.method === "POST" && !graphql))
        throw new CatalogError("Read-only endpoint; method not allowed", 405);
      if (url.pathname === "/api.json" || url.pathname === "/openapi.json")
        return jsonResponse(request, env, openapi, 200, undefined);
      if (["/swagger", "/swagger/", "/graphiql", "/graphiql/"].includes(url.pathname)) {
        const page = url.pathname.startsWith("/swagger") ? "/api-docs/" : "/graphiql/";
        return Response.redirect(site.website + page, 302);
      }
      const jobMatch = url.pathname.match(/^\/api\/v1\/refresh\/status\/([^/]+)$/);
      if (url.pathname === "/refresh-jobs" || jobMatch) {
        let rows;
        if (jobMatch && /^[1-9][0-9]{0,15}$/.test(jobMatch[1])) {
          rows = await liveJobs(env,jobMatch[1]);
        } else {
          if (jobMatch && !/^(?:[a-f0-9]{24}|[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12})$/i.test(jobMatch[1]))
            throw new CatalogError("Invalid refresh job ID");
          const catalog = await createCatalog(env,context);
          const recorded = catalog.manifest.files["refresh-jobs.json"] ?
            await catalog.file("refresh-jobs.json") : [];
          if (jobMatch) {
            rows = recorded.filter(row => row.job_id === jobMatch[1]);
            if (rows[0]?.actions_run_id && ["STARTED","PENDING","RUNNING"].includes(rows[0].status)) {
              // Recover phase status after abrupt runner cancellation.
              try {
                rows = mergeJobs(rows,await liveJobs(env,rows[0].actions_run_id))
                  .filter(row => row.job_id === jobMatch[1]);
              } catch { /* Retain the published status during a GitHub outage. */ }
            }
          } else {
            let live = [];
            try { live = await liveJobs(env); }
            catch (error) { if (!recorded.length) throw error; }
            rows = mergeJobs(recorded,live);
          }
          if (jobMatch && !rows.length) throw new CatalogError("Refresh job not found",404);
        }
        rows = mergeJobs(rows,[]);
        const running = jobMatch && ["STARTED","PENDING","RUNNING"].includes(rows[0].status);
        const dto = jobMatch ? {jobId:rows[0].job_id,type:rows[0].job_type,status:rows[0].status,
          startedAt:rows[0].started_at,completedAt:rows[0].completed_at,error:rows[0].error} :
          selectRows(rows,restArgs(url.searchParams,["id","status","started_at","completed_at"]));
        return jsonResponse(request,env,dto,running ? 202 : 200,undefined,false);
      }
      const catalog = await createCatalog(env,context);
      generation = catalog.manifest.generation;
      let result;
      if (graphql) {
        let payload;
        if (request.method === "POST") {
          if (!request.headers.get("Content-Type")?.includes("application/json"))
            throw new CatalogError("Expected application/json", 415);
          payload = JSON.parse(await limitedText(request, 32768));
        } else payload = { query: url.searchParams.get("query"),
          variables: JSON.parse(url.searchParams.get("variables") ?? "{}"),
          operationName: url.searchParams.get("operationName") ?? undefined };
        result = await runGraphQL(catalog, payload);
      } else result = await withPostgresLocale(catalog.regexLocale ?? "en_US.utf8",
        () => rest(catalog, url));
      return jsonResponse(request, env, result, 200, generation, !result.errors);
    } catch (error) {
      const status = error instanceof CatalogError ? error.status : error instanceof SyntaxError ? 400 : 503;
      const message = error instanceof CatalogError || status === 400 ? error.message : "Catalog request failed; retry shortly";
      return jsonResponse(request, env, { error: message }, status, generation, false);
    }
  }
};
