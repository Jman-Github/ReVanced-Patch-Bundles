import asyncio
import json
import os
import re
import secrets
import subprocess
import time
from collections.abc import Mapping
from typing import Any

from httpx import AsyncClient, HTTPError, Response, Timeout

ETAG_CACHE_FILE = "etag_cache.json"

def _load_etag_cache() -> dict[str, str]:
    if os.path.exists(ETAG_CACHE_FILE):
        try:
            with open(ETAG_CACHE_FILE, encoding="utf-8") as cache_file:
                data = json.load(cache_file)
                if isinstance(data, dict):
                    return {str(key): str(value) for key, value in data.items()}
                return {}
        except Exception:
            return {}
    return {}

ETAG_CACHE_LOCK = asyncio.Lock()

def _write_etag_cache_sync(cache: Mapping[str, str]) -> None:
    with open(ETAG_CACHE_FILE, "w", encoding="utf-8") as cache_file:
        json.dump(cache, cache_file, indent=2)

async def _save_etag_cache(cache: Mapping[str, str]) -> None:
    async with ETAG_CACHE_LOCK:
        await asyncio.to_thread(_write_etag_cache_sync, cache)

def _dump_json_sync(path: str, payload: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)

BOT_EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"
BOT_NAME = "github-actions[bot]"
RepoConfig = Mapping[str, Any]
ETAG_CACHE = _load_etag_cache()

GH_PAT = os.getenv('GH_PAT')

BASE_HEADERS: dict[str, str] = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "revanced-patch-bundles/1.0 (+https://github.com/Jman-Github/ReVanced-Patch-Bundles)",
}
if GH_PAT:
    BASE_HEADERS["Authorization"] = f"Bearer {GH_PAT}"

MAX_RETRIES = 5
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
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
                response = await client.get(url, headers=headers)
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

async def get_latest_release(
    client: AsyncClient,
    repo_url: str,
    prerelease: bool,
    latest_flag: bool = False,
) -> tuple[str | None, str | None, str | None, dict[str, str | None] | None, str | None]:
    async def get_version_urls(
        release: Mapping[str, Any], file_types: tuple[str, ...]
    ) -> tuple[str, str, str, dict[str, str | None], str | None]:
        version = release['tag_name']
        published_at = re.sub(r'[A-Za-z]+$', '', release['published_at'])
        description = release.get('body', '')
        download_urls: dict[str, str | None] = {ext: None for ext in file_types}
        signature_url = None
        for asset in release["assets"]:
            for ext in file_types:
                if asset["browser_download_url"].endswith(ext):
                    download_urls[ext] = asset['browser_download_url']
            if asset["browser_download_url"].endswith(".rvp.asc"):
                signature_url = asset['browser_download_url']
        return version, published_at, description, download_urls, signature_url

    api_url = f"{repo_url}/releases"
    headers = dict(BASE_HEADERS)
    async with ETAG_CACHE_LOCK:
        etag = ETAG_CACHE.get(api_url)
    if etag:
        headers['If-None-Match'] = etag
    response = await _get_with_retries(client, api_url, headers=headers)
    if response.status_code == 304:
        print(f"No changes for {repo_url}; skipping.")
        return None, None, None, None, None
    if response.status_code == 200:
        etag_value = response.headers.get('ETag')
        if etag_value:
            async with ETAG_CACHE_LOCK:
                ETAG_CACHE[api_url] = etag_value
            await _save_etag_cache(ETAG_CACHE)
        releases = response.json()
        if not releases:
            print(f"No releases found for {repo_url}")
            return None, None, None, None, None
        if latest_flag:
            filtered_releases = sorted(releases, key=lambda x: x["published_at"], reverse=True)
        elif prerelease:
            filtered_releases = sorted(
                (r for r in releases if r["prerelease"]),
                key=lambda x: x["published_at"],
                reverse=True
            )
        else:
            filtered_releases = sorted(
                (r for r in releases if not r["prerelease"]),
                key=lambda x: x["published_at"],
                reverse=True
            )
        file_types = (".jar", ".apk", ".rvp")
        for release in filtered_releases:
            (
                version,
                created_at,
                description,
                download_urls,
                signature_url,
            ) = await get_version_urls(release, file_types)
            if any(download_urls[ext] for ext in file_types):
                return version, created_at, description, download_urls, signature_url
        print(f"No suitable release with .jar, .apk, or .rvp assets found for {repo_url}")
        return None, None, None, None, None
    else:
        print(f"Failed to fetch releases from {repo_url}")
        return None, None, None, None, None

