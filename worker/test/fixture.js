import { createHash } from "node:crypto";
const hash = value => createHash("sha256").update(value).digest("hex");
export function fixture(overrides = {}) {
  const source = { id: "s1", legacy_id: 1, url: "https://github.com/owner/repo", host: "github.com",
    namespace: "owner", repo: "repo", aliases: ["demo"], bundles: ["a".repeat(24), "b".repeat(24)],
    enabled: true, source_metadatum: { owner_name: "owner", repo_name: "repo", repo_stars: 12 } };
  const bundle = { id: "a".repeat(24), legacy_id: 1, source_id: "s1", version: "v1", bundle_type: "ReVanced:V4",
    description: "Video patches", download_url: "https://example.test/bundle.rvp",
    signature_download_url: "https://example.test/bundle.asc", file_hash: "c".repeat(64),
    channels: ["latest", "stable"], import_urls: { latest: "https://example.test/import.json" },
    is_latest: true, is_prerelease: false, ecosystem: "revanced",
    metadata_status: "verified", need_patches_update: false, patch_count: 1,
    patcher_runtime: "app.revanced:patcher:22.0.1", extraction_status: "verified",
    patch_metadata_version: "v1", packages: ["com.video"], created_at: "2026-01-01T00:00:00" };
  const dev = { ...bundle, id: "b".repeat(24), legacy_id: 2, version: "v2-dev", channels: ["dev"],
    is_latest: true, is_prerelease: true, metadata_status: "stale",
    need_patches_update: true, patch_count: 0 };
  const patch = { id: bundle.id + ":0", legacy_id: 1, bundle_id: bundle.id, source_id: "s1", name: "Hide ads",
    description: "Remove video advertisements", use: true, dependencies: [], options: [],
    metadata_status: "verified", patch_metadata_version: "v1",
    packages: [{ name: "com.video", versions: ["1.0", "2.0"] }] };
  const stale = { ...patch, id: dev.id + ":0", legacy_id: 2, bundle_id: dev.id,
    metadata_status: "stale", patch_metadata_version: "v1" };
  const index = { pages: ["patches/00000.json"],
    bundles: { [bundle.id]: ["patches/00000.json"], [dev.id]: ["patches/00000.json"] },
    packages: { "com.video": ["patches/00000.json"] } };
  const search = Array.from({ length: 16 }, () => ({}));
  const text = (patch.name + " " + patch.description).toLowerCase();
  for (let i = 0; i < text.length - 2; i++) search[text.codePointAt(i) % 16][text.slice(i, i + 3)] = index.pages;
  const files = { "sources.json": [source], "bundles.json": [bundle, dev],
    ["bundles/" + bundle.id + ".json"]: bundle, ["bundles/" + dev.id + ".json"]: dev,
    "patches/00000.json": [patch, stale], "patch-index.json": index,
    "packages.json": [{ name: "com.video", versions: ["1.0", "2.0"] }],
    "availability.json": { missing: [], retired_history: [] }, ...overrides };
  search.forEach((value, i) => { files["search/" + i + ".json"] = value; });
  const bodies = Object.fromEntries(Object.entries(files).map(([name, value]) => [name, JSON.stringify(value)]));
  const generation = "d".repeat(24);
  const manifest = { schema_version: 1, generation, snapshot: "snapshots/" + generation,
    counts: { sources: 1, bundles: 2, patches: 2 },
    files: Object.fromEntries(Object.entries(bodies).map(([name, body]) => [name, {
      bytes: Buffer.byteLength(body), sha256: hash(body)
    }])) };
  const requests = [];
  const fetcher = async input => {
    const url = new URL(input); requests.push(url.href);
    if (url.pathname.endsWith("/manifest.json")) return Response.json(manifest);
    const prefix = "/database/" + manifest.snapshot + "/";
    if (!url.pathname.startsWith(prefix)) return new Response("", { status: 404 });
    const body = bodies[url.pathname.slice(prefix.length)];
    return body == null ? new Response("", { status: 404 }) : new Response(body);
  };
  const env = { DATA_BASE_URL: "https://example.test/database/", FETCH: fetcher,
    CORS_ORIGINS: "https://website.test" };
  return { env, requests, bodies, manifest, bundle, dev };
}
