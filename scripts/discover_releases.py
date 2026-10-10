import asyncio
import json
import os
import re
import secrets
import time
from collections.abc import Mapping
from datetime import UTC, datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

from httpx import AsyncClient, HTTPError, HTTPStatusError, Response, Timeout

try:
    from scripts.git_hosts import auth_headers, endpoint, hosts, normalize_source
    from scripts.release_assets import (
        artifact_signature,
        asset_extension,
        choose_patch_bundle,
        release_assets,
        release_date,
    )
    from scripts.release_history import release_is_prerelease
except ModuleNotFoundError:
    from git_hosts import auth_headers, endpoint, hosts, normalize_source
    from release_assets import (
        artifact_signature,
        asset_extension,
        choose_patch_bundle,
        release_assets,
        release_date,
    )
    from release_history import release_is_prerelease

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_ROOT / "internal/cache"
PATCH_BUNDLES_DIR = CACHE_DIR / "bundles"
BUNDLE_SOURCES_PATH = PROJECT_ROOT / "config/sources.json"
RELEASE_CACHE_FILE = CACHE_DIR / "release_cache.json"
METADATA_PATH = CACHE_DIR / "bundle-run-metadata.json"


def _load_release_cache() -> dict[str, Any]:
    try:
        data = json.loads(RELEASE_CACHE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {
        url: entry
        for url, entry in data.items()
        if isinstance(entry, dict)
        and isinstance(entry.get("etag"), str)
        and isinstance(entry.get("releases"), list)
        and all(isinstance(release, dict) for release in entry["releases"])
    }


METADATA_LOCK = asyncio.Lock()
RELEASE_CACHE = _load_release_cache()
RELEASE_REQUESTS: dict[str, asyncio.Task[list[dict[str, Any]]]] = {}
RELEASE_COOLDOWNS: dict[tuple[str, str], int] = {}


def _dump_json_sync(path: Path | str, payload: dict[str, Any]) -> None:
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    temp = path_obj.with_name(path_obj.name + ".tmp")
    temp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temp.replace(path_obj)


RepoConfig = Mapping[str, Any]

BUNDLE_METADATA: dict[str, Any] = {}
DISCOVERY_STATUS: dict[str, str] = {}

GH_PAT = os.getenv("GH_PAT")
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")

GITHUB_HEADERS: dict[str, str] = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "patch-bundle-registry/1.0 (+https://github.com/Jman-Github/Patch-Bundle-Registry)",
}
if GH_PAT:
    GITHUB_HEADERS["Authorization"] = f"Bearer {GH_PAT}"

GITLAB_HEADERS: dict[str, str] = {
    "Accept": "application/json",
    "User-Agent": "patch-bundle-registry/1.0 (+https://github.com/Jman-Github/Patch-Bundle-Registry)",
}
if GITLAB_TOKEN:
    GITLAB_HEADERS["PRIVATE-TOKEN"] = GITLAB_TOKEN

MAX_RETRIES = 5
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
SKIPPABLE_SOURCE_STATUS_CODES = {404, 410, 451}
HTTP_TIMEOUT = Timeout(connect=10.0, read=30.0, write=10.0, pool=30.0)
MAX_CONCURRENCY = int(os.getenv("GITHUB_API_CONCURRENCY", "6"))
HTTP_SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENCY)


async def _sleep_with_backoff(attempt: int, reset_at: int | None = None) -> None:
    if reset_at:
        delay = max(0, reset_at - int(time.time())) + 1
    else:
        delay = min(2**attempt, 30) + secrets.randbelow(1000) / 1000
    await asyncio.sleep(delay)


def _retry_after_at(value: str) -> int | None:
    value = value.strip()
    if value.isdigit():
        return int(time.time()) + int(value)
    try:
        date = parsedate_to_datetime(value)
        if date.tzinfo is None:
            date = date.replace(tzinfo=UTC)
        return int(date.timestamp())
    except (TypeError, ValueError, OverflowError):
        return None


