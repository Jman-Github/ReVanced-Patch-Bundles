import assert from "node:assert/strict";
import test from "node:test";
import worker from "../src/index.js";
import { fixture } from "./fixture.js";
import { Catalog } from "../../shared/catalog.js";
import { runGraphQL } from "../src/graphql.js";

async function graph(state, query, variables, options) {
  const catalog = await new Catalog(state.env.DATA_BASE_URL, state.env.FETCH).initialize();
  return JSON.parse(JSON.stringify(await runGraphQL(catalog, {query, variables}, options)));
}

test("latest imports use category winners from history instead of configured pointers", async () => {
  const base = fixture();
  const stable = {...base.bundle, is_latest:false};
  const dev = {...base.dev, channels:[]};
  const newest = {...base.bundle, id:"e".repeat(24), legacy_id:3, channels:[],
    version:"v3", created_at:"2026-02-01T00:00:00Z"};
  const state = fixture({"bundles.json":[stable, dev, newest],
    ["bundles/"+newest.id+".json"]:newest});
  const paths = [
    ["/api/v3/bundle?source_url=https://github.com/owner/repo&version=latest&channel=stable", "v3"],
    ["/api/v3/bundle?source_url=https://github.com/owner/repo&version=latest&channel=prerelease", "v2-dev"],
    ["/api/v3/bundle?source_url=https://github.com/owner/repo&version=latest&channel=any", "v3"],
    ["/api/v3/bundle?source_url=https://github.com/owner/repo&version=v1", "v1"],
    ["/api/v1/bundle/owner/repo/latest", "v3"],
    ["/api/v1/bundle/owner/repo/latest?prerelease=true", "v2-dev"],
    ["/api/v2/bundle/owner/repo/latest?channel=prerelease", "v2-dev"]
  ];
  for (const [path, version] of paths) {
    const response = await worker.fetch(new Request("https://api.test"+path), state.env);
    assert.equal(response.status, 200, path);
    assert.equal((await response.json()).version, version, path);
  }
});

test("v3 channels accept upstream whitespace and capitalization", async () => {
  for (const [channel, version] of [[" Stable ", "v1"], [" PrErElEaSe ", "v2-dev"], [" ANY ", "v1"]]) {
    const params = new URLSearchParams({source_url:"https://github.com/owner/repo",
      version:"latest", channel});
    const response = await worker.fetch(new Request("https://api.test/api/v3/bundle?"+params), fixture().env);
    assert.equal(response.status, 200);
    assert.equal((await response.json()).version, version);
  }
  for (const version of ["v1", "latest"]) {
    const response = await worker.fetch(new Request("https://api.test/api/v3/bundle?"+
      new URLSearchParams({source_url:"https://github.com/owner/repo", version, channel:" "})), fixture().env);
    assert.equal(response.status, version === "latest" ? 400 : 200);
  }
});

test("release and repository dates support String variables and pattern filters", async () => {
  const base = fixture(), source = JSON.parse(base.bodies["sources.json"])[0];
  const state = fixture({"sources.json":[{...source,
    source_metadatum:{...source.source_metadatum, repo_pushed_at:"2026-01-01T00:00:00Z"}}]});
  const result = await graph(state, `query($date:String!) {
    bundle(where:{created_at:{_eq:$date, _like:"2026%", _regex:"^2026-"}}){id}
    source_metadata(where:{repo_pushed_at:{_like:"2026%", _regex:"^2026-"}}){repo_pushed_at}
  }`, {date:base.bundle.created_at});
  assert.equal(result.errors, undefined, JSON.stringify(result));
  assert.deepEqual(result.data.bundle, [{id:1}, {id:2}]);
  assert.deepEqual(result.data.source_metadata, [{repo_pushed_at:"2026-01-01T00:00:00Z"}]);
});

