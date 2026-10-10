import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import worker from "../src/index.js";
import { Catalog, bundleImportPath, compareReleaseDates, matches, normalizeSource, packageFilterMatches } from "../../shared/catalog.js";

import { fixture } from "./fixture.js";
async function call(state, path, options = {}) {
  const response = await worker.fetch(new Request("https://api.test" + path, options), state.env);
  return { response, body: response.status === 304 ? null : await response.json() };
}
async function query(state, queryText, variables) {
  return call(state, "/graphql", { method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: queryText, variables }) });
}
test("cached v3 lookup normalizes URLs and selects latest/stable/prerelease/exact", async () => {
  const state = fixture();
  const base = "/api/v3/bundle?source_url=" + encodeURIComponent("https://api.github.com/repos/owner/repo");
  const latest = await call(state, base + "&version=latest&channel=any");
  assert.equal(latest.response.status, 200);
  assert.equal(latest.body.version, "v1");
  assert.equal(latest.body.bundle_type, "ReVanced:V4");
  assert.equal(latest.body.file_hash, "c".repeat(64));
  assert.equal((await call(state, base + "&version=latest&channel=prerelease")).body.version, "v2-dev");
  assert.equal((await call(state, base + "&version=v1")).body.version, "v1");
  assert.equal((await call(state, base + "&version=latest")).response.status, 400);
  assert.equal((await call(state, base + "&version=absent")).response.status, 404);
  assert(state.requests.every(url => url.startsWith("https://example.test/database/")));
});
test("REST pagination, package compatibility, freshness, search, and update status", async () => {
  const state = fixture();
  assert.equal((await call(state, "/bundles?limit=1&offset=1")).body.data.length, 1);
  assert.equal((await call(state, "/patches?q=ads&package=com.video&app_version=1.0")).body.data.length, 1);
  assert.equal((await call(state, "/patches?app_version=3.0")).body.data.length, 0);
  assert.equal((await call(state, "/patches?include_unverified=true")).body.data.length, 2);
  assert.equal((await call(state, "/bundles?metadata_status=stale")).body.data[0].need_patches_update, true);
  assert.equal((await call(state, "/packages?q=video")).body.data[0].versions.length, 2);
  assert.equal((await call(state, "/bundles?limit=101")).response.status, 400);
  assert.equal((await call(state, "/bundles?sort=invalid")).response.status, 400);
});
test("GraphQL variables, aliases, nested source/packages and aggregates", async () => {
  const state = fixture();
  const result = await query(state, `
    query Catalog($where: bundle_bool_exp!) {
      selected: bundle(where: $where, order_by: {created_at: desc}, limit: 5) {
        id version need_patches_update file_hash
        source { url source_metadata: source_metadatum { owner_name repo_stars } }
        patches { name patch_packages { package { name version } } }
        patches_aggregate { aggregate { count } }
      }
      bundle_aggregate { aggregate { count } }
    }`, { where: { source: { url: { _eq: "https://github.com/owner/repo" } },
                          is_prerelease: { _eq: false } } });
  assert.equal(result.body.errors, undefined, JSON.stringify(result.body));
  assert.equal(result.body.data.selected.length, 1);
  assert.equal(result.body.data.selected[0].patches[0].name, "Hide ads");
  assert.equal(result.body.data.selected[0].patches[0].patch_packages[1].package.version, "2.0");
  assert.equal(result.body.data.selected[0].patches_aggregate.aggregate.count, 1);
  assert.equal(result.body.data.bundle_aggregate.aggregate.count, 2);
});
test("GraphQL relationship filters, sorting and unavailable old fingerprint", async () => {
  const state = fixture();
  const result = await query(state, `{
    patch(where: {patch_packages: {package: {name: {_eq: "com.video"}}}}) {
      name bundle { version source { url } }
    }
  }`);
  assert.equal(result.body.errors, undefined, JSON.stringify(result.body));
  assert.equal(result.body.data.patch.length, 2);
  const obsolete = await query(state, "{ bundle { patcher_failure_fingerprint } }");
  assert.equal(obsolete.body.errors, undefined);
  assert.deepEqual(obsolete.body.data.bundle.map(b => b.patcher_failure_fingerprint), [null, null]);
});
test("GraphQL rejects unknown fields, mutations, excessive depth and repeated expensive aliases", async () => {
  const state = fixture();
  assert((await query(state, "{ bundle { missing } }")).body.errors);
  assert.equal((await query(state, "mutation { delete_bundle }")).response.status, 400);
  const costly = await query(state, "{ " + Array.from({ length: 20 }, (_, i) =>
    "b" + i + ":bundle(limit:100){patches(limit:100){name description}}").join(" ") + " }");
  assert.equal(costly.response.status, 400);
});
test("ETag conditional requests and production CORS", async () => {
  const state = fixture();
  const first = await call(state, "/health", { headers: { Origin: "https://website.test" } });
  assert.equal(first.response.headers.get("Access-Control-Allow-Origin"), "https://website.test");
  const second = await call(state, "/health", { headers: { "If-None-Match": first.response.headers.get("ETag") } });
  assert.equal(second.response.status, 304);
  assert.equal((await call(state, "/health", { headers: { Origin: "https://untrusted.test" } }))
    .response.headers.get("Access-Control-Allow-Origin"), null);
});
test("file integrity and missing generation fail closed", async () => {
  const state = fixture();
  state.bodies["bundles.json"] = "[]";
  assert.equal((await call(state, "/bundles")).response.status, 503);
  const missing = fixture();
  delete missing.bodies["sources.json"];
  assert.equal((await call(missing, "/sources")).response.status, 503);
});
test("request, response, method and shard budgets are bounded", async () => {
  const state = fixture();
  assert.equal((await call(state, "/sources", { method: "DELETE" })).response.status, 405);
  assert.equal((await call(state, "/graphql", { method: "POST", body: "x".repeat(40000),
    headers: { "Content-Type": "application/json" } })).response.status, 413);
  const catalog = await new Catalog(state.env.DATA_BASE_URL, state.env.FETCH).initialize();
  catalog.requests = 36;
  await assert.rejects(() => catalog.file("sources.json"), /budget/);
});
test("normalization supports GitLab subgroups and immutable request memoization", async () => {
  assert(matches({name:"%literal"}, {name:{_ilike:"%"}}));
  assert(matches({name:"Hide Ads"}, {name:{_ilike:"%ADS%"}}));
  assert(!matches({name:"abc"}, {name:{_like:"%a%a%a%a%a%"}}));
  assert.equal(normalizeSource("https://gitlab.com/api/v4/projects/group%2Fteam%2Frepo"),
    "https://gitlab.com/group/team/repo");
  assert.equal(normalizeSource("github.com/Owner/Repo.git/"), "https://github.com/Owner/Repo");
  const state = fixture();
  const catalog = await new Catalog(state.env.DATA_BASE_URL, state.env.FETCH).initialize();
  await Promise.all([catalog.sources(), catalog.sources()]);
  assert.equal(state.requests.filter(r => r.endsWith("/sources.json")).length, 1);
});
test("current generated catalog serves REST through a mocked Pages origin", async () => {
  const root = new URL("../../database/", import.meta.url);
  const env = { DATA_BASE_URL: "https://local.test/database/", FETCH: async input => {
    const path = new URL(input).pathname.replace("/database/", "");
    try { return new Response(await readFile(new URL(path, root))); }
    catch { return new Response("", { status: 404 }); }
  } };
  const result = await call({ env }, "/sources?limit=3");
  assert.equal(result.response.status, 200);
  assert.equal(result.body.data.length, 3);
  assert(result.body.total >= 400);
});