def _retry_policy(response: Response, attempt: int) -> tuple[bool, int | None]:
    retry_after = _retry_after_at(response.headers.get("Retry-After", ""))
    quota_exhausted = response.headers.get("X-RateLimit-Remaining") == "0"
    rate_limited = response.status_code in {403, 429} and (
        quota_exhausted
        or retry_after is not None
        or response.status_code == 429
        or "secondary rate limit" in response.text.lower()
    )
    retryable = response.status_code in RETRYABLE_STATUS_CODES or rate_limited
    if not retryable:
        return False, None
    # Reset describes the primary quota, even during a secondary limit.
    reset_header = (
        response.headers.get("X-RateLimit-Reset") if rate_limited and quota_exhausted else None
    )
    reset_at = int(reset_header) if reset_header and reset_header.isdigit() else None
    if retry_after is not None:
        reset_at = max(reset_at or 0, retry_after)
    elif rate_limited and reset_at is None:
        reset_at = int(time.time()) + 60 * (2**attempt)
    return True, reset_at


async def _get_with_retries(client: AsyncClient, url: str, headers: dict[str, str]) -> Response:
    last_error: Exception | None = None
    origin = urlparse(url)
    authority = (origin.scheme.lower(), origin.netloc.lower())
    for attempt in range(MAX_RETRIES):
        try:
            while True:
                resume_at = RELEASE_COOLDOWNS.get(authority, 0)
                if resume_at > time.time():
                    await asyncio.sleep(resume_at - time.time() + 1)
                async with HTTP_SEMAPHORE:
                    # Recheck after queueing, but never hold a slot while cooling down.
                    if RELEASE_COOLDOWNS.get(authority, 0) > time.time():
                        continue
                    request_url = url
                    for redirects in range(11):
                        response = await client.get(
                            request_url, headers=headers, follow_redirects=False
                        )
                        if not response.is_redirect or "location" not in response.headers:
                            break
                        following = urljoin(request_url, response.headers["location"])
                        target = urlparse(following)
                        # PRIVATE-TOKEN is not stripped by clients on cross-host redirects.
                        if target.netloc != origin.netloc or target.scheme != origin.scheme:
                            raise ValueError("Release redirect changed authority")
                        if redirects == 10:
                            raise ValueError("Too many release redirects")
                        request_url = following
                    retryable, reset_at = _retry_policy(response, attempt)
                    # Publish before releasing the slot so queued repositories also pause.
                    if retryable and reset_at is not None:
                        RELEASE_COOLDOWNS[authority] = max(
                            RELEASE_COOLDOWNS.get(authority, 0), reset_at
                        )
                    break
        except HTTPError as exc:
            last_error = exc
            if attempt + 1 < MAX_RETRIES:
                await _sleep_with_backoff(attempt)
            continue

        if response.status_code == 304:
            return response
        if retryable:
            try:
                response.raise_for_status()
            except HTTPStatusError as exc:
                last_error = exc
            if attempt + 1 < MAX_RETRIES:
                await _sleep_with_backoff(attempt, reset_at)
            continue

        # Permanent errors cannot improve on retry.
        response.raise_for_status()
        return response

    if last_error:
        raise last_error
    raise RuntimeError(f"Unable to fetch URL after {MAX_RETRIES} attempts: {url}")


def _repository_from_release_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed._replace(
        path=parsed.path.removesuffix("/releases"), query="", fragment=""
    ).geturl()


def _headers_for_url(url: str) -> dict[str, str]:
    repository = _repository_from_release_url(url)
    headers = auth_headers(repository)
    headers["User-Agent"] = GITHUB_HEADERS["User-Agent"]
    if url.startswith("https://api.github.com/"):
        headers["Accept"] = GITHUB_HEADERS["Accept"]
    return headers


def _release_time(release: Mapping[str, Any]) -> str:
    # These are public text columns: preserve the provider's spelling and precision.
    return str(release_date(release) or "")


