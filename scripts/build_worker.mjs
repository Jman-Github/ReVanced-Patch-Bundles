import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

// Absolute paths keep Wrangler output stable across named environments and hosts.
const path = relative => fileURLToPath(new URL(relative, import.meta.url));
execFileSync(process.execPath, [
  path("../node_modules/wrangler/bin/wrangler.js"), "deploy", "--dry-run",
  "--config", path("../worker/wrangler.jsonc"), "--env", "production",
  "--outdir", path("../worker/dist/")
], { stdio: "inherit" });