async def fetch_release_data(client: AsyncClient, source: str, repo: Mapping[str, Any]) -> None:
    try:
        prerelease = repo.get('prerelease', False)
        latest_flag = repo.get('latest', False)
        patches_repo = repo.get('patches')
        if not isinstance(patches_repo, str) or not patches_repo:
            print(f"Patch repository not defined for {source}; skipping.")
            return
        (
            patches_version,
            patches_created_at,
            patches_description,
            patches_download_urls,
            patches_signature_url
        ) = await get_latest_release(client, patches_repo, prerelease, latest_flag)
        if not patches_download_urls:
            return
        info_dict: dict[str, Any]
        if patches_download_urls[".rvp"]:
            info_dict = {
                "created_at": patches_created_at,
                "description": patches_description or "",
                "download_url": patches_download_urls[".rvp"],
                "signature_download_url": patches_signature_url if patches_signature_url else "N/A",
                "version": patches_version
            }
        else:
            jar_url = patches_download_urls[".jar"]
            if jar_url:
                integration_repo = repo.get('integration')
                if not isinstance(integration_repo, str) or not integration_repo:
                    print(f"Integration repository not defined for {source}; skipping.")
                    return
                (
                    integrations_version,
                    _integrations_created_at,
                    _integrations_description,
                    integrations_download_urls,
                    _integrations_signature_url
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
                else:
                    print(f"No relevant .apk asset found in integration repo for {source}")
                    return
            else:
                print(f"No relevant .rvp or .jar assets found for {source}")
                return
        base_source = source.replace('-dev', '').replace('-latest', '').replace('-stable', '')
        directory = os.path.join('patch-bundles', f"{base_source}-patch-bundles")
        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, f'{source}-patches-bundle.json')
        await asyncio.to_thread(_dump_json_sync, filepath, info_dict)
        print(f"Latest release information saved to {filepath}")
        await asyncio.to_thread(subprocess.run, ["git", "add", filepath], check=True)
        print(f"File {filepath} staged for commit.")
    except Exception as exc:
        print(f"Error in fetch_release_data for {source}: {exc}")

def _load_sources_sync() -> dict[str, Any]:
    with open("bundle-sources.json", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("bundle-sources.json does not contain object data")
    return data




async def main() -> None:
    try:
        raw_sources = await asyncio.to_thread(_load_sources_sync)
        sources: dict[str, RepoConfig] = {
            str(name): value for name, value in raw_sources.items()
            if isinstance(value, Mapping)
        }
        await asyncio.to_thread(
            subprocess.run,
            ["git", "config", "user.email", BOT_EMAIL],
            check=True,
        )
        await asyncio.to_thread(
            subprocess.run,
            ["git", "config", "user.name", BOT_NAME],
            check=True,
        )
        async with AsyncClient(timeout=HTTP_TIMEOUT) as client:
            tasks = [fetch_release_data(client, source, repo) for source, repo in sources.items()]
            results = await asyncio.gather(*tasks, return_exceptions=True)
        for (source, _), result in zip(sources.items(), results, strict=False):
            if isinstance(result, Exception):
                print(f"Task for {source} failed: {result}")
    except subprocess.CalledProcessError as exc:
        print(f"Subprocess failed: {exc}")
    except Exception as exc:
        print(f"Error in main: {exc}")
if __name__ == "__main__":
    asyncio.run(main())