def _release_sort_time(release: Mapping[str, Any]) -> datetime:
    value = release_date(release)
    try:
        stamp = datetime.fromisoformat(str(value))
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)  # noqa: UP017
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=timezone.utc)  # noqa: UP017
    return stamp.astimezone(timezone.utc)  # noqa: UP017


def _release_is_prerelease(release: Mapping[str, Any]) -> bool:
    return release_is_prerelease(release)


def _release_url(release: Mapping[str, Any]) -> str | None:
    html_url = release.get("html_url")
    if isinstance(html_url, str):
        return html_url
    links = release.get("_links")
    if isinstance(links, Mapping):
        self_url = links.get("self")
        if isinstance(self_url, str):
            return self_url
    return None


async def _fetch_releases(client: AsyncClient, api_url: str) -> list[dict[str, Any]]:
    releases = []
    next_url = api_url
    visited = set()
    while next_url:
        if next_url in visited:
            raise ValueError("Cyclic release pagination")
        visited.add(next_url)
        if len(visited) > 1000:
            raise ValueError("Release pagination exceeds 1000 pages")
        headers = _headers_for_url(next_url)
        cached = RELEASE_CACHE.get(next_url)
        if cached and cached["etag"]:
            headers["If-None-Match"] = cached["etag"]
        from urllib.parse import urlparse

        request_url = next_url
        if not urlparse(next_url).query:
            from urllib.parse import urlencode

            kind = hosts().get(
                urlparse(normalize_source(_repository_from_release_url(next_url))).netloc
            )
            request_url += "?" + urlencode({"limit" if kind == "gitea" else "per_page": 100})
        response = await _get_with_retries(client, request_url, headers)
        if response.status_code == 304:
            if cached is None:
                raise ValueError(f"Received 304 without cached releases for {next_url}")
            page = cached["releases"]
            following = cached.get("next_url")
        else:
            page = response.json()
            if not isinstance(page, list) or any(not isinstance(r, dict) for r in page):
                raise ValueError(f"Release response is not a list of objects: {next_url}")
            following = response.links.get("next", {}).get("url")
            # GitLab can also paginate using X-Next-Page.
            if not following and response.headers.get("x-next-page"):
                from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

                parts = urlsplit(request_url)
                query = dict(parse_qsl(parts.query))
                query["page"] = response.headers["x-next-page"]
                following = urlunsplit(parts._replace(query=urlencode(query)))
            entry = {"etag": response.headers.get("ETag", ""), "releases": page}
            if following:
                entry["next_url"] = following
            RELEASE_CACHE[next_url] = entry
        if following:
            from urllib.parse import urlparse

            if (
                urlparse(following).netloc != urlparse(api_url).netloc
                or urlparse(following).scheme != urlparse(api_url).scheme
            ):
                raise ValueError("Release pagination changed authority")
        releases.extend(page)
        next_url = following
    return releases


