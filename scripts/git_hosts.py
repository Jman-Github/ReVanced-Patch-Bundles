"""Git-host routing for public and explicitly configured repository authorities.

Behavior follows ReVanced External Bundles HostResolver:
https://github.com/brosssh/revanced-external-bundles/blob/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles/integrations/HostResolver.kt
Independently implemented for the JSON catalog.
"""

import json
import os
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOSTS = {
    "github.com": "github",
    "gitlab.com": "gitlab",
    "codeberg.org": "gitea",
    "gitea.com": "gitea",
}


def hosts(root=ROOT):
    path = root / "config/git-hosts.json"
    configured = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    result = {**DEFAULT_HOSTS, **configured}
    if any(
        not isinstance(authority, str)
        or authority != authority.lower()
        or urlparse("https://" + authority).netloc != authority
        or "/" in authority
        or "@" in authority
        for authority in result
    ):
        raise ValueError("Git hosts must be lowercase authorities (host or host:port)")
    if any(kind not in {"github", "gitlab", "gitea"} for kind in result.values()):
        raise ValueError("Git host type must be github, gitlab, or gitea")
    return result


def normalize_source(value, root=ROOT):
    parsed = urlparse(value if "://" in value else "https://" + value)
    if parsed.scheme not in {"http", "https"} or parsed.username or parsed.password:
        raise ValueError("Expected a repository URL without credentials")
    authority = parsed.netloc.lower()
    path = unquote(parsed.path).strip("/")
    if authority == "api.github.com":
        authority, path = "github.com", path.removeprefix("repos/")
    kind = hosts(root).get(authority)
    if kind is None:
        raise ValueError(f"Unsupported git authority: {authority}")
    if kind == "gitlab":
        path = path.removeprefix("api/v4/projects/").split("/-/")[0]
    elif kind == "github":
        path = path.removeprefix("api/v3/repos/").removeprefix("repos/")
    else:
        path = path.removeprefix("api/v1/repos/")
    parts = path.removesuffix(".git").split("/")
    if len(parts) < 2 or any(not part or part in {".", ".."} for part in parts):
        raise ValueError("Expected a repository path")
    if kind != "gitlab":
        parts = parts[:2]
    scheme = parsed.scheme if authority != "github.com" else "https"
    return scheme + "://" + authority + "/" + "/".join(parts)


def endpoint(value, releases=True, root=ROOT):
    url = normalize_source(value, root)
    parsed = urlparse(url)
    kind = hosts(root)[parsed.netloc.lower()]
    path = parsed.path.strip("/")
    origin = parsed.scheme + "://" + parsed.netloc
    if kind == "github":
        base = "https://api.github.com" if parsed.netloc == "github.com" else origin + "/api/v3"
        api = base + "/repos/" + path
    elif kind == "gitlab":
        api = origin + "/api/v4/projects/" + quote(path, safe="")
    else:
        api = origin + "/api/v1/repos/" + path
    return api + ("/releases" if releases else "")


def auth_headers(value, root=ROOT):
    parsed = urlparse(normalize_source(value, root))
    kind = hosts(root)[parsed.netloc.lower()]
    tokens = json.loads(os.environ.get("GIT_HOST_TOKENS") or "{}")
    token = tokens.get(parsed.netloc.lower()) or (
        os.environ.get("GH_PAT")
        if parsed.netloc == "github.com"
        else os.environ.get("GITLAB_TOKEN")
        if parsed.netloc == "gitlab.com"
        else None
    )
    headers = {"Accept": "application/json"}
    if token:
        if kind == "gitlab":
            headers["PRIVATE-TOKEN"] = token
        else:
            headers["Authorization"] = "Bearer " + token
    return headers