test("nested bundle/source relationship filters use indexed packages", async () => {
  const state = fixture();
  const result = await query(state, `{
    bundle(where:{patches:{patch_packages:{package:{name:{_eq:"com.video"}}}}}) { id }
    source(where:{bundles:{version:{_eq:"v1"}}}) { url bundles(where:{version:{_eq:"v1"}}) { version } }
    bundle_aggregate(where:{patches:{name:{_ilike:"%ADS%"}}}) { aggregate { count } }
  }`);
  assert.equal(result.body.errors, undefined, JSON.stringify(result.body));
  assert.equal(result.body.data.bundle.length, 2);
  assert.equal(result.body.data.source[0].bundles[0].version, "v1");
  assert.equal(result.body.data.bundle_aggregate.aggregate.count, 2);
});
test("v1 prerelease and v2 required channel match repository lookup conventions", async () => {
  const state = fixture();
  assert.equal((await call(state, "/api/v1/bundle/owner/repo/latest")).body.version, "v1");
  assert.equal((await call(state, "/api/v1/bundle/owner/repo/latest?prerelease=true")).body.version, "v2-dev");
  assert.equal((await call(state, "/api/v2/bundle/owner/repo/latest")).response.status, 400);
  assert.equal((await call(state, "/api/v2/bundle/owner/repo/latest?channel=prerelease")).body.version, "v2-dev");
});
test("cold-cache calls fit the shared free-plan subrequest budget", async () => {
  const pages = Array.from({length:24}, (_,i) => "patches/" + String(i).padStart(5,"0") + ".json");
  const overrides = Object.fromEntries(pages.map(p => [p, []]));
  overrides["patch-index.json"] = {pages, packages:{}, bundles:{}};
  const state = fixture(overrides);
  let cacheCalls = 0;
  globalThis.caches = {default:{
    match: async () => { cacheCalls++; return undefined; },
    put: async () => { cacheCalls++; }
  }};
  try {
    const pending = [];
    const response = await worker.fetch(new Request("https://api.test/graphql", {
      method:"POST", headers:{"Content-Type":"application/json"},
      body:JSON.stringify({query:"{ patch(limit:100) { name } }"})
    }), state.env, {waitUntil: p => pending.push(p)});
    const result = await response.json();
    await Promise.all(pending);
    assert.equal(result.errors, undefined, JSON.stringify(result));
    assert.equal(state.requests.length, 29);
    assert.equal(cacheCalls, 10);
    assert(state.requests.length + cacheCalls < 50);
  } finally { delete globalThis.caches; }
});

test("invalid GraphQL payloads and malformed encoded URLs return client errors", async () => {
  const state = fixture();
  for (const body of ["null", "[]", '{"query":"{source{id}}","variables":[]}']) {
    assert.equal((await call(state, "/graphql", { method:"POST",
      headers:{"Content-Type":"application/json"}, body })).response.status, 400);
  }
  const source = encodeURIComponent("https://github.com/owner/%ZZ");
  assert.equal((await call(state, "/api/v3/bundle?source_url=" + source +
    "&version=latest&channel=any")).response.status, 400);
});

test("REST patch text search combines with source, ecosystem and channel filters", async () => {
  const state = fixture();
  for (const filter of ["source=demo", "source_url=https://github.com/owner/repo",
                        "ecosystem=revanced", "channel=stable"]) {
    const result = await call(state, "/patches?q=ads&package=com.video&app_version=1.0&" + filter);
    assert.equal(result.response.status, 200);
    assert.deepEqual(result.body.data.map(p => p.bundle_id), [state.bundle.id], filter);
  }
  const dev = await call(state, "/patches?q=ads&channel=dev&include_unverified=true");
  assert.deepEqual(dev.body.data.map(p => p.bundle_id), [state.dev.id]);
});
test("GraphQL logical status filters include explicitly requested stale patches", async () => {
  const state = fixture();
  const result = await query(state, `{
    patch(where:{_and:[{metadata_status:{_eq:"stale"}}]}) { metadata_status }
    patch_aggregate(where:{_or:[{metadata_status:{_eq:"stale"}}]}) { aggregate { count } }
    bundle(where:{catalog_id:{_eq:"${state.dev.id}"}}) {
      patches(where:{_and:[{metadata_status:{_eq:"stale"}}]}) { metadata_status }
    }
  }`);
  assert.equal(result.body.errors, undefined, JSON.stringify(result.body));
  assert.deepEqual(result.body.data.patch, [{metadata_status:"stale"}]);
  assert.equal(result.body.data.patch_aggregate.aggregate.count, 1);
  assert.deepEqual(result.body.data.bundle[0].patches, [{metadata_status:"stale"}]);
});


