import assert from "node:assert/strict";
import test from "node:test";
import { RefreshStatus, refreshJob } from "../src/jobs.js";
import { CatalogSubscriptions } from "../src/subscriptions.js";

function memoryStorage(values = new Map()) {
  return { get:async key => structuredClone(values.get(key)),
    put:async (key,value) => values.set(key,structuredClone(value)),
    list:async () => new Map(), delete:async key => values.delete(key),
    transaction:async callback => callback(memoryStorage(values)) };
}
const running = refreshJob({id:12345678900,status:"in_progress"});
const completed = {...running,status:"COMPLETED"};
test("individual job lookups do not extend the freshness of a shared status",async()=>{
  const actualNow=Date.now;
  let now=actualNow(),requests=0;
  Date.now=()=>now;
  const values=new Map([["recent",{rows:[running],expires:now+100}]]);
  const object=new RefreshStatus({storage:memoryStorage(values)},{JOBS_FETCH:async()=>{
    requests++;
    return Response.json({id:12345678900,path:".github/workflows/catalog-updater.yml",
      status:"completed",conclusion:"success"});
  }});
  try {
    const request=new Request("https://internal/?id="+running.job_id);
    assert.equal((await (await object.fetch(request)).json())[0].status,"STARTED");
    now+=101;
    assert.equal((await (await object.fetch(request)).json())[0].status,"COMPLETED");
    assert.equal(requests,1);
  } finally {Date.now=actualNow;}
});
test("a refreshed job list supersedes an older cached individual status",async()=>{
  const now=Date.now();
  const values=new Map([["recent",{rows:[completed],expires:now+120000}],
    ["job:"+running.job_id,{rows:[running],expires:now+60000}]]);
  const object=new RefreshStatus({storage:memoryStorage(values)},{JOBS_FETCH:async()=>{
    throw new Error("Expected a cached response");
  }});
  const response=await object.fetch(new Request("https://internal/?id="+running.job_id));
  assert.equal((await response.json())[0].status,"COMPLETED");
});
test("subscription polling waits for an in-flight evaluation of the same operation",async()=>{
  const operation={payload:{query:"{source{id}}"},token:"same"};
  const values=new Map([["connection:client",{watch:operation}]]);
  const messages=[],state={id:"client",protocol:"graphql-transport-ws"};
  let release,fetches=0;
  const gate=new Promise(resolve=>{release=resolve;});
  const env={SUBSCRIPTIONS:{idFromName:name=>name,get:()=>({fetch:async()=>{
    fetches++;await gate;return Response.json({data:{source:[]}});
  }})}};
  const object=new CatalogSubscriptions({storage:memoryStorage(values)},env);
  const ws={send:message=>messages.push(JSON.parse(message))};
  const first=object.emit(ws,state,"watch",structuredClone(operation));
  const poll=object.emit(ws,state,"watch",structuredClone(operation));
  try {assert.equal(fetches,1);}
  finally {release();await Promise.all([first,poll]);}
  assert.equal(messages.length,1);
});
