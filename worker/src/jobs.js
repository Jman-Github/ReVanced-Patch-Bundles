import site from "../../config/site.json" with { type: "json" };
import { CatalogError } from "../../shared/catalog.js";

const repository = () => site.repository.split("/").map(encodeURIComponent).join("/");
const base = () => "https://api.github.com/repos/" + repository();
const workflow = "catalog-updater.yml";
const MAX_BYTES = 512 * 1024;
async function github(env, path) {
  if (env.STATUS_GATE) await env.STATUS_GATE();
  const response = await (env.JOBS_FETCH?.fetch?.bind(env.JOBS_FETCH) ?? env.JOBS_FETCH ?? fetch)(base() + path, {
    headers: { Accept: "application/vnd.github+json", "User-Agent": "Patch-Bundle-Registry",
      ...(env.GITHUB_STATUS_TOKEN ? { Authorization: "Bearer " + env.GITHUB_STATUS_TOKEN } : {}) },
    redirect: "manual", signal: AbortSignal.timeout(10000)
  });
  if (response.status === 404) throw new CatalogError("Refresh job not found", 404);
  if (!response.ok) {
    const error = new CatalogError("Refresh status temporarily unavailable",503);
    const retry = response.headers.get("Retry-After");
    const delay = retry && /^\d+$/.test(retry) ? Number(retry)*1000 : Date.parse(retry ?? "")-Date.now();
    const exhausted = response.headers.get("X-RateLimit-Remaining") === "0";
    error.retryAt = Date.now() + Math.max(60000, Number.isFinite(delay) ? delay : 0,
      exhausted ? Number(response.headers.get("X-RateLimit-Reset"))*1000-Date.now() : 0);
    throw error;
  }
  const reader = response.body.getReader(); let size = 0; const chunks = [];
  try {
    while (true) {
      const {value,done} = await reader.read(); if (done) break;
      size += value.length;
      if (size > MAX_BYTES) throw new CatalogError("Refresh status response exceeds budget", 503);
      chunks.push(value);
    }
  } finally { await reader.cancel(); }
  const bytes = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk,offset); offset += chunk.length; }
  return JSON.parse(new TextDecoder().decode(bytes));
}
export function refreshJob(run) {
  // GitHub run IDs exceed GraphQL Int; reserve the upper half of positive Ints.
  let hash = 2166136261;
  for (const c of String(run.id)) hash = Math.imul(hash ^ c.charCodeAt(0),16777619) >>> 0;
  const finished = run.status === "completed";
  const success = run.conclusion === "success";
  return { id: 1073741824 + hash % 1073741823, job_id: String(run.id), job_type: "ALL",
    status: finished ? (success ? "COMPLETED" : "FAILED") : "STARTED",
    started_at: run.run_started_at ?? run.created_at, completed_at: finished ? run.updated_at : null,
    error: finished && !success ? "GitHub Actions: " + (run.conclusion ?? "unknown result") : null,
    run_url: run.html_url, run_attempt: run.run_attempt };
}
function validRun(run) {
  return Number.isSafeInteger(run.id) && run.id > 0 &&
    run.path?.split("@")[0] === ".github/workflows/" + workflow;
}
export async function fetchJobs(env, id) {
  if (id !== undefined) {
    if (!/^[1-9][0-9]{0,15}$/.test(String(id)) || !Number.isSafeInteger(Number(id)))
      throw new CatalogError("Invalid refresh job ID");
    const run = await github(env,"/actions/runs/" + id);
    if (!validRun(run)) throw new CatalogError("Refresh job not found",404);
    return [refreshJob(run)];
  }
  // Dispatch can originate on the default branch; the workflow itself checks
  // out the configured data branch before updating the registry.
  const response = await github(env,"/actions/workflows/" + workflow + "/runs?per_page=25");
  if (!Array.isArray(response.workflow_runs)) throw new CatalogError("Invalid refresh status response",503);
  return response.workflow_runs.filter(validRun).map(refreshJob);
}
// The object coalesces reads across clients; unauthenticated public GitHub reads
// stay below the hourly quota at one request every two minutes.
export class RefreshStatus {
  constructor(ctx,env) { this.ctx = ctx; this.env = env; this.inFlight = new Map(); }
  async reserve(individual) {
    await this.ctx.storage.transaction(async storage => {
      const now = Date.now();
      const cooldown = await storage.get("github-cooldown") ?? 0;
      if (cooldown > now) throw new CatalogError("Refresh status is cooling down; retry later",503);
      let budget = await storage.get("github-budget");
      if (!budget || budget.reset <= now) budget = {reset:now+3600000,count:0,individual:0};
      const maximum = this.env.GITHUB_STATUS_TOKEN ? 4500 : 55;
      if (budget.count >= maximum) throw new CatalogError("Refresh status quota exhausted; retry later",503);
      if (individual && (budget.individual ?? 0) >= (this.env.GITHUB_STATUS_TOKEN ? 1500 : 25))
        throw new CatalogError("Individual status lookup quota exhausted; use recent refresh jobs",503);
      budget.count++; if (individual) budget.individual=(budget.individual ?? 0)+1;
      await storage.put("github-budget",budget);
    });
  }
  async fetch(request) {
    const id = new URL(request.url).searchParams.get("id");
    if (id && (!/^[1-9][0-9]{0,15}$/.test(id) || !Number.isSafeInteger(Number(id))))
      return Response.json({error:"Invalid refresh job ID"},{status:400});
    const key = id ? "job:" + id : "recent";
    if (this.inFlight.has(key)) return (await this.inFlight.get(key)).clone();
    const pending = this.read(key,id);
    this.inFlight.set(key,pending);
    try { return (await pending).clone(); } finally { this.inFlight.delete(key); }
  }
  async read(key,id) {
    const now = Date.now();
    let entry = await this.ctx.storage.get(key);
    try {
      const recent = id && await this.ctx.storage.get("recent");
      const known = recent?.expires > now && recent.rows.find(row => row.job_id === id);
      // Reusing a list entry must not restart its freshness window. A newer
      // list also supersedes an older individual response for the same job.
      if (known && recent.expires >= (entry?.expires ?? 0)) return Response.json([known]);
      if (entry?.expires > now) return Response.json(entry.rows);
      const rows = await fetchJobs({...this.env,STATUS_GATE:()=>this.reserve(Boolean(id))},id ?? undefined);
      entry = { rows, expires: Date.now() + (this.env.GITHUB_STATUS_TOKEN ? 15000 : 120000) };
      // Keep a bounded cache of individual lookups.
      if (id) {
        const entries = await this.ctx.storage.list({prefix:"job:",limit:100});
        if (entries.size >= 100 && !entries.has(key)) await this.ctx.storage.delete(entries.keys().next().value);
      }
      await this.ctx.storage.put(key,entry);
      return Response.json(rows);
    } catch(error) {
      if (Number.isFinite(error.retryAt)) await this.ctx.storage.put("github-cooldown",error.retryAt);
      return Response.json({error:error.message},{status:error.status ?? 503});
    }
  }
}
export function mergeJobs(recorded, live) {
  const normalize = row => ["PENDING","RUNNING"].includes(row.status) ? {...row,status:"STARTED"} : row;
  recorded = recorded.map(normalize); live = live.map(normalize);
  const runs = new Map(live.map(row => [row.job_id, row]));
  const rows = recorded.map(row => {
    const run = runs.get(row.actions_run_id);
    if (!run || !["STARTED"].includes(row.status)) return row;
    if (row.actions_run_attempt > run.run_attempt) return row;
    const retried = row.actions_run_attempt && run.run_attempt > row.actions_run_attempt;
    if (!retried && !["COMPLETED","FAILED"].includes(run.status)) return row;
    return {...row, status:"FAILED", completed_at:run.completed_at ?? run.started_at,
      error:retried ? "GitHub Actions run was retried before this phase completed" :
        run.error ?? "Refresh ended before this phase completed"};
  });
  const merged = new Map(rows.map(row => [row.job_id,row]));
  live.forEach(row => merged.set(row.job_id,row));
  return [...merged.values()];
}
export async function liveJobs(env,id) {
  if (!env.REFRESH_STATUS) return fetchJobs(env,id);
  const response = await env.REFRESH_STATUS.get(env.REFRESH_STATUS.idFromName("public")).fetch(
    "https://status.internal/?" + (id === undefined ? "" : "id=" + encodeURIComponent(id)));
  const result = await response.json();
  if (!response.ok) throw new CatalogError(result.error,response.status);
  return result;
}