test("latest imports follow category flags and exclude retired releases", async () => {
  const base = fixture();
  const current = { ...base.bundle, version: "v0", created_at: "2025-01-01T00:00:00" };
  const history = { ...base.bundle, id: "e".repeat(24), version: "v9",
    created_at: "2026-06-01T00:00:00", channels: [], is_latest: false };
  const dev = { ...base.dev, created_at: "2026-07-01T00:00:00" };
  const state = fixture({ "bundles.json": [current, dev, history],
    ["bundles/" + current.id + ".json"]: current,
    ["bundles/" + dev.id + ".json"]: dev,
    ["bundles/" + history.id + ".json"]: history });
  const path = "/api/v3/bundle?source_url=https://github.com/owner/repo&version=";
  for (const [channel, version] of [["any", dev.version], ["latest", dev.version], ["stable", current.version]]) {
    const result = await call(state, path + "latest&channel=" + channel);
    assert.equal(result.response.status, 200);
    assert.equal(result.body.version, version);
  }
  assert.equal((await call(state, path + "latest&channel=prerelease")).body.version, dev.version);
  assert.equal((await call(state, path + history.version)).body.version, history.version);
  const retired = { ...current, channels: [], is_latest: false };
  const missing = fixture({ "bundles.json": [retired, history] });
  assert.equal((await call(missing, path + "latest&channel=any")).response.status, 404);
});

test("legacy numeric and exact-version imports return the upstream five-field DTO", async () => {
  const state = fixture();
  for (const path of ["/api/v1/bundle/1","/api/v1/bundle/owner/repo/v1"]) {
    const result = await call(state, path);
    assert.equal(result.response.status, 200);
    assert.equal(result.body.version, "v1");
    assert.deepEqual(Object.keys(result.body).sort(), [
      "created_at","description","download_url","signature_download_url","version"]);
  }
  assert.equal((await call(state,"/api/v1/bundle/99")).response.status,404);
  assert.equal((await call(state,"/api/v1/bundle/owner/repo/missing")).response.status,404);
});
test("all public GraphQL tables, primary keys, aggregate nodes and statistics work", async () => {
  const state = fixture({"refresh-jobs.json":[{id:1,job_id:"run",status:"COMPLETED",
    job_type:"BUNDLES",started_at:"2026-01-01T00:00:00Z",completed_at:"2026-01-01T00:01:00Z"}]});
  const result = await query(state, `{
    bundle_by_pk(id:1) { id source_fk catalog_id patches { id bundle_fk } }
    source_by_pk(id:1) { id source_metadatum { id source_fk source { id } } }
    source_metadata_by_pk(id:1) { repo_stars }
    patch_by_pk(id:1) { id bundle { id } }
    package_by_pk(id:1) { id name patch_packages { patch_fk patch { name } } }
    patch_package_by_pk(package_fk:1,patch_fk:1) { package { name } patch { id } }
    patch_package_aggregate { aggregate { count } nodes { package_fk patch_fk } }
    package_aggregate { aggregate { count(columns:[name],distinct:true) } nodes { version } }
    bundle_aggregate { aggregate { count min { id } max { id } sum { id } avg { id }
      variance { id } stddev_pop { id } } nodes { id } }
    refresh_jobs_by_pk(id:1) { status }
    refresh_jobs { id job_type }
  }`);
  assert.equal(result.body.errors,undefined,JSON.stringify(result.body));
  const data = result.body.data;
  assert.equal(data.bundle_by_pk.source_fk,1);
  assert.equal(data.bundle_by_pk.patches[0].bundle_fk,1);
  assert.equal(data.source_metadata_by_pk.repo_stars,12);
  assert.equal(data.patch_package_by_pk.patch.id,1);
  assert.equal(data.package_aggregate.aggregate.count,1);
  assert.equal(data.patch_package_aggregate.aggregate.count,4);
  assert.equal(data.bundle_aggregate.aggregate.sum.id,3);
  assert.equal(data.bundle_aggregate.aggregate.avg.id,1.5);
  assert.equal(data.bundle_aggregate.aggregate.variance.id,0.5);
  assert.equal(data.bundle_aggregate.nodes.length,2);
  assert.equal(data.refresh_jobs_by_pk.status,"COMPLETED");
});
test("version fragments, SQL escapes, regex, null ordering and variable defaults", async () => {
  assert(packageFilterMatches([{name:"com.video",versions:["19.16.39"]}],"19.16"));
  assert(packageFilterMatches([{name:"com.video",versions:["19.16.39"]}],"com.video@19.16.39"));
  assert(!packageFilterMatches([{name:"com.video",versions:["19.16.39"]}],"com.video@19.16"));
  assert(matches({name:"literal_percent%"},{name:{_like:"literal\\_percent\\%"}}));
  const result = await query(fixture(), `
    query Default($limit:Int=1) {
      bundle(order_by:{created_at:asc_nulls_first},limit:$limit) { id }
      patch(where:{name:{_iregex:"^hide [a-z]+$"}}) { name }
      patch_aggregate(where:{name:{_nilike:"%nothing%"}}) { aggregate { count } }
    }`);
  assert.equal(result.body.errors,undefined,JSON.stringify(result.body));
  assert.equal(result.body.data.bundle.length,1);
  assert.equal(result.body.data.patch.length,2);
  assert.equal(result.body.data.patch_aggregate.aggregate.count,2);
});
test("OpenAPI and standard GraphiQL introspection remain usable", async () => {
  const state=fixture();
  const spec=await call(state,"/api.json");
  assert.equal(spec.body.openapi,"3.0.3");
  assert(spec.body.paths["/api/v1/bundle/{id}"]);
  const {getIntrospectionQuery}=await import("graphql");
  const introspection=await query(state,getIntrospectionQuery());
  assert.equal(introspection.response.status,200,JSON.stringify(introspection.body));
  assert.equal(introspection.body.errors,undefined,JSON.stringify(introspection.body));
  assert(introspection.body.data.__schema.types.some(type=>type.name==="patch_package"));
  const swagger=await worker.fetch(new Request("https://api.test/swagger"),state.env);
  assert.equal(swagger.status,302);
});

