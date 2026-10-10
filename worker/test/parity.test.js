import assert from "node:assert/strict";
import test from "node:test";
import worker from "../src/index.js";
import { fixture } from "./fixture.js";
import { createPostgresMatcher } from "../src/postgres-regex.js";
import { catalogOrigins } from "../../shared/catalog.js";

test("disabled sources remain visible but their bundles, patches and relationships are hidden",async()=>{
  const initial=fixture();
  const source=JSON.parse(initial.bodies["sources.json"])[0];
  const {env}=fixture({"sources.json":[{...source,enabled:false,unavailable_reason:"Disabled"}]});
  const query='{source{enabled unavailable_reason bundles{id}} bundle{id} patch{id}}';
  const response=await worker.fetch(new Request("https://api.test/graphql",{
    method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query})}),env);
  const result=await response.json();
  assert.deepEqual(result,{data:{source:[{enabled:false,unavailable_reason:"Disabled",bundles:[]}],bundle:[],patch:[]}});
  for(const path of ["/api/v1/bundle/1","/api/v3/bundle?source_url=https://github.com/owner/repo&version=v1"])
    assert.equal((await worker.fetch(new Request("https://api.test"+path),env)).status,404);
  assert.deepEqual((await (await worker.fetch(new Request("https://api.test/patches"),env)).json()).data,[]);
});
test("phase status uses the upstream REST DTO and the public GraphQL job records",async()=>{
  const job={id:7,job_id:"12345678-1234-5678-9abc-123456789012",job_type:"PATCHES",status:"STARTED",
    started_at:"2026-10-09T00:00:00Z",completed_at:null,error:null};
  const {env}=fixture({"refresh-jobs.json":[job]});
  env.JOBS_FETCH=async()=>Response.json({workflow_runs:[]});
  const response=await worker.fetch(new Request("https://api.test/api/v1/refresh/status/"+job.job_id),env);
  assert.equal(response.status,202);
  assert.deepEqual(await response.json(),{jobId:job.job_id,type:"PATCHES",status:"STARTED",
    startedAt:job.started_at,completedAt:null,error:null});
  const jobs=await worker.fetch(new Request("https://api.test/refresh-jobs"),env);
  assert.equal((await jobs.json()).data[0].job_type,"PATCHES");
});
test("PostgreSQL locale profiles handle international classes, case conversion and boundaries",()=>{
  const utf8=createPostgresMatcher("en_US.UTF-8"),portable=createPostgresMatcher("C");
  assert(utf8("É","^é$","_iregex"));
  assert(utf8("Ελληνικά","^[[:alpha:]]+$","_regex"));
  assert(utf8("-é-","\\mé\\M","_regex"));
  assert(!portable("É","^é$","_iregex"));
  assert(!portable("é","[[:alpha:]]","_regex"));
  assert(!utf8("١","[[:digit:]]","_regex"));
  assert(utf8("あ","[[:upper:]]","_iregex"));
  assert(!utf8("K","^k$","_iregex"));
  assert(!utf8("İ","^[a-z]$","_iregex"));
  assert.throws(()=>createPostgresMatcher("missing_locale"),/Unsupported PostgreSQL locale/);
});
test("live checkpoints use the existing GitHub branch and retain the Pages fallback",()=>{
  assert.deepEqual(catalogOrigins({repository:"owner/registry",data_branch:"bundles",live_data:true},"https://site/database/"),
    ["https://raw.githubusercontent.com/owner/registry/bundles/database/","https://site/database/"]);
  assert.deepEqual(catalogOrigins({},"https://site/database/"),["https://site/database/"]);
});