async def get_latest_release(
    client: AsyncClient,
    repo_url: str,
    prerelease: bool,
    latest_flag: bool = False,
    *,
    required_extensions: tuple[str, ...] = (".jar", ".rvp", ".mpp"),
) -> tuple[
    str | None,
    str | None,
    str | None,
    dict[str, str | None] | None,
    str | None,
    str | None,
]:
    async def get_version_urls(
        release: Mapping[str, Any], file_types: tuple[str, ...]
    ) -> tuple[str, str, str, dict[str, str | None], str | None, str | None]:
        version = release["tag_name"]
        published_at = _release_time(release)
        description = release.get("body") or release.get("description") or ""
        download_urls: dict[str, str | None] = {ext: None for ext in file_types}
        release_url = _release_url(release)
        assets = release_assets(release)
        bundle = choose_patch_bundle(assets)
        for asset in assets:
            extension = asset_extension(asset)
            if extension in file_types and extension not in {".jar", ".rvp", ".mpp"}:
                download_urls[extension] = asset["url"]
        if bundle:
            download_urls[asset_extension(bundle)] = bundle["url"]
            download_urls["provider_digest"] = bundle.get("provider_digest")
        selected = bundle["url"] if bundle else None
        signature_url = artifact_signature(selected, assets) if selected else None
        return version, published_at, description, download_urls, signature_url, release_url

    api_url = endpoint(repo_url)
    # Creation happens before yielding, so all variants share successes and failures.
    if api_url not in RELEASE_REQUESTS:
        RELEASE_REQUESTS[api_url] = asyncio.create_task(_fetch_releases(client, api_url))
    releases = await RELEASE_REQUESTS[api_url]
    if not releases:
        print(f"No releases found for {repo_url}")
        return None, None, None, None, None, None
    releases = [
        release
        for release in releases
        if not release.get("draft") and not release.get("upcoming_release")
    ]
    if latest_flag:
        filtered_releases = sorted(releases, key=_release_sort_time, reverse=True)
    elif prerelease:
        filtered_releases = sorted(
            (r for r in releases if _release_is_prerelease(r)), key=_release_sort_time, reverse=True
        )
    else:
        filtered_releases = sorted(
            (r for r in releases if not _release_is_prerelease(r)),
            key=_release_sort_time,
            reverse=True,
        )
    file_types = (".jar", ".apk", ".rvp", ".mpp")
    for release in filtered_releases:
        (
            version,
            created_at,
            description,
            download_urls,
            signature_url,
            release_url,
        ) = await get_version_urls(release, file_types)
        if any(download_urls[ext] for ext in required_extensions):
            return version, created_at, description, download_urls, signature_url, release_url
    print(f"No suitable release with {required_extensions} assets found for {repo_url}")
    return None, None, None, None, None, None


