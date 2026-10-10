import asyncio
import json
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import AsyncMock

import httpx
import pytest

from scripts import discover_releases as bundles

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
    monkeypatch.setattr(bundles, "RELEASE_COOLDOWNS", {})
    monkeypatch.setattr(bundles, "HTTP_SEMAPHORE", asyncio.Semaphore(6))
    monkeypatch.setattr(bundles, "_sleep_with_backoff", AsyncMock())
    yield


@pytest.mark.parametrize("newest_artifact", ["patch", "integration"])
def test_patch_and_integration_selection_skip_releases_without_required_artifacts(
    newest_artifact,
) -> None:
    requests = []
    patch = release("patch-v1")
    patch["assets"] = [{"browser_download_url": "https://example.com/patches.jar"}]
    apk = release("apk-v2")
    apk["assets"] = [{"browser_download_url": "https://example.com/integrations.apk"}]
    newest = patch if newest_artifact == "patch" else apk
    newest["published_at"] = "2026-10-08T12:00:00Z"

    def handler(request):
        requests.append(request)
        return httpx.Response(200, json=[apk, patch])

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            selected = await bundles.get_latest_release(client, REPO, False)
            assert selected[0] == "patch-v1"
            # Artifact selection changes without another release-list request.
            integration = await bundles.get_latest_release(
                client, REPO, False, required_extensions=(".apk",)
            )
            assert integration[0] == "apk-v2"
        assert len(requests) == 1

    asyncio.run(run())


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
        (403, {"Retry-After": "Thu, 01 Jan 1970 00:03:20 GMT"}, "", 200),
        (429, {"Retry-After": "Thu, 01 Jan 1970 00:03:20 GMT"}, "", 200),
        (503, {"Retry-After": "Thu, 01 Jan 1970 00:03:20 GMT"}, "", 200),
        (503, {"Retry-After": "invalid"}, "", None),
        (
            403,
            {
                "Retry-After": "Thu, 01 Jan 1970 00:03:20 GMT",
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": "300",
            },
            "",
            300,
        ),
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
    resume_at: int | None,
) -> None:
    clock = [100]
    monkeypatch.setattr(bundles.time, "time", lambda: clock[0])

    async def advance(_attempt, reset_at=None):
        if reset_at is not None:
            clock[0] = max(clock[0], reset_at + 1)

    bundles._sleep_with_backoff.side_effect = advance
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


@pytest.mark.parametrize("case", ["missing_integration", "unconfigured_integration", "apk_only"])
def test_legacy_discovery_does_not_require_integrations(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    case: str,
) -> None:
    monkeypatch.setattr(bundles, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(bundles, "PATCH_BUNDLES_DIR", tmp_path / "internal/cache/bundles")
    monkeypatch.setattr(bundles, "DISCOVERY_STATUS", {"demo-stable": "available"})
    monkeypatch.setattr(bundles, "BUNDLE_METADATA", {})
    folder = bundles.PATCH_BUNDLES_DIR / "demo-patch-bundles"
    folder.mkdir(parents=True)
    old_bundle = folder / "demo-stable-patches-bundle.json"
    old_bundle.write_text('{"patches":{"version":"v0","url":"https://example.test/v0.jar"}}')
    previous = old_bundle.read_bytes()
    patch_release = release("v1")
    extension = "apk" if case == "apk_only" else "jar"
    patch_release["assets"] = [
        {"browser_download_url": f"https://example.test/patches.{extension}"}
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        payload = [patch_release] if request.url.path.endswith("/patches/releases") else []
        return httpx.Response(200, json=payload)

    async def run() -> None:
        repo = {"patches": REPO}
        if case != "unconfigured_integration":
            repo["integration"] = "https://api.github.com/repos/example/integrations"
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await bundles.fetch_release_data(client, "demo-stable", repo)
            assert result is (None if case == "apk_only" else True)

    asyncio.run(run())
    if case == "apk_only":
        assert bundles.DISCOVERY_STATUS["demo-stable"] == "no_matching_release"
        assert old_bundle.read_bytes() == previous
    else:
        assert bundles.DISCOVERY_STATUS["demo-stable"] == "available"
        raw = json.loads(old_bundle.read_text())
        assert raw["patches"]["version"] == "v1"
        assert raw["created_at"] == patch_release["published_at"]
        assert "integrations" not in raw


@pytest.mark.parametrize(
    "repo",
    [
        "https://github.com/releases-team/releases-tools",
        "https://codeberg.org/releases-team/releases-tools",
    ],
)
def test_release_endpoint_does_not_truncate_repository_names(repo):
    seen = []

    def handler(request):
        seen.append(str(request.url))
        return httpx.Response(200, json=[release("v1")])

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await bundles.get_latest_release(client, repo, False)
            assert result[0] == "v1"

    asyncio.run(run())
    assert len(seen) == 1
    assert "/releases-team/releases-tools/releases?" in seen[0]


def test_download_url_queries_and_uppercase_extensions_are_eligible():
    artifact = "https://example.com/v1/patches.RVP?download=1"
    signature = "https://example.com/v1/patches.RVP.asc?token=signature"
    payload = release("v1")
    payload["assets"] = [{"browser_download_url": url} for url in [artifact, signature]]

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json=[payload]))
        ) as client:
            result = await bundles.get_latest_release(client, REPO, False)
            assert result[0] == "v1"
            assert result[3][".rvp"] == artifact
            assert result[4] == signature

    asyncio.run(run())