test("relationship aggregates filter, order and paginate without truncating totals", async () => {
  const state=fixture();
  const result=await query(state,`{
    source(where:{bundles_aggregate:{count:{predicate:{_gt:1}}}}) { id }
    bundle(where:{patches_aggregate:{count:{predicate:{_eq:1}}}},
      order_by:{patches_aggregate:{count:desc}}) { id }
    package(where:{patch_packages_aggregate:{count:{predicate:{_gte:2}}}}) { name }
    bundle_aggregate(limit:1) { aggregate { count } nodes { id } }
    remaining:bundle_aggregate(offset:1) { aggregate { count sum { id } } }
  }`);
  assert.equal(result.body.errors,undefined,JSON.stringify(result.body));
  assert.equal(result.body.data.source.length,1);
  assert.equal(result.body.data.bundle.length,2);
  assert.equal(result.body.data.package.length,2);
  assert.equal(result.body.data.bundle_aggregate.aggregate.count,1);
});

test("generated catalog serves global patch counts and pages through indexes", async () => {
  const root=new URL("../../database/",import.meta.url);
  const requests=[];
  const state={env:{DATA_BASE_URL:"https://local.test/database/",FETCH:async input=>{
    const target=new URL(input).pathname.replace("/database/","");
    requests.push(target);
    try{return new Response(await readFile(new URL(target,root)));}
    catch{return new Response("",{status:404});}
  }}};
  const result=await query(state,`{
    patch(limit:10,offset:10) { id name bundle_fk }
    patch_aggregate { aggregate { count count_with_use:count(columns:[use])
      count_complete:count(columns:[id,name]) sum { id } } nodes { id } }
  }`);
  assert.equal(result.body.errors,undefined,JSON.stringify(result.body));
  assert.equal(result.body.data.patch.length,10);
  assert.equal(result.body.data.patch_aggregate.aggregate.count,11502);
  assert.equal(result.body.data.patch_aggregate.aggregate.count_complete,11502);
  assert.equal(result.body.data.patch_aggregate.nodes.length,25);
  assert(requests.filter(path=>path.includes("/patches/")).length<=2,JSON.stringify(requests));
  assert(requests.length<=8,JSON.stringify(requests));
});

test("timestamp comparisons match equivalent UTC offsets",()=> {
  assert(matches({created_at:"2026-01-01T02:00:00+02:00"},
    {created_at:{_eq:"2026-01-01T00:00:00Z"}}));
  assert(matches({created_at:"2026-01-01T02:00:00+02:00"},
    {created_at:{_lt:"2026-01-01T00:01:00Z"}}));
});

test("GraphQL relation predicates do not narrow returned patch rows", async () => {
  const base = fixture();
  const original = JSON.parse(base.bodies["patches/00000.json"]);
  const other = {...original[0], id:base.bundle.id+":1", legacy_id:3,
    name:"Other app", packages:[{name:"com.other",versions:[]}]};
  const state = fixture({
    "patches/00000.json":[...original,other],
    "packages.json":[{name:"com.video",versions:["1.0","2.0"]},{name:"com.other",versions:[]}],
    "patch-index.json":{pages:["patches/00000.json"],
      bundles:{[base.bundle.id]:["patches/00000.json"],[base.dev.id]:["patches/00000.json"]},
      packages:{"com.video":["patches/00000.json"],"com.other":["patches/00000.json"]}}
  });
  const result = await query(state, `{
    patch(where:{bundle:{patches:{patch_packages:{package:{name:{_eq:"com.video"}}}}}}) {
      name
    }
  }`);
  assert.equal(result.body.errors, undefined, JSON.stringify(result.body));
  assert.deepEqual(result.body.data.patch.map(p=>p.name),["Hide ads","Hide ads","Other app"]);
});
test("GraphQL distinct patch names are selected before pagination", async () => {
  const base = fixture();
  const original = JSON.parse(base.bodies["patches/00000.json"]);
  const other = {...original[0], id:base.bundle.id+":1", legacy_id:3, name:"Other"};
  const state = fixture({
    "patches/00000.json":[...original,other],
    "patch-index.json":{pages:["patches/00000.json"],
      bundles:{[base.bundle.id]:["patches/00000.json"],[base.dev.id]:["patches/00000.json"]},
      packages:{"com.video":["patches/00000.json"]},
      patch_ids:{"1":["patches/00000.json"],"2":["patches/00000.json"],"3":["patches/00000.json"]}}
  });
  const result = await query(state, "{patch(distinct_on:[name],limit:2){name}}");
  assert.equal(result.body.errors, undefined, JSON.stringify(result.body));
  assert.deepEqual(result.body.data.patch.map(p=>p.name),["Hide ads","Other"]);
});

