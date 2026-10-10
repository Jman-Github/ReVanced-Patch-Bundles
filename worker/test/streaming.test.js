import assert from "node:assert/strict";
import test from "node:test";
import { Catalog } from "../../shared/catalog.js";
import { createPostgresComparator } from "../../shared/postgres-collation.js";
import { runGraphQL, schema, subscriptionPayload } from "../src/graphql.js";
import { fixture } from "./fixture.js";
import { CatalogSubscriptions } from "../src/subscriptions.js";
import { executeCatalogQuery } from "../src/index.js";

async function evaluate(state, query, cursor, variables) {
  const catalog=await new Catalog(state.env.DATA_BASE_URL,state.env.FETCH).initialize();
  return JSON.parse(JSON.stringify(await runGraphQL(catalog,{query,variables},{subscription:true,cursor})));
}
test("streaming schema exposes cursor inputs only on subscriptions",()=>{
  const roots=schema.getSubscriptionType().getFields();
  for(const name of ["bundle","patch","source","source_metadata","package","patch_package","refresh_jobs"])
    assert(roots[name+"_stream"]);
  assert.equal(schema.getQueryType().getFields().bundle_stream,undefined);
  assert(subscriptionPayload({query:
    "subscription {bundle_stream(batch_size:1,cursor:[{initial_value:{id:0}}]){id}}"}).stream);
});
test("stream cursors advance without requiring cursor columns in the response",async()=>{
  const state=fixture(),query=`subscription Stream($n:Int!=1) {...Rows}
    fragment Rows on subscription_root {
      releases:bundle_stream(batch_size:$n,cursor:[{initial_value:{id:0}}]){version}
    }`;
  const first=await evaluate(state,query);
  assert.equal(first.errors,undefined,JSON.stringify(first));
  assert.deepEqual(first.data.releases,[{version:"v1"}]);
  const second=await evaluate(state,query,first.extensions.registryStream.cursor);
  assert.deepEqual(second.data.releases,[{version:"v2-dev"}]);
  const empty=await evaluate(state,query,second.extensions.registryStream.cursor);
  assert.deepEqual(empty.data.releases,[]);
  assert(empty.extensions.registryStream.empty);
});
test("descending cursors, relationships, filters and compound cursors work",async()=>{
  const state=fixture();
  const query=`subscription {bundle_stream(batch_size:1,
    cursor:[{initial_value:{id:3},ordering:DESC}],
    where:{source:{url:{_eq:"https://github.com/owner/repo"}}}
  ){id source{url} patches(limit:1){name}}}`;
  const first=await evaluate(state,query);
  assert.equal(first.errors,undefined,JSON.stringify(first));
  assert.equal(first.data.bundle_stream[0].id,2);
  const second=await evaluate(state,query,first.extensions.registryStream.cursor);
  assert.equal(second.data.bundle_stream[0].id,1);
  const compound=await evaluate(state,`subscription {
    patch_package_stream(batch_size:1,cursor:[{initial_value:{patch_fk:0,package_fk:0}}]){
      patch_fk package_fk package{name version}
    }
  }`);
  assert.equal(compound.errors,undefined,JSON.stringify(compound));
  assert.equal(compound.data.patch_package_stream.length,1);
});
test("non-unique cursor batches include ties instead of dropping records",async()=>{
  const state=fixture();
  const query=`subscription {bundle_stream(batch_size:1,
    cursor:[{initial_value:{created_at:"2025-01-01T00:00:00Z"}}]){id}}`;
  const first=await evaluate(state,query);
  assert.deepEqual(first.data.bundle_stream,[{id:1},{id:2}]);
  const next=await evaluate(state,query,first.extensions.registryStream.cursor);
  assert.deepEqual(next.data.bundle_stream,[]);
});
test("streams preserve list, depth and catalog budgets and reject empty cursors",async()=>{
  await assert.rejects(evaluate(fixture(),`subscription {
    bundle_stream(batch_size:101,cursor:[{initial_value:{id:0}}]){id}
  }`),/1.100/);
  const invalid=await evaluate(fixture(),`subscription {
    bundle_stream(batch_size:1,cursor:[{initial_value:{}}]){id}
  }`);
  assert.match(invalid.errors[0].message,/non-null initial/);
  const overflow=fixture({"bundles.json":Array.from({length:101},(_,i)=>({
    ...fixture().bundle,id:String(i),legacy_id:i+1
  }))});
  const ties=await evaluate(overflow,`subscription {bundle_stream(batch_size:1,
    cursor:[{initial_value:{created_at:"2025-01-01T00:00:00Z"}}]){id}}`);
  assert.match(ties.errors[0].message,/ties exceed 100/);
});
test("stream boundary ties count toward the existing query complexity budget",async()=>{
  const base=fixture();
  const state=fixture({"bundles.json":Array.from({length:3},(_,i)=>({
    ...base.bundle,id:String(i),legacy_id:i+1
  }))});
  const children="source{bundles(limit:100){source{bundles(limit:100){id}}}}";
  const tied=await evaluate(state,`subscription {bundle_stream(batch_size:1,
    cursor:[{initial_value:{created_at:"2025-01-01T00:00:00Z"}}]){${children}}}`);
  assert.match(tied.errors?.[0]?.message ?? "",/complexity exceeds 20000/);
  const unique=await evaluate(state,`subscription {bundle_stream(batch_size:1,
    cursor:[{initial_value:{id:0}}]){${children}}}`);
  assert.equal(unique.errors,undefined,JSON.stringify(unique));
  assert.equal(unique.data.bundle_stream.length,1);
});
test("a unique patch cursor reads bounded index pages instead of every shard",async()=>{
  const state=fixture();
  const index=JSON.parse(state.bodies["patch-index.json"]);
  index.patch_ids={"1":["patches/00000.json"],"2":["patches/00000.json"]};
  const indexed=fixture({"patch-index.json":index});
  const result=await evaluate(indexed,`subscription {
    patch_stream(batch_size:1,cursor:[{initial_value:{id:0}}]){id name}
  }`);
  assert.equal(result.errors,undefined,JSON.stringify(result));
  assert.deepEqual(result.data.patch_stream,[{id:1,name:"Hide ads"}]);
});
test("stream progress survives a new Durable Object instance and identical projected rows",async()=>{
  const values=new Map(),messages=[];
  const state={id:"client",protocol:"graphql-transport-ws"};
  const payload={query:`subscription {patch_stream(batch_size:1,
    cursor:[{initial_value:{id:0}}]){name}}`};
  const operation={payload,token:"token",live:true};
  values.set("connection:client",{watch:operation});
  const storage={get:async key=>structuredClone(values.get(key)),
    put:async (key,value)=>values.set(key,structuredClone(value))};
  const env=fixture().env;
  env.SUBSCRIPTIONS={idFromName:name=>name,get:()=>({fetch:async (url,init)=>{
    const {payload,cursor}=JSON.parse(init.body);
    return Response.json(await executeCatalogQuery(env,undefined,payload,{subscription:true,cursor}));
  }})};
  const ws={send:value=>messages.push(JSON.parse(value))};
  for(let i=0;i<3;i++) {
    const object=new CatalogSubscriptions({storage},env);
    await object.emit(ws,state,"watch",structuredClone(values.get("connection:client").watch));
  }
  assert.equal(messages.length,2);
  assert.deepEqual(messages.map(row=>row.payload.data.patch_stream),[
    [{name:"Hide ads"}],[{name:"Hide ads"}]
  ]);
  assert.deepEqual(values.get("connection:client").watch.cursor.patch_stream,[2]);
});
test("stream execution errors reach the client before completion on both protocols",async()=>{
  for(const protocol of ["graphql-transport-ws","graphql-ws"]) {
    const values=new Map(),messages=[];
    const state={id:"failed-stream",protocol};
    const operation={payload:{query:`subscription {
      patch_stream(batch_size:1,cursor:[{initial_value:{}}]){id}
    }`},token:"failed",live:true};
    values.set("connection:failed-stream",{watch:operation});
    const storage={get:async key=>structuredClone(values.get(key)),
      put:async (key,value)=>values.set(key,structuredClone(value))};
    const env=fixture().env;
    env.SUBSCRIPTIONS={idFromName:name=>name,get:()=>({fetch:async (url,init)=>{
      const {payload,cursor}=JSON.parse(init.body);
      return Response.json(await executeCatalogQuery(env,undefined,payload,{subscription:true,cursor}));
    }})};
    const object=new CatalogSubscriptions({storage},env);
    await object.emit({send:value=>messages.push(JSON.parse(value))},state,"watch",operation);
    assert.deepEqual(messages.map(message=>message.type),[
      protocol==="graphql-transport-ws" ? "next" : "data","complete"
    ]);
    assert.match(messages[0].payload.errors[0].message,/non-null initial/);
    assert.equal(values.get("connection:failed-stream").watch,undefined);
    assert.equal(operation.cursor,undefined);
  }
});
test("PostgreSQL text ranges, order and min/max share deterministic collation",async()=>{
  const original=fixture();
  const names=["a","AAAD Premium","Z"];
  const rows=names.map((name,i)=>({...JSON.parse(original.bodies["bundles.json"])[0],
    id:String(i),legacy_id:i+1,description:name,version:name}));
  const state=fixture({"bundles.json":rows});
  const result=await evaluate(state,`{
    ranged:bundle(where:{version:{_gt:"a",_lt:"b"}},order_by:{version:asc}){version}
    sorted:bundle(order_by:{version:asc}){version}
    bundle_aggregate{aggregate{min{version}max{version}}}
  }`);
  assert.equal(result.errors,undefined,JSON.stringify(result));
  assert.deepEqual(result.data.ranged,[{version:"AAAD Premium"}]);
  assert.deepEqual(result.data.sorted,names.map(version=>({version})));
  assert.deepEqual(result.data.bundle_aggregate.aggregate,{min:{version:"a"},max:{version:"Z"}});
  const compare=createPostgresComparator();
  assert(compare("\u00e9","z")<0);
  assert(compare("a","A")<0);
  assert(compare("a-b","ab")<0);
  assert(compare("l\u00b7","m")<0);
  assert(createPostgresComparator("C")("Z","a")<0);
  assert(createPostgresComparator("C.UTF-8")("\u{1f600}","\u{1f601}")<0);
});

test("native backward-run ordering applies to ranges, extrema and stream cursors",async()=>{
  const original=fixture();
  const rows=["0a","0_A","0_a"].map((version,i)=>({
    ...JSON.parse(original.bodies["bundles.json"])[0],id:String(i),legacy_id:i+1,version
  }));
  const state=fixture({"bundles.json":rows});
  const result=await evaluate(state,`{
    ranged:bundle(where:{version:{_gt:"0_A"}},order_by:{version:asc}){version}
    bundle_aggregate{aggregate{min{version}max{version}}}
  }`);
  assert.equal(result.errors,undefined,JSON.stringify(result));
  assert.deepEqual(result.data.ranged,[{version:"0a"}]);
  assert.deepEqual(result.data.bundle_aggregate.aggregate,{min:{version:"0_a"},max:{version:"0a"}});
  const streamed=await evaluate(state,`subscription {bundle_stream(batch_size:1,
    cursor:[{initial_value:{version:"0_A"}}]){version}}`);
  assert.equal(streamed.errors,undefined,JSON.stringify(streamed));
  assert.deepEqual(streamed.data.bundle_stream,[{version:"0a"}]);
});