test("cancelled Actions runs finish abandoned phase records across public endpoints",async()=>{
  const job={id:7,job_id:"12345678-1234-5678-9abc-123456789012",actions_run_id:"123",
    job_type:"PATCHES",status:"STARTED",started_at:"2026-10-09T00:00:00Z",completed_at:null,error:null};
  const {env}=fixture({"refresh-jobs.json":[job]});
  const run={id:123,path:".github/workflows/catalog-updater.yml",status:"completed",
    conclusion:"cancelled",updated_at:"2026-10-09T00:05:00Z"};
  env.JOBS_FETCH=async url=>Response.json(String(url).includes("/actions/runs/") ? run : {workflow_runs:[run]});
  const response=await worker.fetch(new Request("https://api.test/api/v1/refresh/status/"+job.job_id),env);
  assert.equal(response.status,200);
  const status=await response.json();
  assert.equal(status.status,"FAILED");
  assert.equal(status.completedAt,run.updated_at);
  const query='{refresh_jobs(where:{job_id:{_eq:"'+job.job_id+'"}}){status}}';
  const graph=await worker.fetch(new Request("https://api.test/graphql",{
    method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query})}),env);
  assert.deepEqual((await graph.json()).data.refresh_jobs,[{status:"FAILED"}]);
});

test("PostgreSQL case closure distinguishes literals from backreferences",()=>{
  const match=(value,pattern)=>createPostgresMatcher("en_US.utf8")(value,pattern,"_iregex");
  assert(!match("ǅ","^ǅ$"));
  assert(match("Ǆ","^ǅ$"));
  assert(match("ǆ","^ǅ$"));
  assert(match("KK","^(.)\\1$"));
  assert(!match("K","^k$"));
  assert(match("k","^K$"));
});

test("previously published discovery job IDs remain usable with the status endpoint",async()=>{
  const job={id:7,job_id:"a".repeat(24),job_type:"BUNDLES",status:"COMPLETED",
    started_at:"2026-10-09T00:00:00Z",completed_at:"2026-10-09T00:05:00Z",error:null};
  const {env}=fixture({"refresh-jobs.json":[job]});
  const response=await worker.fetch(new Request("https://api.test/api/v1/refresh/status/"+job.job_id),env);
  assert.equal(response.status,200);
  assert.equal((await response.json()).jobId,job.job_id);
});

test("a cached completed attempt does not fail phases from a newer attempt",async()=>{
  const {mergeJobs}=await import("../src/jobs.js");
  const phase={job_id:"phase",actions_run_id:"123",actions_run_attempt:2,status:"STARTED"};
  const old={job_id:"123",run_attempt:1,status:"COMPLETED"};
  assert.equal(mergeJobs([phase],[old])[0].status,"STARTED");
  assert.equal(mergeJobs([{...phase,actions_run_attempt:1}],
    [{...old,run_attempt:2,status:"STARTED",started_at:"2026-10-09T00:00:00Z"}])[0].status,"FAILED");
});

test("a cached branch manifest reads its snapshot from the containing commit",async()=>{
  const {Catalog}=await import("../../shared/catalog.js");
  const state=fixture();
  state.manifest.snapshot_ref="c".repeat(40);
  const base="https://raw.githubusercontent.com/owner/registry/bundles/database/";
  const requests=[];
  const fetcher=async input=>{
    const url=new URL(input); requests.push(url.href);
    if(url.href===base+"manifest.json") return Response.json(state.manifest);
    const prefix="/owner/registry/"+state.manifest.snapshot_ref+"/database/"+state.manifest.snapshot+"/";
    if(!url.pathname.startsWith(prefix)) return new Response("",{status:404});
    const body=state.bodies[url.pathname.slice(prefix.length)];
    return body===undefined ? new Response("",{status:404}) : new Response(body);
  };
  const catalog=await new Catalog(base,fetcher).initialize();
  assert.equal((await catalog.bundles())[0].version,"v1");
  assert.equal((await catalog.patchRows({bundle_id:state.bundle.id})).rows[0].name,"Hide ads");
  assert(requests.slice(1).every(url=>url.includes("/"+state.manifest.snapshot_ref+"/database/")));
  // A Pages copy continues serving its own files, without redirecting to GitHub.
  assert.equal((await new Catalog(state.env.DATA_BASE_URL,state.env.FETCH).initialize()
    .then(c=>c.bundles()))[0].version,"v1");
});
test("snapshot references cannot redirect catalog reads to another location",async()=>{
  const {Catalog}=await import("../../shared/catalog.js");
  const state=fixture();
  state.manifest.snapshot_ref="../../other";
  await assert.rejects(new Catalog(state.env.DATA_BASE_URL,state.env.FETCH).initialize(),
    /Invalid catalog snapshot reference/);
});