test("browser manifest revalidates and expiry remains distinguishable from corruption", async () => {
  const state = fixture();
  let manifestOptions;
  const fetcher = async (input, options) => {
    if (new URL(input).pathname.endsWith("/manifest.json")) manifestOptions = options;
    return state.env.FETCH(input);
  };
  const catalog = await new Catalog(state.env.DATA_BASE_URL, fetcher, false).initialize();
  assert.equal(manifestOptions.cache, "no-cache");
  delete state.bodies["sources.json"];
  await assert.rejects(catalog.sources(), error =>
    error.status === 503 && error.generationUnavailable === true);
  const corrupt = fixture();
  corrupt.bodies["sources.json"] = "[]";
  const invalid = await new Catalog(corrupt.env.DATA_BASE_URL, corrupt.env.FETCH, false).initialize();
  await assert.rejects(invalid.sources(), error =>
    error.status === 503 && !error.generationUnavailable);
});

test("source relationship filters stay within the selected source shard budget", async () => {
  const base = fixture();
  const index = JSON.parse(base.bodies["patch-index.json"]);
  index.pages.push(...Array.from({length:25}, (_, i) => "patches/unrelated-" + i + ".json"));
  const state = fixture({"patch-index.json":index});
  const result = await query(state, `{
    source(where:{url:{_eq:"https://github.com/owner/repo"},
      bundles:{patches:{name:{_eq:"Hide ads"}}}}) { id }
    conjunct:source(where:{_and:[
      {url:{_eq:"https://github.com/owner/repo"}},
      {bundles:{patches:{_or:[{name:{_eq:"Hide ads"}},{name:{_eq:"Other"}}]}}}
    ]}) { id }
  }`);
  assert.equal(result.body.errors,undefined,JSON.stringify(result.body));
  assert.deepEqual(result.body.data.source,[{id:1}]);
  assert.deepEqual(result.body.data.conjunct,[{id:1}]);
  assert(!state.requests.some(url=>url.includes("unrelated-")));
});

test("scoped relationship predicates hydrate siblings without returning other bundles", async () => {
  const base=fixture();
  const original=JSON.parse(base.bodies["patches/00000.json"]);
  const video=original[0];
  const other={...original[1],name:"Other app",packages:[{name:"com.other",versions:[]}]};
  const index={pages:["patches/00000.json","patches/00001.json",
      ...Array.from({length:25},(_,i)=>"patches/unrelated-"+i+".json")],
    bundles:{[base.bundle.id]:["patches/00000.json"],[base.dev.id]:["patches/00001.json"]},
    packages:{"com.video":["patches/00000.json"],"com.other":["patches/00001.json"]},
    patch_ids:{"1":["patches/00000.json"],"2":["patches/00001.json"]}};
  const state=fixture({
    "patches/00000.json":[video],"patches/00001.json":[other],"patch-index.json":index,
    "packages.json":[{name:"com.video",versions:["1.0","2.0"]},{name:"com.other",versions:[]}]
  });
  const result=await query(state,`{
    patch(where:{bundle_fk:{_eq:1},bundle:{source:{bundles:{
      patches:{patch_packages:{package:{name:{_eq:"com.other"}}}}
    }}}}) { name }
    bundle(where:{id:{_eq:1}}) {
      patches(where:{bundle:{source:{bundles:{patches:{name:{_eq:"Other app"}}}}}}) { name }
    }
    source_metadata(where:{id:{_eq:1},source:{bundles:{patches:{name:{_eq:"Other app"}}}}}) { id }
    patch_package(where:{patch_fk:{_eq:1},patch:{bundle:{source:{bundles:{
      patches:{name:{_eq:"Other app"}}
    }}}}}) { patch_fk }
  }`);
  assert.equal(result.body.errors,undefined,JSON.stringify(result.body));
  assert.deepEqual(result.body.data.patch,[{name:"Hide ads"}]);
  assert.deepEqual(result.body.data.bundle,[{patches:[{name:"Hide ads"}]}]);
  assert.deepEqual(result.body.data.source_metadata,[{id:1}]);
  assert.deepEqual(result.body.data.patch_package,[{patch_fk:1},{patch_fk:1}]);
  const links=await query(state,`{
    patch_package(where:{patch_fk:{_eq:1},patch:{bundle:{source:{bundles:{
      patches:{name:{_eq:"Other app"}}
    }}}}}) { patch_fk }
    byPackage:patch_package(where:{package_fk:{_eq:1}}) { patch_fk }
    unknown:source_metadata(where:{id:{_eq:999},source:{bundles:{patches:{name:{_eq:"Other app"}}}}}) { id }
  }`);
  assert.equal(links.body.errors,undefined,JSON.stringify(links.body));
  assert.deepEqual(links.body.data.patch_package,[{patch_fk:1},{patch_fk:1}]);
  assert.deepEqual(links.body.data.byPackage,[{patch_fk:1}]);
  assert.deepEqual(links.body.data.unknown,[]);
  assert(!state.requests.some(url=>url.includes("unrelated-")));
});

test("latest import fallback compares release instants across UTC offsets", async () => {
  const base=fixture();
  const stable={...base.bundle,channels:["stable"],created_at:"2026-10-08T02:00:00+02:00"};
  const dev={...base.dev,created_at:"2026-10-08T00:30:00Z"};
  const state=fixture({"bundles.json":[stable,dev]});
  const result=await call(state,"/api/v3/bundle?source_url=https://github.com/owner/repo&version=latest&channel=any");
  assert.equal(result.response.status,200);
  assert.equal(result.body.version,"v2-dev");
});

test("release ordering treats legacy dates as UTC and missing dates as oldest", () => {
  const dates = [
    { created_at: null },
    { created_at: "2026-10-08T02:00:00+02:00" },
    { created_at: "2026-10-08T00:30:00" },
    { created_at: "invalid" },
  ];
  assert.deepEqual(dates.toSorted(compareReleaseDates), [dates[2], dates[1], dates[0], dates[3]]);
  assert.equal(compareReleaseDates(dates[2], { created_at: "2026-10-08T00:30:00Z" }), 0);
});

