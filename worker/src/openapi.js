import site from "../../config/site.json" with { type: "json" };

const parameter = (name, description, schema = {type:"string"}, required = false, location = "query") =>
  ({ name, in: location, description, required, schema });
const responses = {
  200: { description: "Catalog result", content: {"application/json":{schema:{type:"object"}}} },
  400: { description: "Invalid query" }, 404: { description: "No matching cached record" },
  422: { description: "Query exceeds catalog budget; narrow the filter" },
  503: { description: "Catalog temporarily unavailable" }
};
const list = [parameter("limit","Rows per page",{type:"integer",minimum:1,maximum:100,default:25}),
  parameter("offset","Rows to skip",{type:"integer",minimum:0,maximum:10000,default:0}),
  parameter("q","Search text"), parameter("sort","Sort field"),
  parameter("order","Sort direction",{type:"string",enum:["asc","desc"]})];
const get = (summary, parameters = []) => ({get:{summary, parameters, responses}});
export const openapi = {
  openapi: "3.0.3",
  info: { title: "Patch Bundle Registry API", version: "3.0.0",
    description: "Public read-only patch catalog. Catalog records come from immutable snapshots; live refresh status comes from GitHub Actions. " +
      "Queries use limits of 100 rows, 2 MiB responses and bounded shard loading. " +
      "Numeric IDs belong to this catalog; IDs from other installations are not interchangeable." },
  servers: [{url:site.api}],
  paths: {
    "/refresh-jobs": get("Recent and active refresh jobs",list),
    "/api/v1/refresh/status/{jobId}": {get:{summary:"Refresh job status",parameters:[
      parameter("jobId","Phase UUID or GitHub Actions refresh run ID",undefined,true,"path")],
      responses:{...responses,202:{description:"Job pending or running"}}}},
    "/health": get("Catalog generation and counts"),
    "/api/v3/bundle": get("Import a current or historical bundle", [
      parameter("source_url","Repository URL on a supported Git host",undefined,true),
      parameter("version","Exact release tag or latest",undefined,true),
      parameter("channel","Required for latest",{type:"string",enum:["any","stable","prerelease"]})]),
    "/api/v1/bundle/{id}": get("Legacy numeric-ID import", [
      parameter("id","Stable catalog bundle ID",{type:"integer"},true,"path")]),
    "/api/v1/bundle/{owner}/{repo}/{version}": get("Legacy repository exact-version or latest import", [
      parameter("owner","Recorded repository owner or namespace",undefined,true,"path"),
      parameter("repo","Repository name",undefined,true,"path"),
      parameter("version","Release tag or latest",undefined,true,"path"),
      parameter("prerelease","Select prerelease for latest",{type:"boolean",default:false})]),
    "/api/v2/bundle/{owner}/{repo}/latest": get("Legacy repository channel import", [
      parameter("owner","Recorded repository owner or namespace",undefined,true,"path"),
      parameter("repo","Repository name",undefined,true,"path"),
      parameter("channel","Release channel",{type:"string",enum:["any","stable","prerelease"]},true)]),
    "/sources": get("Browse source repositories", [...list,parameter("source_url","Exact repository URL")]),
    "/sources/{id}": get("Source details",[parameter("id","Catalog source hash",undefined,true,"path")]),
    "/bundles": get("Browse releases", [...list,parameter("source","Source ID, alias or repository URL"),
      parameter("ecosystem","revanced or morphe"),parameter("version","Exact release tag"),
      parameter("channel","latest, stable or dev"),parameter("package","Compatible package name"),
      parameter("metadata_status","verified, stale, unverified or missing")]),
    "/releases": get("Browse releases (bundle alias)",list),
    "/bundles/{id}": get("Bundle details and release notes",[
      parameter("id","Catalog bundle hash",undefined,true,"path")]),
    "/bundles/{id}/patches": get("Browse patches in a bundle",[
      parameter("id","Catalog bundle hash",undefined,true,"path"),...list,
      parameter("include_unverified","Include fallback metadata",{type:"boolean"})]),
    "/patches": get("Browse indexed patches", [...list,parameter("source","Source ID or alias"),
      parameter("ecosystem","revanced or morphe"),parameter("channel","latest, stable or dev"),
      parameter("bundle_id","Catalog bundle hash"),parameter("package","Exact package name"),
      parameter("app_version","Compatible application version"),
      parameter("page_cursor","Continue loading candidate shards",{type:"integer",minimum:0}),
      parameter("include_unverified","Include fallback metadata",{type:"boolean",default:false})]),
    "/packages": get("Browse application packages and versions",list),
    "/availability": get("Missing channels and retired source records"),
    "/graphql": {
      get: { summary: "Query the public GraphQL schema", parameters:[
        parameter("query","GraphQL query",undefined,true),
        parameter("variables","JSON variables"),parameter("operationName","Named operation")],responses },
      post: { summary: "Query the public GraphQL schema", requestBody:{required:true,
        content:{"application/json":{schema:{type:"object",required:["query"],properties:{
          query:{type:"string"},variables:{type:"object"},operationName:{type:"string"}}}}}},responses }
    }
  }
};
for (const alias of ["/v1/graphql","/hasura/v1/graphql"])
  openapi.paths[alias] = openapi.paths["/graphql"];
for (const name of ["sources","bundles","releases","patches","packages","availability"])
  openapi.paths["/api/v1/" + name] = openapi.paths["/" + name];