test("ILIKE follows the query locale for Turkish I and Greek sigma",async()=>{
  async function lookup(description,pattern,locale) {
    const original=fixture();
    const bundles=JSON.parse(original.bodies["bundles.json"]).map(b=>({...b,description}));
    const {env}=fixture({"bundles.json":bundles});
    env.POSTGRES_LOCALE=locale;
    const query='query($pattern:String!){bundle(where:{description:{_ilike:$pattern}}){id}}';
    const response=await worker.fetch(new Request("https://api.test/graphql",{
      method:"POST",headers:{"Content-Type":"application/json"},
      body:JSON.stringify({query,variables:{pattern}})}),env);
    const result=await response.json();
    assert.equal(result.errors,undefined,JSON.stringify(result));
    return result.data.bundle.length;
  }
  assert.deepEqual(await Promise.all([
    lookup("İ","i","en_US.utf8"), lookup("ΟΣ","%σ","en_US.utf8"),
    lookup("İ","i","C"), lookup("É","é","C")
  ]),[2,2,0,0]);
});

test("nested GraphQL negation preserves SQL NULL semantics",async()=>{
  const original=fixture();
  const bundles=JSON.parse(original.bodies["bundles.json"]);
  bundles[1].patcher_failure_fingerprint="broken";
  const {env}=fixture({"bundles.json":bundles});
  const query=`{
    notEqual:bundle(where:{_not:{patcher_failure_fingerprint:{_eq:"other"}}}){id}
    notAnd:bundle(where:{_not:{_and:[
      {patcher_failure_fingerprint:{_eq:"other"}},{id:{_eq:2}}
    ]}}){id}
    notOr:bundle(where:{_not:{_or:[
      {patcher_failure_fingerprint:{_eq:"other"}},{id:{_eq:2}}
    ]}}){id}
    doubleNot:bundle(where:{_not:{_not:{patcher_failure_fingerprint:{_eq:"broken"}}}}){id}
    notLike:bundle(where:{_not:{patcher_failure_fingerprint:{_like:"other"}}}){id}
    known:bundle(where:{patcher_failure_fingerprint:{_is_null:false}}){id}
    notIn:bundle(where:{patcher_failure_fingerprint:{_nin:["other"]}}){id}
    emptyNotIn:bundle(where:{patcher_failure_fingerprint:{_nin:[]}}){id}
    noRelatedPatch:bundle(where:{_not:{patches:{description:{_eq:"missing"}}}}){id}
    noRelatedMetadata:bundle(where:{_not:{source:{source_metadatum:{
      repo_description:{_eq:"missing"}
    }}}}){id}
    count:bundle_aggregate(where:{_not:{patcher_failure_fingerprint:{_eq:"other"}}}){
      aggregate{count}
    }
  }`;
  const response=await worker.fetch(new Request("https://api.test/graphql",{
    method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query})}),env);
  const result=await response.json();
  assert.equal(result.errors,undefined,JSON.stringify(result));
  assert.deepEqual(result.data,{
    notEqual:[{id:2}],notAnd:[{id:1},{id:2}],notOr:[],doubleNot:[{id:2}],
    notLike:[{id:2}],known:[{id:2}],notIn:[{id:2}],emptyNotIn:[{id:1},{id:2}],
    noRelatedPatch:[{id:1},{id:2}],noRelatedMetadata:[{id:1},{id:2}],
    count:{aggregate:{count:1}}
  });
});