async def fetch_release_data(
    client: AsyncClient, source: str, repo: Mapping[str, Any]
) -> bool | None:
    try:
        if repo.get("disabled", False) or source in DISABLED_ALIASES:
            return None
        prerelease = repo.get("prerelease", False)
        latest_flag = repo.get("latest", False)
        patches_repo = repo.get("patches")
        if not isinstance(patches_repo, str) or not patches_repo:
            print(f"Patch repository not defined for {source}; skipping.")
            return None
        (
            patches_version,
            patches_created_at,
            patches_description,
            patches_download_urls,
            patches_signature_url,
            patches_release_url,
        ) = await get_latest_release(client, patches_repo, prerelease, latest_flag)
        if not patches_download_urls:
            DISCOVERY_STATUS[source] = "no_matching_release"
            return None
        info_dict: dict[str, Any]
        cached_releases = await RELEASE_REQUESTS[endpoint(patches_repo)]
        selected_release: dict[str, Any] = next(
            (r for r in cached_releases if r.get("tag_name") == patches_version), {}
        )
        metadata_entry: dict[str, Any] = {
            "source": source,
            "base_source": re.sub(r"-(latest|stable|dev)$", "", source),
            "artifact_path": "",
            "type": "",
            "is_prerelease": _release_is_prerelease(selected_release),
            "patches": {
                "version": patches_version or "",
                "published_at": patches_created_at or "",
                "notes": patches_description or "",
                "release_url": patches_release_url or "",
                "download_url": "",
                "signature_url": patches_signature_url or "",
            },
        }
        if patches_download_urls[".mpp"]:
            info_dict = {
                "created_at": patches_created_at,
                "description": patches_description or "",
                "download_url": patches_download_urls[".mpp"],
                "bundle_type": "Morphe:V1",
                "signature_download_url": patches_signature_url if patches_signature_url else "N/A",
                "version": patches_version,
            }
            metadata_entry["type"] = "mpp"
            metadata_entry["patches"]["download_url"] = patches_download_urls[".mpp"]
        elif patches_download_urls[".rvp"]:
            info_dict = {
                "created_at": patches_created_at,
                "description": patches_description or "",
                "download_url": patches_download_urls[".rvp"],
                "bundle_type": "ReVanced:V4",
                "signature_download_url": patches_signature_url if patches_signature_url else "N/A",
                "version": patches_version,
            }
            metadata_entry["type"] = "rvp"
            metadata_entry["patches"]["download_url"] = patches_download_urls[".rvp"]
        else:
            jar_url = patches_download_urls[".jar"]
            if jar_url:
                integration_repo = repo.get("integration")
                # A legacy patch JAR is a complete catalog artifact. An optional
                # integrations APK enriches it without gating discovery.
                info_dict = {
                    "created_at": patches_created_at,
                    "description": patches_description or "",
                    "signature_download_url": patches_signature_url,
                    "patches": {"version": patches_version, "url": jar_url},
                    "bundle_type": "ReVanced:V3",
                }
                metadata_entry["type"] = "split"
                metadata_entry["patches"]["download_url"] = jar_url
                integrations_download_urls = None
                if isinstance(integration_repo, str) and integration_repo:
                    try:
                        (
                            integrations_version,
                            integrations_created_at,
                            integrations_description,
                            integrations_download_urls,
                            integrations_signature_url,
                            integrations_release_url,
                        ) = await get_latest_release(
                            client,
                            integration_repo,
                            prerelease,
                            latest_flag,
                            required_extensions=(".apk",),
                        )
                    except (HTTPError, ValueError) as exc:
                        print(f"Optional integrations unavailable for {source}: {exc}")
                if integrations_download_urls and integrations_download_urls[".apk"]:
                    apk_url = integrations_download_urls[".apk"]
                    info_dict["integrations"] = {"version": integrations_version, "url": apk_url}
                    metadata_entry["type"] = "split"
                    metadata_entry["patches"]["download_url"] = jar_url
                    metadata_entry["integrations"] = {
                        "version": integrations_version or "",
                        "published_at": integrations_created_at or "",
                        "notes": integrations_description or "",
                        "release_url": integrations_release_url or "",
                        "download_url": apk_url,
                        "signature_url": integrations_signature_url or "",
                    }
            else:
                print(f"No relevant .rvp, .mpp, or .jar assets found for {source}")
                DISCOVERY_STATUS[source] = "no_matching_release"
                return None
        base_source = re.sub(r"-(latest|stable|dev)$", "", source)
        directory = PATCH_BUNDLES_DIR / f"{base_source}-patch-bundles"
        directory.mkdir(parents=True, exist_ok=True)
        filepath = directory / f"{source}-patches-bundle.json"
        info_dict["is_prerelease"] = metadata_entry["is_prerelease"]
        info_dict["provider_digest"] = patches_download_urls.get("provider_digest")
        await asyncio.to_thread(_dump_json_sync, filepath, info_dict)
        relative_filepath = filepath.relative_to(PROJECT_ROOT)
        print(f"Latest release information saved to {relative_filepath}")
        DISCOVERY_STATUS[source] = "available"
        metadata_entry["artifact_path"] = str(relative_filepath)
        async with METADATA_LOCK:
            BUNDLE_METADATA[source] = metadata_entry
        return True
    except HTTPStatusError as exc:
        DISCOVERY_STATUS[source] = "upstream_unavailable"
        status_code = exc.response.status_code
        if status_code in SKIPPABLE_SOURCE_STATUS_CODES:
            print(
                f"Skipping {source}: release data unavailable "
                f"({status_code}) for {exc.request.url}"
            )
            return None
        print(f"Error in fetch_release_data for {source}: {exc}")
        return False
    except Exception as exc:
        DISCOVERY_STATUS[source] = "upstream_unavailable"
        print(f"Error in fetch_release_data for {source}: {exc}")
        return False


def _load_sources_sync() -> dict[str, Any]:
    with BUNDLE_SOURCES_PATH.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("config/sources.json does not contain object data")
    return data