def test_signature_matches_the_selected_modern_artifact():
    payload = release("v1")
    urls = [
        "https://example.com/v1/patches.mpp",
        "https://example.com/v1/patches.rvp",
        "https://example.com/v1/patches.mpp.asc",
        "https://example.com/v1/patches.rvp.asc",
    ]
    payload["assets"] = [{"browser_download_url": url} for url in urls]

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json=[payload]))
        ) as client:
            result = await bundles.get_latest_release(client, REPO, False)
            assert result[3][".mpp"] == urls[0]
            assert result[4] == urls[2]

    asyncio.run(run())


def test_gitlab_suffix_prerelease_keeps_stable_and_dev_channels_separate():
    stable = release("v1")
    dev = release("v2-dev")
    del stable["prerelease"]
    del dev["prerelease"]
    dev["name"] = "Development build"
    dev["published_at"] = "2026-10-07T12:00:00Z"

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json=[dev, stable]))
        ) as client:
            results = await asyncio.gather(
                bundles.get_latest_release(client, "https://gitlab.com/team/patches", False),
                bundles.get_latest_release(client, "https://gitlab.com/team/patches", True),
            )
        assert [result[0] for result in results] == ["v1", "v2-dev"]

    asyncio.run(run())


def test_release_order_uses_utc_instead_of_offset_wall_clock():
    older = release("v1")
    older["published_at"] = "2026-10-08T02:00:00+02:00"
    newer = release("v2")
    newer["published_at"] = "2026-10-08T00:30:00Z"

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json=[older, newer]))
        ) as client:
            selected = await bundles.get_latest_release(client, REPO, False, True)
        assert selected[0] == "v2"

    asyncio.run(run())


@pytest.mark.parametrize(
    ("source", "channel"),
    [
        ("team-devtools-stable", "stable"),
        ("team-stabletools-dev", "dev"),
        ("team-latesttools-latest", "latest"),
    ],
)
def test_source_names_with_channel_words_reach_the_catalog(tmp_path, monkeypatch, source, channel):
    from scripts import generate_database as database

    monkeypatch.setattr(bundles, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(bundles, "PATCH_BUNDLES_DIR", tmp_path / "internal/cache/bundles")
    monkeypatch.setattr(bundles, "BUNDLE_METADATA", {})
    monkeypatch.setattr(bundles, "DISCOVERY_STATUS", {})
    settings = {"patches": REPO, "prerelease": channel == "dev", "latest": channel == "latest"}
    config = tmp_path / "config"
    config.mkdir()
    (config / "site.json").write_bytes(
        database.encoded(
            {
                "website": "https://example.test",
                "api": "https://api.example.test",
                "page_size": 2,
            }
        )
    )
    (config / "sources.json").write_bytes(database.encoded({source: settings}))

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json=[release("v1", channel == "dev")])
            )
        ) as client:
            assert await bundles.fetch_release_data(client, source, settings)

    asyncio.run(run())
    manifest = database.build_database(tmp_path)
    records = database.read_json(tmp_path / "database" / manifest["snapshot"] / "bundles.json")
    assert len(records) == 1
    assert records[0]["channels"] == [channel]
    assert bundles.BUNDLE_METADATA[source]["base_source"] == source.rsplit("-", 1)[0]