test("legacy active phase records normalize to STARTED for status and GraphQL",async()=>{
  for (const status of ["PENDING","RUNNING"]) {
    const job={id:7,job_id:"12345678-1234-5678-9abc-123456789012",job_type:"PATCHES",status,
      started_at:"2026-10-09T00:00:00Z",completed_at:null,error:null};
    const {env}=fixture({"refresh-jobs.json":[job]});
    env.JOBS_FETCH=async()=>Response.json({workflow_runs:[]});
    const response=await worker.fetch(new Request("https://api.test/api/v1/refresh/status/"+job.job_id),env);
    assert.equal(response.status,202);
    assert.equal((await response.json()).status,"STARTED");
    const query='{refresh_jobs(where:{status:{_eq:"STARTED"}}){job_id status}}';
    const graph=await worker.fetch(new Request("https://api.test/graphql",{
      method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query})}),env);
    assert.deepEqual((await graph.json()).data.refresh_jobs,[{job_id:job.job_id,status:"STARTED"}]);
  }
});
test("old phase UUIDs resolve beyond the first hundred recorded jobs",async()=>{
  const jobs=Array.from({length:130},(_,i)=>({
    id:i+1,job_id:"12345678-1234-5678-9abc-"+String(i).padStart(12,"0"),job_type:"PATCHES",
    status:"COMPLETED",started_at:"2026-01-01T00:00:00Z",completed_at:"2026-01-01T00:01:00Z",error:null
  }));
  const {env}=fixture({"refresh-jobs.json":jobs});
  const response=await worker.fetch(new Request("https://api.test/api/v1/refresh/status/"+jobs[0].job_id),env);
  assert.equal(response.status,200);
  assert.equal((await response.json()).jobId,jobs[0].job_id);
  const query='{refresh_jobs(where:{job_id:{_eq:"'+jobs[0].job_id+'"}}){id}}';
  const graph=await worker.fetch(new Request("https://api.test/graphql",{
    method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query})}),env);
  assert.deepEqual((await graph.json()).data.refresh_jobs,[{id:1}]);
});
test("automatic upstream unavailability keeps published imports accessible",async()=>{
  const initial=fixture(), source=JSON.parse(initial.bodies["sources.json"])[0];
  const {env}=fixture({"sources.json":[{...source,enabled:true,unavailable_reason:"404: Not Found"}]});
  const response=await worker.fetch(new Request("https://api.test/api/v3/bundle?source_url=https://github.com/owner/repo&version=v1"),env);
  assert.equal(response.status,200);
});


test("published job history stays queryable when live Actions status fails",async()=>{
  const job={id:7,job_id:"12345678-1234-5678-9abc-123456789012",job_type:"PATCHES",status:"COMPLETED",
    started_at:"2026-01-01T00:00:00Z",completed_at:"2026-01-01T00:05:00Z",error:null};
  for (const failure of [async()=>new Response("",{status:503}),async()=>{throw new TypeError("Network unavailable");}]) {
    const {env}=fixture({"refresh-jobs.json":[job]}); env.JOBS_FETCH=failure;
    const response=await worker.fetch(new Request("https://api.test/refresh-jobs"),env);
    assert.equal(response.status,200);
    assert.deepEqual((await response.json()).data,[job]);
    const query='{refresh_jobs(where:{job_id:{_eq:"'+job.job_id+'"}}){job_id status}}';
    const graph=await worker.fetch(new Request("https://api.test/graphql",{
      method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({query})}),env);
    assert.deepEqual(await graph.json(),{data:{refresh_jobs:[{job_id:job.job_id,status:"COMPLETED"}]}});
    const live=await worker.fetch(new Request("https://api.test/api/v1/refresh/status/123"),env);
    assert.equal(live.status,503);
  }
});
test("live job failures remain visible when there is no published history",async()=>{
  const {env}=fixture({"refresh-jobs.json":[]});
  env.JOBS_FETCH=async()=>new Response("",{status:503});
  const response=await worker.fetch(new Request("https://api.test/refresh-jobs"),env);
  assert.equal(response.status,503);
  const graph=await worker.fetch(new Request("https://api.test/graphql",{
    method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({query:"{refresh_jobs{job_id}}"})}),env);
  assert.match((await graph.json()).errors[0].message,/temporarily unavailable/);
});