test("GraphQL nullable filters match omitted patch and repository metadata fields", async () => {
  const base = fixture();
  const [patch, stale] = JSON.parse(base.bodies["patches/00000.json"]);
  delete patch.use;
  const state = fixture({ "patches/00000.json": [patch, stale] });
  const result = await query(state, `{
    patch(where: {bundle_id: {_eq: "${base.bundle.id}"}, use: {_is_null: true}}) { name use }
    source_metadata(where: {repo_pushed_at: {_is_null: true}}) { id repo_pushed_at }
  }`);
  assert.equal(result.response.status, 200);
  assert.equal(result.body.errors, undefined);
  assert.deepEqual(result.body.data.patch, [{ name: "Hide ads", use: null }]);
  assert.deepEqual(result.body.data.source_metadata, [{ id: 1, repo_pushed_at: null }]);
});

test("website imports follow channels by default and pin explicitly selected versions", () => {
  const bundle={sourceUrl:"https://gitlab.com/group/sub/repo",version:"v1+release",isPrerelease:false};
  let url=new URL(bundleImportPath(bundle),"https://api.test");
  assert.equal(url.searchParams.get("version"),"latest");
  assert.equal(url.searchParams.get("source_url"),bundle.sourceUrl);
  assert.equal(url.searchParams.get("channel"),"stable");
  url=new URL(bundleImportPath({...bundle,isPrerelease:true},true),"https://api.test");
  assert.equal(url.searchParams.get("version"),"v1+release");
  assert.equal(url.searchParams.get("channel"),"prerelease");
});

test("legacy routes resolve current repository metadata across hosts and renames", async () => {
  const base = fixture();
  const original = JSON.parse(base.bodies["sources.json"])[0];
  for (const url of ["https://github.com/old-owner/old-repo",
                     "https://gitlab.com/team/subgroup/project",
                     "https://codeberg.org/team/project"]) {
    const source = {...original, url, source_metadatum: {
      ...original.source_metadatum, owner_name:"current-owner", repo_name:"current-repo"}};
    const state = fixture({"sources.json":[source]});
    for (const path of ["/api/v1/bundle/current-owner/current-repo/v1",
                       "/api/v1/bundle/current-owner/current-repo/latest",
                       "/api/v2/bundle/current-owner/current-repo/latest?channel=STABLE"]) {
      const result = await call(state,path);
      assert.equal(result.response.status,200,url+" "+path);
      assert.equal(result.body.version,"v1");
    }
    assert.equal((await call(state,"/api/v1/bundle/current-owner/current-repo/latest?prerelease=true")).body.version,"v2-dev");
    assert.equal((await call(state,"/api/v1/bundle/old-owner/old-repo/latest")).response.status,404);
    source.enabled=false;
    const disabled=fixture({"sources.json":[source]});
    assert.equal((await call(disabled,"/api/v1/bundle/current-owner/current-repo/v1")).response.status,404);
    assert.equal((await call(disabled,"/api/v3/bundle?source_url="+encodeURIComponent(url)+"&version=v1")).response.status,404);
  }
});

test("legacy exact-version imports ignore latest channel flags", async () => {
  const base=fixture();
  const history={...base.bundle,id:"e".repeat(24),version:"old/tag",channels:[],is_latest:false};
  const state=fixture({"bundles.json":[base.bundle,base.dev,history],
    ["bundles/"+history.id+".json"]:history});
  assert.equal((await call(state,"/api/v1/bundle/owner/repo/old%2Ftag")).body.version,"old/tag");
  assert.equal((await call(state,"/api/v2/bundle/owner/repo/latest")).response.status,400);
  assert.equal((await call(state,"/api/v2/bundle/owner/repo/v1?channel=stable")).response.status,404);
});

test("scoped package relationships hydrate peer patches for filters and ordering", async () => {
  const base=fixture();
  const original=JSON.parse(base.bodies["patches/00000.json"]);
  const first={...original[0],packages:[
    {name:"com.other",versions:[]},{name:"com.video",versions:["1.0"]}
  ]};
  const second={...original[1],name:"Peer patch",packages:[{name:"com.video",versions:["1.0"]}]};
  const index={pages:["patches/00000.json","patches/00001.json",
      ...Array.from({length:25},(_,i)=>"patches/unrelated-"+i+".json")],
    bundles:{[base.bundle.id]:["patches/00000.json"],[base.dev.id]:["patches/00001.json"]},
    packages:{"com.video":["patches/00000.json","patches/00001.json"],"com.other":["patches/00000.json"]},
    patch_ids:{"1":["patches/00000.json"],"2":["patches/00001.json"]}};
  const overrides={"patches/00000.json":[first],"patches/00001.json":[second],
    "patch-index.json":index,"packages.json":[
      {name:"com.video",versions:["1.0"]},{name:"com.other",versions:[]}
    ]};
  const cases=[
    ['patch_aggregate(where:{id:{_eq:1},patch_packages:{package:{patch_packages:{patch:{id:{_eq:2}}}}}}){aggregate{count} nodes{id}}',
      {patch_aggregate:{aggregate:{count:1},nodes:[{id:1}]}}],
    ['patch(where:{id:{_eq:1},_not:{patch_packages:{package:{patch_packages:{patch:{id:{_eq:2}}}}}}}){id}',
      {patch:[]}],
    ['patch(where:{id:{_eq:1},patch_packages_aggregate:{count:{filter:{package:{patch_packages:{patch:{id:{_eq:2}}}}},predicate:{_eq:1}}}}){id}',
      {patch:[{id:1}]}],
    ['patch(where:{id:{_eq:1},patch_packages:{package:{patch_packages:{patch:{id:{_eq:2}}}}}}){id}',
      {patch:[{id:1}]}],
    ['patch(where:{id:{_eq:1},patch_packages:{package:{patch_packages_aggregate:{count:{predicate:{_gte:2}}}}}}){id}',
      {patch:[{id:1}]}],
    ['patch_package(where:{patch_fk:{_eq:1},package:{patch_packages:{patch:{id:{_eq:2}}}}}){package{name}}',
      {patch_package:[{package:{name:"com.video"}}]}],
    ['patch_package(where:{patch_fk:{_eq:1}},order_by:{package:{patch_packages_aggregate:{count:desc}}},limit:1){package{name}}',
      {patch_package:[{package:{name:"com.video"}}]}],
    [`bundle(where:{id:{_eq:1}}) {
      patches(where:{
        patch_packages:{package:{patch_packages:{patch:{
          bundle:{patches:{name:{_eq:"Peer patch"}}}
        }}}}
      }) {id}
    }`,
      {bundle:[{patches:[{id:1}]}]}],
  ];
  for(const [selection,expected] of cases) {
    const state=fixture(overrides);
    const result=await query(state,"{"+selection+"}");
    assert.equal(result.body.errors,undefined,JSON.stringify(result.body));
    assert.deepEqual(result.body.data,expected,selection);
    assert(!state.requests.some(url=>url.includes("unrelated-")));
  }
});

