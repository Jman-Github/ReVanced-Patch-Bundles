import asyncio
import json
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import AsyncMock

import httpx
import pytest

from scripts import generate_bundles as bundles

REPO = "https://api.github.com/repos/example/patches"


def release(version: str, prerelease: bool = False) -> dict[str, object]:
    return {
        "tag_name": version,
        "published_at": "2026-10-07T12:00:00Z" if prerelease else "2026-10-06T12:00:00Z",
        "prerelease": prerelease,
        "assets": [{"browser_download_url": f"https://example.com/{version}/patches.rvp"}],
    }


@pytest.fixture(autouse=True)
def reset_state(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setattr(bundles, "RELEASE_CACHE", {})
    monkeypatch.setattr(bundles, "RELEASE_REQUESTS", {})
    monkeypatch.setattr(bundles, "HTTP_SEMAPHORE", asyncio.Semaphore(6))
    monkeypatch.setattr(bundles, "_sleep_with_backoff", AsyncMock())
    yield


def test_concurrent_variants_share_request() -> None:
    requests: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        await asyncio.sleep(0)
        return httpx.Response(200, json=[release("v2-dev", True), release("v1")])

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            results = await asyncio.gather(
                bundles.get_latest_release(client, REPO, False, True),
                bundles.get_latest_release(client, REPO, False),
                bundles.get_latest_release(client, REPO, True),
            )
        assert [result[0] for result in results] == ["v2-dev", "v1", "v2-dev"]

    asyncio.run(run())
    assert len(requests) == 1


@pytest.mark.parametrize("status", [404, 410, 451])
def test_missing_repository_is_shared_without_retries(status: int) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(status)

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            results = await asyncio.gather(
                bundles.fetch_release_data(client, "demo-latest", {"patches": REPO}),
                bundles.fetch_release_data(client, "demo-stable", {"patches": REPO}),
                bundles.fetch_release_data(client, "demo-dev", {"patches": REPO}),
            )
        assert results == [None, None, None]

    asyncio.run(run())
    assert len(requests) == 1
    bundles._sleep_with_backoff.assert_not_awaited()


def test_unchanged_response_reuses_persisted_payload() -> None:
    requests: list[httpx.Request] = []
    bundles.RELEASE_CACHE[f"{REPO}/releases"] = {"etag": '"cached"', "releases": [release("v1")]}

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(304)

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await bundles.get_latest_release(client, REPO, False)
        assert result[0] == "v1"

    asyncio.run(run())
    assert len(requests) == 1
    assert requests[0].headers["If-None-Match"] == '"cached"'


def test_changed_response_refreshes_etag_and_payload() -> None:
    bundles.RELEASE_CACHE[f"{REPO}/releases"] = {"etag": '"old"', "releases": [release("v1")]}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["If-None-Match"] == '"old"'
        return httpx.Response(200, headers={"ETag": '"new"'}, json=[release("v2")])

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await bundles.get_latest_release(client, REPO, False)
        assert result[0] == "v2"

    asyncio.run(run())
    assert bundles.RELEASE_CACHE[f"{REPO}/releases"] == {
        "etag": '"new"',
        "releases": [release("v2")],
    }


def test_transient_error_is_retried() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(503 if len(requests) == 1 else 200, json=[])

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await bundles._get_with_retries(client, REPO, {})
        assert result.status_code == 200

    asyncio.run(run())
    assert len(requests) == 2
    bundles._sleep_with_backoff.assert_awaited_once_with(0, None)


def test_exhausted_retries_preserve_http_error_without_final_sleep() -> None:
    async def run() -> None:
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(503))
        ) as client:
            with pytest.raises(httpx.HTTPStatusError) as error:
                await bundles._get_with_retries(client, REPO, {})
        assert error.value.response.status_code == 503

    asyncio.run(run())
    assert bundles._sleep_with_backoff.await_count == bundles.MAX_RETRIES - 1


