import asyncio
import json
import os
import re
import secrets
import time
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from httpx import AsyncClient, HTTPError, HTTPStatusError, Response, Timeout

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PATCH_BUNDLES_DIR = PROJECT_ROOT / "patch-bundles"
BUNDLE_SOURCES_PATH = PATCH_BUNDLES_DIR / "bundle-sources.json"
ETAG_CACHE_FILE = PROJECT_ROOT / "etag_cache.json"
METADATA_PATH = PROJECT_ROOT / "bundle-run-metadata.json"


def _load_etag_cache() -> dict[str, str]:
    if ETAG_CACHE_FILE.exists():
        try:
            with ETAG_CACHE_FILE.open(encoding="utf-8") as cache_file:
                data = json.load(cache_file)
                if isinstance(data, dict):
                    return {str(key): str(value) for key, value in data.items()}
                return {}
        except Exception:
            return {}
    return {}

ETAG_CACHE_LOCK = asyncio.Lock()
METADATA_LOCK = asyncio.Lock()
RELEASE_CACHE_LOCK = asyncio.Lock()
RELEASE_CACHE: dict[str, list[dict[str, Any]]] = {}

def _write_etag_cache_sync(cache: Mapping[str, str]) -> None:
    with ETAG_CACHE_FILE.open("w", encoding="utf-8") as cache_file:
        json.dump(cache, cache_file, indent=2)

async def _save_etag_cache(cache: Mapping[str, str]) -> None:
    async with ETAG_CACHE_LOCK:
        await asyncio.to_thread(_write_etag_cache_sync, cache)

def _dump_json_sync(path: Path | str, payload: dict[str, Any]) -> None:
    path_obj = Path(path)
    with path_obj.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

RepoConfig = Mapping[str, Any]
ETAG_CACHE = _load_etag_cache()

BUNDLE_METADATA: dict[str, Any] = {}

GH_PAT = os.getenv('GH_PAT')
GITLAB_TOKEN = os.getenv('GITLAB_TOKEN')

GITHUB_HEADERS: dict[str, str] = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "revanced-patch-bundles/1.0 (+https://github.com/Jman-Github/ReVanced-Patch-Bundles)",
}
if GH_PAT:
    GITHUB_HEADERS["Authorization"] = f"Bearer {GH_PAT}"