test("relationship ordering honors mandatory source scope before reading shards", async () => {
  const base=fixture();
  const source=JSON.parse(base.bodies["sources.json"])[0];
  const unrelated=Array.from({length:25},(_,i)=>"patches/unrelated-"+i+".json");
  const other={...base.dev,id:"e".repeat(24),legacy_id:3,source_id:"s2"};
  const index=JSON.parse(base.bodies["patch-index.json"]);
  index.pages.push(...unrelated);
  index.bundles[other.id]=unrelated;
  const state=fixture({
    "sources.json":[source,{...source,id:"s2",legacy_id:2,url:"https://github.com/other/repo"}],
    "bundles.json":[base.bundle,base.dev,other],"patch-index.json":index
  });
  const result=await query(state,`{
    filtered:source(where:{id:{_eq:1},bundles:{patches:{name:{_eq:"Hide ads"}}}}) {id}
    bundle(where:{id:{_eq:1}},order_by:{patches_aggregate:{count:desc}}) {id}
    source(where:{_and:[{url:{_eq:"https://github.com/owner/repo"}}]},
      order_by:{bundles_aggregate:{sum:{patch_count:desc}}}) {id}
    ordered:source(where:{id:{_eq:1}},
      order_by:{source_metadatum:{source:{bundles_aggregate:{count:desc}}}}) {id}
  }`);
  assert.equal(result.body.errors,undefined,JSON.stringify(result.body));
  assert.deepEqual(result.body.data,{filtered:[{id:1}],bundle:[{id:1}],source:[{id:1}],ordered:[{id:1}]});
  assert(!state.requests.some(url=>url.includes("unrelated-")));
});

test("release descriptions remain searchable and orderable past 1000 characters",async()=>{
  const initial=fixture(),prefix="a".repeat(1000);
  const rows=[{...initial.bundle,description:prefix+"z tail-marker"},
    {...initial.dev,description:prefix+"b tail-marker"}];
  const state=fixture({"bundles.json":rows,...Object.fromEntries(
    rows.map(row=>["bundles/"+row.id+".json",row]))});
  const rest=await call(state,"/bundles?q=tail-marker");
  assert.equal(rest.response.status,200);
  assert.equal(rest.body.data.length,2);
  const result=await query(state,`{
    bundle(where:{description:{_like:"%tail-marker%"}},order_by:{description:asc}){
      version description
    }
    bundle_aggregate{aggregate{min{description}max{description}}}
  }`);
  assert.equal(result.body.errors,undefined,JSON.stringify(result.body));
  assert.deepEqual(result.body.data.bundle,[
    {version:rows[1].version,description:rows[1].description},
    {version:rows[0].version,description:rows[0].description}
  ]);
  assert.deepEqual(result.body.data.bundle_aggregate.aggregate,{
    min:{description:rows[1].description},max:{description:rows[0].description}
  });
});


test("unnamed patches preserve REST search, SQL null filters and app compatibility", async () => {
  const initial = fixture();
  const original = JSON.parse(initial.bodies["patches/00000.json"])[0];
  const state = fixture({"patches/00000.json": [{...original, name: null}]});
  const found = await call(state, "/patches?q=advertisements&package=com.video&app_version=1.0");
  assert.equal(found.body.data.length, 1);
  assert.equal(found.body.data[0].name, null);
  assert.equal(found.body.data[0].description, original.description);
  assert.equal((await call(state, "/patches?q=null")).body.data.length, 0);
  const graph = await query(state,
    '{patch(where:{name:{_is_null:true}}){name description patch_packages{package{name version}}}' +
    'patch_aggregate{aggregate{count countName:count(columns:[name]) min{name} max{name}}}}');
  assert.equal(graph.body.errors, undefined, JSON.stringify(graph.body));
  assert.equal(graph.body.data.patch.length, 1);
  assert.equal(graph.body.data.patch[0].name, null);
  assert.equal(graph.body.data.patch[0].patch_packages.length, 2);
  assert.deepEqual(graph.body.data.patch_aggregate.aggregate,
    {count:1, countName:0, min:{name:null}, max:{name:null}});
});