@pytest.mark.parametrize(
    ("status", "headers", "body", "resume_at"),
    [
        (403, {"Retry-After": "20"}, "", 120),
        (403, {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "150"}, "", 150),
        (403, {}, "You have exceeded a secondary rate limit.", 160),
        (
            403,
            {"X-RateLimit-Remaining": "4999", "X-RateLimit-Reset": "3600", "Retry-After": "20"},
            "",
            120,
        ),
        (
            403,
            {"X-RateLimit-Remaining": "4999", "X-RateLimit-Reset": "3600"},
            "You have exceeded a secondary rate limit.",
            160,
        ),
        (429, {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "3600"}, "", 3600),
        (
            429,
            {"X-RateLimit-Remaining": "4999", "X-RateLimit-Reset": "3600", "Retry-After": "20"},
            "",
            120,
        ),
        (
            403,
            {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "150", "Retry-After": "20"},
            "",
            150,
        ),
    ],
)
def test_rate_limit_waits_for_server(
    monkeypatch: pytest.MonkeyPatch,
    status: int,
    headers: dict[str, str],
    body: str,
    resume_at: int,
) -> None:
    monkeypatch.setattr(bundles.time, "time", lambda: 100)
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return (
            httpx.Response(status, headers=headers, text=body)
            if len(requests) == 1
            else (httpx.Response(200))
        )

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            await bundles._get_with_retries(client, REPO, {})

    asyncio.run(run())
    bundles._sleep_with_backoff.assert_awaited_once_with(0, resume_at)


@pytest.mark.parametrize(
    "payload", [None, [], {"url": "etag-only"}, {"url": {"etag": "x", "releases": [None]}}]
)
def test_invalid_cache_is_ignored(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, payload: object
) -> None:
    cache_path = tmp_path / "release_cache.json"
    cache_path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(bundles, "RELEASE_CACHE_FILE", cache_path)

    assert bundles._load_release_cache() == {}


def test_cache_survives_another_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    cache_path = tmp_path / "release_cache.json"
    cached = {f"{REPO}/releases": {"etag": '"saved"', "releases": [release("v1")]}}
    monkeypatch.setattr(bundles, "RELEASE_CACHE_FILE", cache_path)
    bundles._dump_json_sync(cache_path, cached)

    assert bundles._load_release_cache() == cached


def test_main_revalidates_releases_on_next_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sources_path = tmp_path / "sources.json"
    sources_path.write_text(
        json.dumps(
            {
                "demo-latest": {"patches": REPO, "latest": True},
                "demo-stable": {"patches": REPO},
                "demo-dev": {"patches": REPO, "prerelease": True},
            }
        ),
        encoding="utf-8",
    )
    cache_path = tmp_path / "cache.json"
    metadata_path = tmp_path / "metadata.json"
    monkeypatch.setattr(bundles, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(bundles, "PATCH_BUNDLES_DIR", tmp_path / "patch-bundles")
    monkeypatch.setattr(bundles, "BUNDLE_SOURCES_PATH", sources_path)
    monkeypatch.setattr(bundles, "RELEASE_CACHE_FILE", cache_path)
    monkeypatch.setattr(bundles, "METADATA_PATH", metadata_path)
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.headers.get("If-None-Match") == '"saved"':
            return httpx.Response(304)
        return httpx.Response(
            200,
            headers={"ETag": '"saved"'},
            json=[
                release("v2-dev", True),
                release("v1"),
            ],
        )

    monkeypatch.setattr(
        bundles,
        "AsyncClient",
        lambda **kwargs: httpx.AsyncClient(transport=httpx.MockTransport(handler), **kwargs),
    )

    async def run() -> None:
        assert await bundles.main() == 0
        # Reload the saved file to simulate a fresh process on another runner.
        bundles.RELEASE_CACHE = bundles._load_release_cache()
        assert await bundles.main() == 0

    asyncio.run(run())
    assert len(requests) == 2
    assert requests[1].headers["If-None-Match"] == '"saved"'
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))["bundles"]
    assert {source: value["patches"]["version"] for source, value in metadata.items()} == {
        "demo-latest": "v2-dev",
        "demo-stable": "v1",
        "demo-dev": "v2-dev",
    }