test("provider date precision survives GraphQL and keeps legacy import formatting", async () => {
  for (const date of ["2026-01-01T00:00:00.123456Z", "2026-01-01T01:00:00.987+01:00"]) {
    const base = fixture(), bundle = {...base.bundle, created_at:date};
    const state = fixture({"bundles.json":[bundle], ["bundles/"+bundle.id+".json"]:bundle});
    const result = await graph(state, `query($date:String!) {
      bundle(where:{created_at:{_eq:$date}}){created_at}
    }`, {date});
    assert.equal(result.errors, undefined, JSON.stringify(result));
    assert.deepEqual(result.data.bundle, [{created_at:date}]);
    for (const path of [
      "/api/v1/bundle/1",
      "/api/v1/bundle/owner/repo/v1",
      "/api/v2/bundle/owner/repo/latest?channel=stable",
      "/api/v3/bundle?source_url=https://github.com/owner/repo&version=v1"
    ]) {
      const response = await worker.fetch(new Request("https://api.test"+path), state.env);
      assert.equal(response.status, 200, path);
      assert.equal((await response.json()).created_at, date.split("Z")[0], path);
    }
    const detail = await worker.fetch(new Request("https://api.test/bundles/"+bundle.id), state.env);
    assert.equal(detail.status, 200);
    assert.equal((await detail.json()).created_at, date);
  }
});

test("text dates use collation for ordering, relationships and extrema instead of instants", async () => {
  const base = fixture(), source = JSON.parse(base.bodies["sources.json"])[0];
  const a = "2026-01-01T00:30:00+02:00", b = "2025-12-31T23:00:00Z";
  const rows = [{...base.bundle, created_at:a}, {...base.dev, source_id:"s2", created_at:b}];
  const state = fixture({"sources.json":[source, {...source, id:"s2", legacy_id:2}],
    "bundles.json":rows});
  const result = await graph(state, `{
    bundle(order_by:{created_at:asc}){id}
    bundle_aggregate{aggregate{min{created_at} max{created_at}}}
    source(order_by:{bundles_aggregate:{min:{created_at:asc}}}){id}
    selected:bundle(where:{created_at:{_gt:"2026"}}){id}
    equivalent:bundle(where:{created_at:{_eq:"2025-12-31T22:30:00Z"}}){id}
  }`);
  assert.equal(result.errors, undefined, JSON.stringify(result));
  assert.deepEqual(result.data.bundle, [{id:2}, {id:1}]);
  assert.deepEqual(result.data.bundle_aggregate.aggregate, {min:{created_at:b}, max:{created_at:a}});
  assert.deepEqual(result.data.source, [{id:2}, {id:1}]);
  assert.deepEqual(result.data.selected, [{id:1}]);
  assert.deepEqual(result.data.equivalent, []);
});

test("date stream cursors distinguish text spellings of the same instant", async () => {
  const base = fixture(), a = "2026-01-01T00:00:00Z", b = "2026-01-01T01:00:00+01:00";
  const state = fixture({"bundles.json":[{...base.bundle, created_at:a}, {...base.dev, created_at:b}]});
  const query = `subscription {
    bundle_stream(batch_size:1,cursor:[{initial_value:{created_at:"2025"}}]){id}
  }`;
  const first = await graph(state, query, undefined, {subscription:true});
  assert.equal(first.errors, undefined, JSON.stringify(first));
  assert.deepEqual(first.data.bundle_stream, [{id:1}]);
  const second = await graph(state, query, undefined,
    {subscription:true, cursor:first.extensions.registryStream.cursor});
  assert.deepEqual(second.data.bundle_stream, [{id:2}]);
});

test("refresh-job timestamp filters and stream ties still compare instants", async () => {
  const jobs = [
    {id:1, job_id:"job1", started_at:"2026-01-01T00:00:00Z", status:"COMPLETED"},
    {id:2, job_id:"job2", started_at:"2026-01-01T01:00:00+01:00", status:"COMPLETED"}
  ];
  const state = fixture({"refresh-jobs.json":jobs});
  const filtered = await graph(state, `query($date:timestamptz!) {
    refresh_jobs(where:{started_at:{_eq:$date}}){id}
  }`, {date:"2026-01-01T00:00:00Z"});
  assert.equal(filtered.errors, undefined, JSON.stringify(filtered));
  assert.deepEqual(filtered.data.refresh_jobs, [{id:1}, {id:2}]);
  const streamed = await graph(state, `subscription {
    refresh_jobs_stream(batch_size:1,cursor:[{initial_value:{started_at:"2025-01-01T00:00:00Z"}}]){id}
  }`, undefined, {subscription:true});
  assert.deepEqual(streamed.data.refresh_jobs_stream, [{id:1}, {id:2}]);
});