test("verified empty bundles and paused rejections remain distinct in REST and GraphQL", async () => {
  const initial = fixture();
  const empty = {...initial.bundle, patch_count:0, patch_list_available:true};
  const paused = {...initial.dev, need_patches_update:false, extraction_terminal:true,
    extraction_status:"runtime_parsing_failure", metadata_status:"missing"};
  const state = fixture({"bundles.json":[empty,paused], "patches/00000.json":[],
    ["bundles/" + empty.id + ".json"]:empty, ["bundles/" + paused.id + ".json"]:paused});
  const graph = await query(state,
    '{bundle(order_by:{id:asc}){metadata_status need_patches_update patches{name}' +
    'patches_aggregate{aggregate{count}}}}');
  assert.equal(graph.body.errors, undefined, JSON.stringify(graph.body));
  assert.deepEqual(graph.body.data.bundle, [
    {metadata_status:"verified",need_patches_update:false,patches:[],patches_aggregate:{aggregate:{count:0}}},
    {metadata_status:"missing",need_patches_update:false,patches:[],patches_aggregate:{aggregate:{count:0}}}
  ]);
  const detail = await call(state, "/bundles/" + empty.id);
  assert.equal(detail.body.metadata_status, "verified");
  assert.equal(detail.body.patch_count, 0);
  assert.equal((await call(state, "/bundles/" + paused.id)).body.need_patches_update, false);
});

test("Boolean aggregate filters support predicates, filters, distinct and SQL NULL semantics", async () => {
  const initial = fixture();
  const source = JSON.parse(initial.bodies["sources.json"])[0];
  const empty = {...source, id:"s2", legacy_id:2, url:"https://github.com/owner/empty", bundles:[],
    source_metadatum:{...source.source_metadatum,id:2}};
  const stable = {...initial.bundle, need_patches_update:false};
  const dev = {...initial.dev, need_patches_update:true};
  const unknown = {...stable,id:"c".repeat(24),legacy_id:3,need_patches_update:null};
  const state = fixture({"sources.json":[source,empty], "bundles.json":[stable,dev,unknown]});
  const sources = async where => {
    const result = await query(state, "{source(where:" + where + ",order_by:{id:asc}){id}}");
    assert.equal(result.body.errors, undefined, JSON.stringify(result.body));
    return result.body.data.source.map(row => row.id);
  };
  const condition = (op, predicate, filter = "", distinct = "") =>
    "{bundles_aggregate:{" + op + ":{arguments:need_patches_update,predicate:" +
      predicate + filter + distinct + "}}}";
  assert.deepEqual(await sources(condition("bool_and","{_eq:false}")), [1]);
  assert.deepEqual(await sources(condition("bool_or","{_eq:true}")), [1]);
  assert.deepEqual(await sources(condition("bool_or","{_eq:false}",",filter:{is_prerelease:{_eq:false}}")), [1]);
  assert.deepEqual(await sources(condition("bool_and","{_eq:false}","",",distinct:true")), [1]);
  const allNull = condition("bool_and","{_is_null:true}",",filter:{id:{_gt:2}}");
  assert.deepEqual(await sources(allNull), [1,2]);
  const unknownComparison = condition("bool_and","{_eq:true}",",filter:{id:{_gt:2}}");
  assert.deepEqual(await sources("{_not:" + unknownComparison + "}"), []);
  assert.deepEqual(await sources("{_or:[{id:{_eq:1}}," + unknownComparison + "]}"), [1]);
  // The filter can traverse nested patch aggregates, loading only the required relationships.
  assert.deepEqual(await sources(condition("bool_and","{_eq:false}",
    ",filter:{patches_aggregate:{bool_or:{arguments:use,predicate:{_eq:true}}}}")), [1]);
  const invalid = await query(state,
    "{source(where:{bundles_aggregate:{bool_and:{arguments:version,predicate:{_eq:true}}}}){id}}");
  assert(invalid.body.errors?.length);
});

test("Boolean aggregate argument enums match the reference schema", async () => {
  const result = await query(fixture(),
    '{__type(name:"bundle_aggregate_bool_exp_bool_and"){inputFields{name type{name kind ofType{name kind}}}}}');
  assert.equal(result.body.errors, undefined);
  const fields = result.body.data.__type.inputFields;
  assert.equal(fields.find(field => field.name === "arguments").type.ofType.name,
    "bundle_select_column_bundle_aggregate_bool_exp_bool_and_arguments_columns");
  assert.equal(fields.find(field => field.name === "predicate").type.ofType.name, "Boolean_comparison_exp");
  assert.deepEqual(fields.map(field => field.name).sort(), ["arguments","distinct","filter","predicate"]);
});

test("patches with no supported versions have no compatibility links or app-version matches", async () => {
  const initial = fixture();
  const original = JSON.parse(initial.bodies["patches/00000.json"])[0];
  const rows = [
    {...original, name:"Any version", packages:[{name:"com.video",versions:[]}]},
    {...original, id:original.bundle_id+":1",legacy_id:3,name:"No versions",
      compatiblePackages:{"com.video":[]},packages:[]},
    {...original, id:original.bundle_id+":2",legacy_id:4,name:"Restricted",
      packages:[{name:"com.video",versions:["1.0"]}]}
  ];
  const state = fixture({"patches/00000.json":rows, "package-records.json":[
    {id:1,name:"com.video",version:"1.0"}, {id:2,name:"com.video",version:null}
  ]});
  const rest = await call(state, "/patches?package=com.video&app_version=999.0");
  assert.deepEqual(rest.body.data.map(row => row.name), ["Any version"]);
  const graph = await query(state,
    "{patch(order_by:{id:asc}){name patch_packages{package{version}}}}");
  assert.equal(graph.body.errors, undefined, JSON.stringify(graph.body));
  assert.deepEqual(graph.body.data.patch, [
    {name:"Any version",patch_packages:[{package:{version:null}}]},
    {name:"No versions",patch_packages:[]},
    {name:"Restricted",patch_packages:[{package:{version:"1.0"}}]}
  ]);
});