GITLAB_HEADERS: dict[str, str] = {
    "Accept": "application/json",
    "User-Agent": "revanced-patch-bundles/1.0 (+https://github.com/Jman-Github/ReVanced-Patch-Bundles)",
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
        delay = min(2 ** attempt, 30) + secrets.randbelow(1000) / 1000
    await asyncio.sleep(delay)

async def _get_with_retries(client: AsyncClient, url: str, headers: dict[str, str]) -> Response:
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            async with HTTP_SEMAPHORE:
                response = await client.get(url, headers=headers, follow_redirects=True)
        except HTTPError as exc:
            last_error = exc
            await _sleep_with_backoff(attempt)
            continue

        if response.status_code == 304:
            return response

        if response.status_code in RETRYABLE_STATUS_CODES:
            await _sleep_with_backoff(attempt)
            continue

        if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
            reset_header = response.headers.get("X-RateLimit-Reset")
            reset_at = int(reset_header) if reset_header and reset_header.isdigit() else None
            await _sleep_with_backoff(attempt, reset_at)
            continue

        try:
            response.raise_for_status()
        except HTTPError as exc:
            last_error = exc
            await _sleep_with_backoff(attempt)
            continue

        return response

    if last_error:
        raise last_error
    raise RuntimeError(f"Unable to fetch URL after {MAX_RETRIES} attempts: {url}")

def _headers_for_url(url: str) -> dict[str, str]:
    if "gitlab.com/api/v4/" in url:
        return dict(GITLAB_HEADERS)
    return dict(GITHUB_HEADERS)

def _release_time(release: Mapping[str, Any]) -> str:
    value = (
        release.get("published_at")
        or release.get("released_at")
        or release.get("created_at")
        or ""
    )
    value = str(value)
    value = re.sub(r"\.\d+(?=Z$)", "", value)
    return re.sub(r"[A-Za-z]+$", "", value)

def _release_is_prerelease(release: Mapping[str, Any]) -> bool:
    if "prerelease" in release:
        return bool(release["prerelease"])
    label = f"{release.get('tag_name', '')} {release.get('name', '')}".lower()
    return bool(re.search(r"(^|[-._])(dev|alpha|beta|rc|pre)([-._\d]|$)", label))

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

def _asset_download_urls(release: Mapping[str, Any]) -> list[str]:
    assets = release.get("assets")
    urls: list[str] = []
    if isinstance(assets, list):
        for asset in assets:
            if isinstance(asset, Mapping) and isinstance(asset.get("browser_download_url"), str):
                urls.append(asset["browser_download_url"])
    elif isinstance(assets, Mapping):
        links = assets.get("links")
        if isinstance(links, list):
            for link in links:
                if not isinstance(link, Mapping):
                    continue
                direct_url = link.get("direct_asset_url")
                fallback_url = link.get("url")
                if isinstance(direct_url, str):
                    urls.append(direct_url)
                elif isinstance(fallback_url, str):
                    urls.append(fallback_url)
    return urls

async def get_latest_release(
    client: AsyncClient,
    repo_url: str,
    prerelease: bool,
    latest_flag: bool = False,
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
        version = release['tag_name']
        published_at = _release_time(release)
        description = release.get('body') or release.get('description') or ''
        download_urls: dict[str, str | None] = {ext: None for ext in file_types}
        signature_url = None
        release_url = _release_url(release)
        for asset_url in _asset_download_urls(release):
            for ext in file_types:
                if asset_url.endswith(ext):
                    download_urls[ext] = asset_url
            if asset_url.endswith(".rvp.asc") or asset_url.endswith(".mpp.asc"):
                signature_url = asset_url
        return version, published_at, description, download_urls, signature_url, release_url

    api_url = f"{repo_url}/releases"
    async with RELEASE_CACHE_LOCK:
        cached_releases = RELEASE_CACHE.get(api_url)
    if cached_releases is None:
        headers = _headers_for_url(api_url)
        async with ETAG_CACHE_LOCK:
            etag = ETAG_CACHE.get(api_url)
        if etag:
            headers['If-None-Match'] = etag
        response = await _get_with_retries(client, api_url, headers=headers)
        if response.status_code == 304:
            async with RELEASE_CACHE_LOCK:
                cached_releases = RELEASE_CACHE.get(api_url)
            if cached_releases is None:
                headers.pop('If-None-Match', None)
                response = await _get_with_retries(client, api_url, headers=headers)
        if response.status_code == 304:
            print(f"No cached releases available for {repo_url}; skipping.")
            return None, None, None, None, None, None
        if response.status_code == 200:
            etag_value = response.headers.get('ETag')
            if etag_value:
                async with ETAG_CACHE_LOCK:
                    ETAG_CACHE[api_url] = etag_value
                await _save_etag_cache(ETAG_CACHE)
            cached_releases = response.json()
            async with RELEASE_CACHE_LOCK:
                RELEASE_CACHE[api_url] = cached_releases
        else:
            print(f"Failed to fetch releases from {repo_url}")
            return None, None, None, None, None, None
    releases = cached_releases
    if not releases:
        print(f"No releases found for {repo_url}")
        return None, None, None, None, None, None
    releases = [
        release for release in releases
        if not release.get("draft") and not release.get("upcoming_release")
    ]
    if latest_flag:
        filtered_releases = sorted(releases, key=_release_time, reverse=True)
    elif prerelease:
        filtered_releases = sorted(
            (r for r in releases if _release_is_prerelease(r)),
            key=_release_time,
            reverse=True
        )
    else:
        filtered_releases = sorted(
            (r for r in releases if not _release_is_prerelease(r)),
            key=_release_time,
            reverse=True
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
        if any(download_urls[ext] for ext in file_types):
            return version, created_at, description, download_urls, signature_url, release_url
    print(f"No suitable release with .jar, .apk, .rvp, or .mpp assets found for {repo_url}")
    return None, None, None, None, None, None

async def fetch_release_data(
    client: AsyncClient, source: str, repo: Mapping[str, Any]
) -> bool | None:
    try:
        prerelease = repo.get('prerelease', False)
        latest_flag = repo.get('latest', False)
        patches_repo = repo.get('patches')
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
            return None
        info_dict: dict[str, Any]
        metadata_entry: dict[str, Any] = {
            "source": source,
            "base_source": source.replace('-dev', '').replace('-latest', '').replace('-stable', ''),
            "artifact_path": "",
            "type": "",
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
                "signature_download_url": patches_signature_url if patches_signature_url else "N/A",
                "version": patches_version
            }
            metadata_entry["type"] = "mpp"
            metadata_entry["patches"]["download_url"] = patches_download_urls[".mpp"]
        elif patches_download_urls[".rvp"]:
            info_dict = {
                "created_at": patches_created_at,
                "description": patches_description or "",
                "download_url": patches_download_urls[".rvp"],
                "signature_download_url": patches_signature_url if patches_signature_url else "N/A",
                "version": patches_version
            }
            metadata_entry["type"] = "rvp"
            metadata_entry["patches"]["download_url"] = patches_download_urls[".rvp"]
        else:
            jar_url = patches_download_urls[".jar"]
            if jar_url:
                integration_repo = repo.get('integration')
                if not isinstance(integration_repo, str) or not integration_repo:
                    print(f"Integration repository not defined for {source}; skipping.")
                    return None
                (
                    integrations_version,
                    integrations_created_at,
                    integrations_description,
                    integrations_download_urls,
                    integrations_signature_url,
                    integrations_release_url,
                ) = await get_latest_release(client, integration_repo, prerelease, latest_flag)
                if integrations_download_urls and integrations_download_urls[".apk"]:
                    apk_url = integrations_download_urls[".apk"]
                    info_dict = {
                        "patches": {
                            "version": patches_version,
                            "url": jar_url
                        },
                        "integrations": {
                            "version": integrations_version,
                            "url": apk_url
                        }
                    }
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
                    print(f"No relevant .apk asset found in integration repo for {source}")
                    return None
            else:
                print(f"No relevant .rvp, .mpp, or .jar assets found for {source}")
                return None
        base_source = source.replace('-dev', '').replace('-latest', '').replace('-stable', '')
        directory = PATCH_BUNDLES_DIR / f"{base_source}-patch-bundles"
        directory.mkdir(parents=True, exist_ok=True)
        filepath = directory / f'{source}-patches-bundle.json'
        await asyncio.to_thread(_dump_json_sync, filepath, info_dict)
        relative_filepath = filepath.relative_to(PROJECT_ROOT)
        print(f"Latest release information saved to {relative_filepath}")
        metadata_entry["artifact_path"] = str(relative_filepath)
        async with METADATA_LOCK:
            BUNDLE_METADATA[source] = metadata_entry
        return True
    except HTTPStatusError as exc:
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
        print(f"Error in fetch_release_data for {source}: {exc}")
        return False

def _load_sources_sync() -> dict[str, Any]:
    with BUNDLE_SOURCES_PATH.open(encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("bundle-sources.json does not contain object data")
    return data




async def main() -> int:
    try:
        raw_sources = await asyncio.to_thread(_load_sources_sync)
        sources: dict[str, RepoConfig] = {
            str(name): value for name, value in raw_sources.items()
            if isinstance(value, Mapping)
        }
        async with AsyncClient(timeout=HTTP_TIMEOUT) as client:
            tasks = [fetch_release_data(client, source, repo) for source, repo in sources.items()]
            results = await asyncio.gather(*tasks, return_exceptions=True)
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
            "bundles": BUNDLE_METADATA,
        }
        await asyncio.to_thread(_dump_json_sync, METADATA_PATH, metadata_payload)
        return 1 if had_task_failure else 0
    except Exception as exc:
        print(f"Error in main: {exc}")
        return 1

if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