@pytest.mark.parametrize(
    ("status", "headers", "body", "deadline"),
    [
        (403, {"Retry-After": "60"}, "", 160),
        (429, {"Retry-After": "Thu, 01 Jan 1970 00:03:20 GMT"}, "", 200),
        (403, {}, "You have exceeded a secondary rate limit.", 160),
    ],
)
def test_rate_limit_pauses_queued_repositories_but_not_other_hosts(
    monkeypatch, status, headers, body, deadline
):
    clock = [100]
    calls = []
    monkeypatch.setattr(bundles.time, "time", lambda: clock[0])
    monkeypatch.setattr(bundles, "HTTP_SEMAPHORE", asyncio.Semaphore(1))

    async def run():
        first_paused = asyncio.Event()
        queued_paused = asyncio.Event()
        resume = asyncio.Event()

        async def backoff(_attempt, reset_at=None):
            assert reset_at == deadline
            first_paused.set()
            await resume.wait()

        async def cooldown_sleep(delay):
            assert delay == deadline - clock[0] + 1
            queued_paused.set()
            await resume.wait()

        bundles._sleep_with_backoff.side_effect = backoff
        monkeypatch.setattr(bundles.asyncio, "sleep", cooldown_sleep)

        def handler(request):
            calls.append((str(request.url), clock[0]))
            if len(calls) == 1:
                return httpx.Response(status, headers=headers, text=body)
            return httpx.Response(200)

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            first = asyncio.create_task(bundles._get_with_retries(client, REPO + "/a", {}))
            await asyncio.wait_for(first_paused.wait(), 1)
            second = asyncio.create_task(bundles._get_with_retries(client, REPO + "/b", {}))
            await asyncio.wait_for(queued_paused.wait(), 1)
            await bundles._get_with_retries(client, "https://gitlab.com/api/v4/projects/demo", {})
            assert len(calls) == 2
            assert calls[-1][0].startswith("https://gitlab.com/")
            clock[0] = deadline + 1
            resume.set()
            await asyncio.wait_for(asyncio.gather(first, second), 1)
        assert all(at > deadline for url, at in calls if url.startswith(REPO + "/b"))

    asyncio.run(run())
    assert len(calls) == 4


@pytest.mark.parametrize("code", [404, 410, 451])
def test_release_endpoint_errors_persist_automatic_source_availability(tmp_path, monkeypatch, code):
    from scripts.source_policy import PERMANENT_STATUS, source_availability

    monkeypatch.setattr(bundles, "PROJECT_ROOT", tmp_path)
    cache = tmp_path / "internal/cache"
    monkeypatch.setattr(bundles, "PATCH_BUNDLES_DIR", cache / "bundles")
    monkeypatch.setattr(bundles, "METADATA_PATH", cache / "bundle-run-metadata.json")
    monkeypatch.setattr(bundles, "RELEASE_CACHE_FILE", cache / "release_cache.json")
    monkeypatch.setattr(bundles, "_load_sources_sync", lambda: {"demo-stable": {"patches": REPO}})
    monkeypatch.setattr(
        bundles,
        "AsyncClient",
        lambda **kwargs: httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(code)), **kwargs
        ),
    )
    asyncio.run(bundles.main())
    assert (
        source_availability(tmp_path)["https://github.com/example/patches"]
        == PERMANENT_STATUS[code]
    )