DISABLED_ALIASES = set()


async def main() -> int:
    started_at = datetime.now(timezone.utc).isoformat()  # noqa: UP017
    RELEASE_REQUESTS.clear()
    BUNDLE_METADATA.clear()
    DISCOVERY_STATUS.clear()
    try:
        # Recovery must use a completed check from this discovery run, never
        # restored channel statuses after a discovery process crashes.
        checks_path = PROJECT_ROOT / "internal/cache/release-checks.json"
        await asyncio.to_thread(_dump_json_sync, checks_path, {})
        raw_sources = await asyncio.to_thread(_load_sources_sync)
        sources: dict[str, RepoConfig] = {
            str(name): value for name, value in raw_sources.items() if isinstance(value, Mapping)
        }
        try:
            from scripts.source_policy import disabled_sources
        except ModuleNotFoundError:
            from source_policy import disabled_sources
        try:
            from scripts.git_hosts import normalize_source
        except ModuleNotFoundError:
            from git_hosts import normalize_source
        disabled = disabled_sources(sources, PROJECT_ROOT)
        DISABLED_ALIASES.clear()
        DISABLED_ALIASES.update(
            name
            for name, settings in sources.items()
            if settings.get("patches")
            and normalize_source(settings["patches"], PROJECT_ROOT).lower() in disabled
        )
        async with AsyncClient(timeout=HTTP_TIMEOUT) as client:
            tasks = [fetch_release_data(client, source, repo) for source, repo in sources.items()]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        try:
            from scripts.release_history import save_history
        except ModuleNotFoundError:
            from release_history import save_history
        try:
            from scripts.source_policy import (
                PERMANENT_STATUS,
                save_availability,
                source_availability,
            )
        except ModuleNotFoundError:
            from source_policy import PERMANENT_STATUS, save_availability, source_availability
        availability = source_availability(PROJECT_ROOT)
        release_sets = {}
        for settings in sources.values():
            repo = settings.get("patches")
            if not repo:
                continue
            task = RELEASE_REQUESTS.get(endpoint(repo))
            if task and task.done() and not task.cancelled():
                error = task.exception()
                canonical = normalize_source(repo).lower()
                if error is None:
                    release_sets[canonical] = task.result()
                elif (
                    isinstance(error, HTTPStatusError)
                    and error.response.status_code in PERMANENT_STATUS
                ):
                    availability[canonical] = PERMANENT_STATUS[error.response.status_code]
        await asyncio.to_thread(save_availability, PROJECT_ROOT, availability)
        await asyncio.to_thread(
            _dump_json_sync, checks_path, {canonical: True for canonical in release_sets}
        )
        await asyncio.to_thread(save_history, PROJECT_ROOT, sources, release_sets)
        had_task_failure = False
        for (source, _), result in zip(sources.items(), results, strict=False):
            if isinstance(result, Exception):
                print(f"Task for {source} failed: {result}")
                had_task_failure = True
            elif result is False:
                had_task_failure = True
        timestamp = datetime.now(timezone.utc).isoformat()  # noqa: UP017
        metadata_payload = {
            "generated_at": timestamp,
            "started_at": started_at,
            "status": "FAILED" if had_task_failure else "COMPLETED",
            "error": (
                "One or more release sources could not be refreshed" if had_task_failure else None
            ),
            "bundles": BUNDLE_METADATA,
        }
        await asyncio.to_thread(_dump_json_sync, METADATA_PATH, metadata_payload)
        await asyncio.to_thread(_dump_json_sync, RELEASE_CACHE_FILE, RELEASE_CACHE)
        await asyncio.to_thread(
            _dump_json_sync, PATCH_BUNDLES_DIR / "discovery-status.json", DISCOVERY_STATUS
        )
        print(f"Checked {len(sources)} sources using {len(RELEASE_REQUESTS)} release requests.")
        return 1 if had_task_failure else 0
    except Exception as exc:
        print(f"Error in main: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
