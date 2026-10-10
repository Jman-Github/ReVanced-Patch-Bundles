import assert from "node:assert/strict";
import test from "node:test";
import worker from "../src/index.js";
import { fetchJobs, RefreshStatus } from "../src/jobs.js";
import { subscriptionPayload } from "../src/graphql.js";
import { CatalogSubscriptions } from "../src/subscriptions.js";
const run = {id:12345678900,path:".github/workflows/catalog-updater.yml",head_branch:"bundles",
  status:"in_progress",conclusion:null,run_started_at:"2026-10-08T00:00:00Z",html_url:"https://github.com/test/run",run_attempt:1};
const env = {JOBS_FETCH:async url => Response.json(url.includes("/actions/runs/") ? run : {workflow_runs:[run]})};
test("active jobs use safe GraphQL IDs, expose running/queued/failed states and restrict workflow", async () => {
  const rows = await fetchJobs(env);
  assert.equal(rows[0].status,"STARTED"); assert(rows[0].id < 2147483647); assert.equal(rows[0].job_id,String(run.id));
  const response = await worker.fetch(new Request("https://api.test/api/v1/refresh/status/"+run.id),env);
  assert.equal(response.status,202); assert.equal((await response.json()).status,"STARTED");
  for (const [status,conclusion,expected] of [["queued",null,"STARTED"],["completed","failure","FAILED"],["completed","cancelled","FAILED"],["completed","success","COMPLETED"]]) {
    const rows = await fetchJobs({JOBS_FETCH:async()=>Response.json({...run,status,conclusion})},String(run.id));
    assert.equal(rows[0].status,expected);
  }
  const main=await fetchJobs({JOBS_FETCH:async url=>{
    assert(!url.includes("branch="));return Response.json({workflow_runs:[{...run,head_branch:"main"}]});
  }});
  assert.equal(main[0].job_id,String(run.id));
  await assert.rejects(fetchJobs(env,"../other"),/Invalid refresh/);
  await assert.rejects(fetchJobs({JOBS_FETCH:async()=>Response.json({...run,path:"other.yml"})},String(run.id)),/not found/);
});
test("status cache shares reads and expires across requests",async()=>{
  const values=new Map(); let requests=0;
  const storage={get:async key=>values.get(key),put:async(key,val)=>values.set(key,val),
    list:async()=>new Map(),delete:async key=>values.delete(key)};
  storage.transaction=async callback=>callback(storage);
  const object=new RefreshStatus({storage},{JOBS_FETCH:async()=>{requests++;return Response.json({workflow_runs:[run]});}});
  await object.fetch(new Request("https://internal/"));
  await object.fetch(new Request("https://internal/"));
  assert.equal(requests,1);
  values.get("recent").expires=Date.now()-1;
  await object.fetch(new Request("https://internal/"));
  assert.equal(requests,2);
});
test("status requests coalesce, honor shared cooldowns and preserve polling quota",async()=>{
  const values=new Map();
  const storage={get:async key=>values.get(key),put:async(key,val)=>values.set(key,val),
    list:async()=>new Map(),delete:async key=>values.delete(key)};
  storage.transaction=async callback=>callback(storage);
  let requests=0,release;
  const response=new Promise(resolve=>{release=resolve;});
  const object=new RefreshStatus({storage},{JOBS_FETCH:async()=>{requests++;return response;}});
  const first=object.fetch(new Request("https://internal/"));
  const second=object.fetch(new Request("https://internal/"));
  release(Response.json({workflow_runs:[run]}));
  assert.equal((await first).status,200);assert.equal((await second).status,200);
  assert.equal(requests,1);
  const known=await object.fetch(new Request("https://internal/?id="+run.id));
  assert.equal(known.status,200);assert.equal(requests,1);
  values.clear();
  const cooling=new RefreshStatus({storage},{JOBS_FETCH:async()=>{
    requests++;return new Response("",{status:429,headers:{"Retry-After":"120"}});
  }});
  assert.equal((await cooling.fetch(new Request("https://internal/"))).status,503);
  assert(values.get("github-cooldown")>Date.now()+100000);
  assert.equal((await cooling.fetch(new Request("https://internal/?id=5"))).status,503);
  assert.equal(requests,2);
  values.clear();
  values.set("github-budget",{reset:Date.now()+3600000,count:25,individual:25});
  assert.equal((await cooling.fetch(new Request("https://internal/?id=6"))).status,503);
  assert.equal(requests,2);
  // Individual lookups cannot consume the quota reserved for the recent list.
  await object.reserve(false);
  assert.equal(values.get("github-budget").count,26);
});
test("subscription alarms isolate closed clients and stop polling inactive connections",async()=>{
  const messages=[],deleted=[];let alarms=0;
  const bad={deserializeAttachment:()=>({id:"bad",initialized:true}),send:()=>{throw new Error("Closed");},close:()=>{}};
  const good={deserializeAttachment:()=>({id:"good",initialized:true,protocol:"graphql-transport-ws"}),
    send:value=>messages.push(JSON.parse(value)),close:()=>{}};
  const ctx={getWebSockets:()=>[bad,good],storage:{get:async()=>({}),
    delete:async key=>deleted.push(key),setAlarm:async()=>{alarms++;}}};
  await new CatalogSubscriptions(ctx,{}).alarm();
  assert.deepEqual(deleted,["connection:bad"]);assert.equal(messages[0].type,"ping");
  assert.equal(alarms,0);
});
test("subscription validation supports single-root fragments and rejects mutations and multiple roots",()=>{
  const operation=subscriptionPayload({query:"subscription Watch($n:Int=1){ bundle(limit:$n){id version} }",operationName:"Watch"});
  assert.equal(operation.stream,true); assert.match(operation.payload.query,/subscription Watch/);
  assert.throws(()=>subscriptionPayload({query:"mutation { source {id} }"}),/read-only/);
  assert.throws(()=>subscriptionPayload({query:"subscription {source {id} bundle {id}}"}),/one top level/);
  const fragment=subscriptionPayload({query:"subscription {...Root} fragment Root on subscription_root {source {id}}"});
  assert.equal(fragment.stream,true);
});
