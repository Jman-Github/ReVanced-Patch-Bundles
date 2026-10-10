import { subscriptionPayload } from "./graphql.js";
import { executeCatalogQuery } from "./index.js";

const INTERVAL = 1000;
const bytes = value => new TextEncoder().encode(value).length;
async function fingerprint(text) {
  return [...new Uint8Array(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(text)))]
    .map(n => n.toString(16).padStart(2,"0")).join("");
}
export class CatalogSubscriptions {
  constructor(ctx,env) { this.ctx = ctx; this.env = env; this.evaluating = new Set(); }
  async fetch(request) {
    // This path is reachable only through the namespace binding, not the public
    // router. Give each evaluation its own invocation and subrequest budget.
    if (new URL(request.url).pathname === "/evaluate" && request.method === "POST") {
      try {
        const {payload,cursor} = await request.json();
        return Response.json(await executeCatalogQuery(this.env,this.ctx,payload,
          {subscription:true,cursor}));
      } catch(error) {
        return Response.json({error:error.message},{status:error.status ?? 503});
      }
    }
    if (request.headers.get("Upgrade")?.toLowerCase() !== "websocket")
      return new Response("Expected WebSocket upgrade",{status:426});
    const offered = (request.headers.get("Sec-WebSocket-Protocol") ?? "").split(",").map(s => s.trim());
    const protocol = offered.includes("graphql-transport-ws") ? "graphql-transport-ws" :
      offered.includes("graphql-ws") ? "graphql-ws" : null;
    if (!protocol) return new Response("Unsupported GraphQL WebSocket protocol",{status:400});
    if (this.ctx.getWebSockets().length >= 32) return new Response("Subscription capacity reached; retry",{status:503});
    const [client,server] = Object.values(new WebSocketPair());
    this.ctx.acceptWebSocket(server);
    server.serializeAttachment({id:crypto.randomUUID(),protocol,initialized:false,opened:Date.now()});
    await this.schedule();
    return new Response(null,{status:101,webSocket:client,headers:{"Sec-WebSocket-Protocol":protocol}});
  }
  async schedule() {
    if (await this.ctx.storage.getAlarm() === null) await this.ctx.storage.setAlarm(Date.now()+INTERVAL);
  }
  send(ws,type,id,payload) { ws.send(JSON.stringify({type,...(id === undefined ? {} : {id}),...(payload === undefined ? {} : {payload})})); }
  async webSocketMessage(ws,message) {
    const state = ws.deserializeAttachment();
    const key = "connection:" + state.id;
    try {
      if (typeof message !== "string" || bytes(message) > 32768) return ws.close(4400,"Message exceeds 32 KiB");
      const msg = JSON.parse(message);
      if (!msg || typeof msg !== "object" || typeof msg.type !== "string") return ws.close(4400,"Invalid message");
      if (msg.type === "connection_init") {
        if (state.initialized) return ws.close(4429,"Already initialized");
        state.initialized = true; ws.serializeAttachment(state);
        this.send(ws,"connection_ack"); return;
      }
      if (msg.type === "ping") { this.send(ws,"pong",undefined,msg.payload); return; }
      if (msg.type === "pong") return;
      if (msg.type === "connection_terminate" && state.protocol === "graphql-ws") return ws.close(1000,"Complete");
      if (!state.initialized) return ws.close(4401,"Initialize connection first");
      const operations = await this.ctx.storage.get(key) ?? Object.create(null);
      if (typeof msg.id !== "string" || !msg.id || msg.id.length > 128 || ["__proto__","constructor","prototype"].includes(msg.id)) return ws.close(4400,"Invalid operation ID");
      const modern = state.protocol === "graphql-transport-ws";
      if (msg.type === (modern ? "complete" : "stop")) {
        delete operations[msg.id]; await this.ctx.storage.put(key,operations); return;
      }
      if (msg.type !== (modern ? "subscribe" : "start")) return ws.close(4400,"Unexpected message type");
      if (Object.hasOwn(operations,msg.id)) return ws.close(4409,"Operation already exists");
      if (Object.keys(operations).length >= 4) {
        this.send(ws,"error",msg.id,[{message:"At most four operations per connection"}]); return;
      }
      let converted;
      try { converted = subscriptionPayload(msg.payload); }
      catch(error) { this.send(ws,"error",msg.id,[{message:error.message}]); return; }
      const operation = {payload:converted.payload,token:crypto.randomUUID(),live:converted.stream};
      operations[msg.id] = operation;
      await this.ctx.storage.put(key,operations);
      await this.emit(ws,state,msg.id,operation,converted.stream);
      await this.schedule();
    } catch { ws.close(4400,"Invalid subscription message"); }
  }
  async emit(ws,state,id,operation,stream = operation.live ?? true) {
    const key = "connection:" + state.id;
    const evaluation = JSON.stringify([state.id,id,operation.token]);
    // Alarm events can arrive while the initial query is awaiting I/O. Avoid
    // delivering out-of-order results or evaluating a one-shot query twice.
    if (this.evaluating.has(evaluation)) return;
    this.evaluating.add(evaluation);
    try {
      const evaluator = this.env.SUBSCRIPTIONS.get(this.env.SUBSCRIPTIONS.idFromName("query-" + state.id + "-" + id));
      const response = await evaluator.fetch("https://subscription.internal/evaluate",{
        method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({payload:operation.payload,cursor:operation.cursor})
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error ?? "Subscription evaluation failed");
      const cursorStream = result.extensions?.registryStream;
      if (cursorStream) delete result.extensions;
      const text = JSON.stringify(result);
      const digest = await fingerprint(text);
      const current = await this.ctx.storage.get(key) ?? {};
      if (current[id]?.token !== operation.token) return;
      if (result.errors || (cursorStream ? !cursorStream.empty : digest !== operation.digest)) {
        this.send(ws,state.protocol === "graphql-transport-ws" ? "next" : "data",id,result);
        operation.digest = digest;
      }
      if (cursorStream && !result.errors) operation.cursor = cursorStream.cursor;
      const operations = await this.ctx.storage.get(key) ?? Object.create(null);
      // A client can unsubscribe while a catalog fetch is in progress.
      if (operations[id]?.token !== operation.token) return;
      if (!stream || result.errors) {
        this.send(ws,"complete",id); delete operations[id];
      } else operations[id] = operation;
      await this.ctx.storage.put(key,operations);
    } catch(error) {
      const operations = await this.ctx.storage.get(key) ?? Object.create(null);
      if (operations[id]?.token !== operation.token) return;
      this.send(ws,"error",id,[{message:error.message}]);
      delete operations[id]; await this.ctx.storage.put(key,operations);
    } finally { this.evaluating.delete(evaluation); }
  }
  async alarm() {
    const sockets = this.ctx.getWebSockets();
    let active = false;
    for (const ws of sockets) {
      const state = ws.deserializeAttachment();
      try {
        if (!state.initialized && Date.now()-state.opened > 30000) { ws.close(4408,"Initialization timeout"); continue; }
        const operations = await this.ctx.storage.get("connection:" + state.id) ?? Object.create(null);
        if (!state.initialized || Object.keys(operations).length) active = true;
        for (const [id,operation] of Object.entries(operations)) await this.emit(ws,state,id,operation);
        if (state.initialized) this.send(ws,state.protocol === "graphql-transport-ws" ? "ping" : "ka");
      } catch {
        // A socket can close during an awaited fetch. Keep other clients running.
        await this.ctx.storage.delete("connection:" + state.id);
        try { ws.close(1011,"Connection failed"); } catch {}
      }
    }
    if (active && this.ctx.getWebSockets().length) await this.ctx.storage.setAlarm(Date.now()+INTERVAL);
  }
  async webSocketClose(ws,code) {
    const state = ws.deserializeAttachment();
    await this.ctx.storage.delete("connection:" + state.id);
    ws.close(code);
  }
  async webSocketError(ws) {
    await this.ctx.storage.delete("connection:" + ws.deserializeAttachment().id);
    ws.close(1011,"Connection failed");
  }
}
