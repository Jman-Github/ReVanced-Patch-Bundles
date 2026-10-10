import assert from "node:assert/strict";
import { fileURLToPath } from "node:url";
import { Miniflare, convertV4MiniflareOptions } from "miniflare";
import { fixture } from "../worker/test/fixture.js";

const state=fixture();
const origin=async request=>{
  const url=new URL(request.url);
  if(url.pathname.endsWith("/manifest.json"))return Response.json(state.manifest);
  const name=url.pathname.split(state.manifest.snapshot+"/")[1];
  return name && state.bodies[name] ? new Response(state.bodies[name]) : new Response("",{status:404});
};
const run={id:12345678900,path:".github/workflows/catalog-updater.yml",head_branch:"bundles",
  status:"in_progress",run_started_at:"2026-10-08T00:00:00Z"};
const mf=new Miniflare(convertV4MiniflareOptions({
  modules:true, scriptPath:fileURLToPath(new URL("../worker/dist/index.js",import.meta.url)),
  compatibilityDate:"2026-10-07",compatibilityFlags:["nodejs_compat"],
  bindings:{DATA_BASE_URL:"https://example.test/database/",CORS_ORIGINS:"https://website.test"},
  serviceBindings:{FETCH:origin,JOBS_FETCH:async request=>Response.json(
    new URL(request.url).pathname.includes("/actions/runs/") ? run : {workflow_runs:[run]})},
  durableObjects:{SUBSCRIPTIONS:{className:"CatalogSubscriptions",useSQLite:true},
    REFRESH_STATUS:{className:"RefreshStatus",useSQLite:true}}
}));
const sockets=[];
async function connect(protocol) {
  const response=await mf.dispatchFetch("https://api.test/graphql",{headers:{
    Upgrade:"websocket","Sec-WebSocket-Protocol":protocol,Origin:"https://website.test"}});
  assert.equal(response.status,101);
  const ws=response.webSocket; ws.accept(); sockets.push(ws);
  const queue=[],pending=[];
  ws.addEventListener("message",event=>{
    const value=JSON.parse(event.data);
    if(value.type==="ping") {
      if(ws.readyState===1)ws.send(JSON.stringify({type:"pong",payload:value.payload}));
      return;
    }
    if(value.type==="ka" || value.type==="pong")return;
    if(pending.length)pending.shift()(value);else queue.push(value);
  });
  const next=()=>queue.length?Promise.resolve(queue.shift()):new Promise((resolve,reject)=>{
    const timeout=setTimeout(()=>reject(new Error("WebSocket response timeout")),25000);
    pending.push(value=>{clearTimeout(timeout);resolve(value);});
  });
  return {ws,next};
}
try {
  assert.equal((await mf.dispatchFetch("https://api.test/graphql",{headers:{Upgrade:"websocket",
    "Sec-WebSocket-Protocol":"graphql-transport-ws",Origin:"https://blocked.test"}})).status,403);
  for(const protocol of ["graphql-transport-ws","graphql-ws"]) {
    const {ws,next}=await connect(protocol);
    ws.send(JSON.stringify({type:"connection_init"}));
    assert.equal((await next()).type,"connection_ack");
    ws.send(JSON.stringify({type:protocol==="graphql-ws"?"start":"subscribe",id:"watch",
      payload:{operationName:"Watch",query:"subscription Watch {...Rows} subscription Other {...Rows} fragment Rows on subscription_root {bundle(limit:1){id version}}"}}));
    const initial=await next(); assert.equal(initial.type,protocol==="graphql-ws"?"data":"next",JSON.stringify(initial));
    assert.equal(initial.payload.errors,undefined,JSON.stringify(initial));
    assert.equal(initial.payload.data.bundle[0].version,"v1");
    ws.send(JSON.stringify({type:protocol==="graphql-ws"?"start":"subscribe",id:"bad",
      payload:{query:"subscription { bundle(limit:101){id} }"}}));
    const limit=await next();
    assert.equal(limit.type,"error"); assert.match(limit.payload[0].message,/1.100/);
    // Change the snapshot, then wait for the alarm to deliver the changed result.
    const rows=JSON.parse(state.bodies["bundles.json"]);rows[0].version="v3";
    state.bodies["bundles.json"]=JSON.stringify(rows);
    const {createHash}=await import("node:crypto");
    state.manifest.files["bundles.json"]={bytes:Buffer.byteLength(state.bodies["bundles.json"]),
      sha256:createHash("sha256").update(state.bodies["bundles.json"]).digest("hex")};
    state.manifest.generation=(protocol==="graphql-ws"?"e":"f").repeat(24);
    state.manifest.snapshot="snapshots/"+state.manifest.generation;
    let update; do {update=await next();}while(["ping","ka"].includes(update.type));
    assert.equal(update.payload.data.bundle[0].version,"v3");
    ws.send(JSON.stringify({type:protocol==="graphql-ws"?"stop":"complete",id:"watch"}));
    ws.close(1000);
    // Restore the fixture for the second protocol.
    rows[0].version="v1";state.bodies["bundles.json"]=JSON.stringify(rows);
    state.manifest.generation="d".repeat(24);state.manifest.snapshot="snapshots/"+state.manifest.generation;
    state.manifest.files["bundles.json"]={bytes:Buffer.byteLength(state.bodies["bundles.json"]),
      sha256:createHash("sha256").update(state.bodies["bundles.json"]).digest("hex")};
  }
  for(const protocol of ["graphql-transport-ws","graphql-ws"]) {
    const {ws,next}=await connect(protocol);
    ws.send(JSON.stringify({type:"connection_init"}));
    assert.equal((await next()).type,"connection_ack");
    ws.send(JSON.stringify({type:protocol==="graphql-ws"?"start":"subscribe",id:"stream",
      payload:{query:"subscription {bundle_stream(batch_size:1,cursor:[{initial_value:{id:0}}]){version}}"}}));
    const first=await next();
    assert.equal(first.type,protocol==="graphql-ws"?"data":"next",JSON.stringify(first));
    assert.deepEqual(first.payload,{data:{bundle_stream:[{version:"v1"}]}});
    const second=await next();
    assert.deepEqual(second.payload,{data:{bundle_stream:[{version:"v2-dev"}]}});
    const original=state.bodies["bundles.json"],rows=JSON.parse(original);
    rows.push({...rows[0],id:"c".repeat(24),legacy_id:3,version:"v3"});
    state.bodies["bundles.json"]=JSON.stringify(rows);
    const {createHash}=await import("node:crypto");
    state.manifest.files["bundles.json"]={bytes:Buffer.byteLength(state.bodies["bundles.json"]),
      sha256:createHash("sha256").update(state.bodies["bundles.json"]).digest("hex")};
    state.manifest.generation=(protocol==="graphql-ws"?"1":"2").repeat(24);
    state.manifest.snapshot="snapshots/"+state.manifest.generation;
    const third=await next();
    assert.deepEqual(third.payload,{data:{bundle_stream:[{version:"v3"}]}});
    ws.send(JSON.stringify({type:protocol==="graphql-ws"?"stop":"complete",id:"stream"}));
    ws.close(1000);
    state.bodies["bundles.json"]=original;
    state.manifest.generation=(protocol==="graphql-ws"?"4":"3").repeat(24);
    state.manifest.snapshot="snapshots/"+state.manifest.generation;
    state.manifest.files["bundles.json"]={bytes:Buffer.byteLength(original),
      sha256:createHash("sha256").update(original).digest("hex")};
  }
  const plain=await mf.dispatchFetch("https://api.test/bundles?limit=1");
  assert.equal(plain.status,200);
  const response=await mf.dispatchFetch("https://api.test/refresh-jobs");
  assert.equal(response.status,200);assert.equal((await response.json()).data[0].status,"STARTED");
  const status=await mf.dispatchFetch("https://api.test/api/v1/refresh/status/"+run.id);
  assert.equal(status.status,202);assert.equal((await status.json()).jobId,String(run.id));
  const jobs=await mf.dispatchFetch("https://api.test/graphql",{method:"POST",
    headers:{"Content-Type":"application/json"},body:JSON.stringify({query:
      '{refresh_jobs(where:{status:{_eq:"STARTED"}}){job_id status}}'} )});
  const live=await jobs.json();assert.equal(live.errors,undefined,JSON.stringify(live));
  assert.equal(live.data.refresh_jobs[0].job_id,String(run.id));
  console.log("Live Worker checks passed: live queries and cursor streams on both protocols, changed snapshots, query limits, origins and active jobs.");
} finally {for(const ws of sockets)try{ws.close(1000);}catch{}await mf.dispose();}
