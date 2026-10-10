"""Refresh repository metadata daily within the existing updater; isolate upstream failures."""

import argparse
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urljoin, urlparse

import httpx
from generate_database import ROOT, encoded, normalize_source, read_json
from git_hosts import auth_headers, endpoint, hosts


def metadata_for(url, payload):
    namespace, repo = urlparse(url).path.strip("/").rsplit("/", 1)
    kind = hosts().get(urlparse(url).netloc, "github")
    if kind in {"github", "gitea"}:
        owner = payload.get("owner") or {}
        return {
            "owner_name": owner.get("login") or namespace,
            "repo_name": payload.get("name") or repo,
            "owner_avatar_url": owner.get("avatar_url"),
            "repo_description": payload.get("description"),
            "repo_stars": payload.get("stargazers_count", payload.get("stars_count")),
            "repo_pushed_at": payload.get("pushed_at"),
            "is_repo_archived": payload.get("archived"),
        }
    group = payload.get("namespace") or {}
    avatar = group.get("avatar_url")
    return {
        "owner_name": group.get("full_path") or namespace,
        "repo_name": payload.get("path") or repo,
        "owner_avatar_url": urljoin(url, avatar) if avatar else None,
        "repo_description": payload.get("description"),
        "repo_stars": payload.get("star_count"),
        "repo_pushed_at": payload.get("last_activity_at"),
        "is_repo_archived": payload.get("archived"),
    }


def fetch_metadata(client, api, headers):
    origin = urlparse(api)
    for _ in range(11):
        response = client.get(api, headers=headers, follow_redirects=False)
        if not response.is_redirect or "location" not in response.headers:
            return response
        following = urljoin(api, response.headers["location"])
        target = urlparse(following)
        # Keep Authorization and PRIVATE-TOKEN scoped to their original origin.
        if target.netloc != origin.netloc or target.scheme != origin.scheme:
            raise ValueError("Repository metadata redirect changed origin")
        api = following
    raise ValueError("Too many repository metadata redirects")


def refresh(root, client, limit=None, now=None):
    now = now or datetime.now(UTC)
    path = root / "database/repository-metadata.json"
    previous = read_json(path, {})
    inventory = read_json(root / "config/sources.json", {})
    urls = {
        normalize_source(item["patches"])
        for item in inventory.values()
        if isinstance(item, dict) and isinstance(item.get("patches"), str)
    }
    try:
        from scripts.source_policy import (
            PERMANENT_STATUS,
            disabled_sources,
            save_availability,
            source_availability,
        )
    except ModuleNotFoundError:
        from source_policy import (
            PERMANENT_STATUS,
            disabled_sources,
            save_availability,
            source_availability,
        )
    disabled = disabled_sources(inventory, root)
    availability = source_availability(root)
    checks = read_json(root / "internal/cache/release-checks.json", {})
    recovered = {url for url, completed in checks.items() if completed is True}
    result = {url.lower(): previous.get(url.lower(), {}) for url in sorted(urls)}
    attempted = 0
    for url in sorted(urls):
        cached = result[url.lower()]
        if url.lower() in disabled:
            continue
        try:
            checked = datetime.fromisoformat(cached.get("checked_at", ""))
            if url.lower() not in availability and now - checked < timedelta(days=1):
                continue
        except (ValueError, TypeError):
            pass
        if limit is not None and attempted >= limit:
            break
        attempted += 1
        api = endpoint(url, releases=False)
        headers = auth_headers(url)
        if cached.get("etag"):
            headers["If-None-Match"] = cached["etag"]
        updated = {**cached, "checked_at": now.isoformat()}
        try:
            response = fetch_metadata(client, api, headers)
            updated["http_status"] = response.status_code
            if response.status_code in PERMANENT_STATUS:
                availability[url.lower()] = PERMANENT_STATUS[response.status_code]
            if response.status_code == 200:
                payload = response.json()
                if not isinstance(payload, dict):
                    raise ValueError("Expected repository metadata")
                updated["source_metadatum"] = metadata_for(url, payload)
                updated["etag"] = response.headers.get("etag")
                if url.lower() in recovered:
                    availability.pop(url.lower(), None)
            elif response.status_code == 304:
                if url.lower() in recovered:
                    availability.pop(url.lower(), None)
            else:
                print(f"Repository metadata unavailable: {url} (HTTP {response.status_code})")
        except (httpx.HTTPError, ValueError, TypeError, AttributeError):
            updated["http_status"] = None
            print(f"Repository metadata unavailable: {url}")
        result[url.lower()] = updated
        if updated.get("http_status") in {401, 429} or (
            updated.get("http_status") == 403
            and (
                response.headers.get("x-ratelimit-remaining") == "0"
                or "retry-after" in response.headers
                or "secondary rate limit" in response.text.lower()
            )
        ):
            break
    save_availability(root, availability)
    if result != previous:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(encoded(result))
    print(f"Repository metadata: {attempted} refresh attempts, {len(result)} registered sources")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    with httpx.Client(timeout=20, follow_redirects=False) as client:
        refresh(Path(ROOT), client, args.limit)
