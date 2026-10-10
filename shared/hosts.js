// Independently implements the host routing described by upstream HostResolver.
// https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/integrations/HostResolver.kt
import configured from "../config/git-hosts.json" with { type: "json" };
export const gitHosts = Object.freeze({
  "github.com": "github", "gitlab.com": "gitlab",
  "codeberg.org": "gitea", "gitea.com": "gitea", ...configured
});
