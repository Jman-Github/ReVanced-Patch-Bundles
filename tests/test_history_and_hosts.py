import asyncio
import json
import shutil

import httpx
import pytest
from test_generate_database import fixture, snapshot, write

from scripts import discover_releases as discovery
from scripts import generate_database as db
from scripts.git_hosts import auth_headers, endpoint, normalize_source
from scripts.release_history import save_history


def test_git_host_endpoints_and_token_scope(tmp_path, monkeypatch):
    write(
        tmp_path / "config/git-hosts.json",
        {"git.example.test:8443": "gitlab", "gitea.example.test": "gitea"},
    )
    assert normalize_source("codeberg.org/Owner/Repo.git") == "https://codeberg.org/Owner/Repo"
    assert (
        endpoint("https://gitea.com/owner/repo")
        == "https://gitea.com/api/v1/repos/owner/repo/releases"
    )
    assert endpoint("https://git.example.test:8443/team/sub/repo", root=tmp_path) == (
        "https://git.example.test:8443/api/v4/projects/team%2Fsub%2Frepo/releases"
    )
    monkeypatch.setenv("GH_PAT", "public-token")
    monkeypatch.setenv("GIT_HOST_TOKENS", '{"gitea.example.test":"scoped-token"}')
    assert auth_headers("https://gitea.example.test/owner/repo", tmp_path)["Authorization"] == (
        "Bearer scoped-token"
    )
    assert "Authorization" not in auth_headers("codeberg.org/owner/repo", tmp_path)
    with pytest.raises(ValueError):
        normalize_source("https://unconfigured.example.test/owner/repo", tmp_path)


def test_all_release_pages_and_cached_pagination(monkeypatch):
    monkeypatch.setattr(discovery, "RELEASE_CACHE", {})
    seen = []
    first = "https://api.github.com/repos/owner/repo/releases"
    second = first + "?page=2"

    def handler(request):
        seen.append(str(request.url))
        if "if-none-match" in request.headers:
            return httpx.Response(304)
        page = 2 if request.url.params.get("page") == "2" else 1
        headers = {"etag": f'"page{page}"'}
        if page == 1:
            headers["link"] = f'<{second}>; rel="next"'
        return httpx.Response(200, headers=headers, json=[{"tag_name": f"v{page}"}])

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            assert [r["tag_name"] for r in await discovery._fetch_releases(client, first)] == [
                "v1",
                "v2",
            ]
            assert [r["tag_name"] for r in await discovery._fetch_releases(client, first)] == [
                "v1",
                "v2",
            ]

    asyncio.run(run())
    assert seen == [first + "?per_page=100", second, first + "?per_page=100", second]


def test_history_is_published_without_replacing_channels_and_restores_on_fresh_runner(tmp_path):
    folder = fixture(tmp_path)
    inventory = db.read_json(tmp_path / "config/sources.json")
    releases = [
        {
            "tag_name": "v0",
            "published_at": "2025-01-01T00:00:00Z",
            "assets": [{"browser_download_url": "https://example.test/v0.rvp"}],
        }
    ]
    registry = save_history(tmp_path, inventory, {"https://github.com/owner/demo": releases})
    assert len(registry) == 1
    first = db.build_database(tmp_path)
    snapshot = tmp_path / "database" / first["snapshot"]
    bundles = db.read_json(snapshot / "bundles.json")
    historical = next(b for b in bundles if b["version"] == "v0")
    assert historical["channels"] == []
    assert historical["need_patches_update"]
    assert next(b for b in bundles if b["version"] == "v1")["is_latest"]
    identifier = historical["legacy_id"]
    assert folder.exists()
    shutil.rmtree(tmp_path / "internal/cache")
    db.restore_catalog_cache(tmp_path)
    second = db.build_database(tmp_path)
    bundles = db.read_json(tmp_path / "database" / second["snapshot"] / "bundles.json")
    assert next(b for b in bundles if b["version"] == "v0")["legacy_id"] == identifier
    assert db.read_json(tmp_path / "internal/cache/history/sources.json")


def test_history_retries_survive_catalog_roundtrip(tmp_path):
    fixture(tmp_path)
    inventory = db.read_json(tmp_path / "config/sources.json")
    registry = save_history(
        tmp_path,
        inventory,
        {
            "https://github.com/owner/demo": [
                {
                    "tag_name": "v0",
                    "assets": [{"browser_download_url": "https://example.test/v0.rvp"}],
                }
            ]
        },
    )
    key, settings = next(iter(registry.items()))
    path = tmp_path / settings["cache_path"]
    write(
        path.with_name(f"{key}-extraction.json"),
        {
            "version": "v0",
            "download_url": "https://example.test/v0.rvp",
            "status": "runtime_initialization_failure",
            "attempted_at": "2026-10-08T00:00:00Z",
            "failure_fingerprint": "runtime",
        },
    )
    db.build_database(tmp_path)
    shutil.rmtree(tmp_path / "internal/cache")
    db.restore_catalog_cache(tmp_path)
    registry = db.read_json(tmp_path / "internal/cache/history/sources.json")
    settings = registry[key]
    restored = db.read_json((tmp_path / settings["cache_path"]).with_name(f"{key}-extraction.json"))
    assert restored["attempted_at"] == "2026-10-08T00:00:00Z"
    assert restored["failure_fingerprint"] == "runtime"


def test_all_historical_formats_and_prerelease_are_retained(tmp_path):
    inventory = {"demo-stable": {"patches": "https://codeberg.org/owner/repo"}}
    registry = save_history(
        tmp_path,
        inventory,
        {
            "https://codeberg.org/owner/repo": [
                {
                    "tag_name": f"v0-{ext}",
                    "prerelease": True,
                    "assets": [
                        {
                            "browser_download_url": f"https://codeberg.org/owner/repo/releases/download/v0-{ext}/p.{ext}"
                        }
                    ],
                }
                for ext in ["jar", "mpp", "rvp"]
            ]
        },
    )
    assert len(registry) == 3
    assert all(item["prerelease"] for item in registry.values())
    for item in registry.values():
        raw = json.loads((tmp_path / item["cache_path"]).read_text())
        assert raw["is_prerelease"]


def test_history_merge_preserves_current_legacy_integrations(tmp_path):
    fixture(tmp_path)
    inventory = {"zzz-stable": {"patches": "https://github.com/owner/demo"}}
    write(tmp_path / "config/sources.json", inventory)
    download = "https://example.test/demo.jar"
    integrations = {"version": "v1", "url": "https://example.test/integrations.apk"}
    raw = {"patches": {"version": "v1", "url": download}, "integrations": integrations}
    folder = tmp_path / "internal/cache/bundles/zzz-patch-bundles"
    write(folder / "zzz-stable-patches-bundle.json", raw)
    patches = {"version": "v1", "patches": [{"name": "Patch"}]}
    patch_path = folder / "zzz-stable-patches-list.json"
    write(patch_path, patches)
    proof = {
        "version": "v1",
        "download_url": download,
        "status": "verified",
        "file_hash": "a" * 64,
        "patch_list_hash": db.digest(patch_path.read_bytes()),
    }
    write(folder / "zzz-stable-extraction.json", proof)
    registry = save_history(
        tmp_path,
        inventory,
        {
            "https://github.com/owner/demo": [
                {"tag_name": "v1", "assets": [{"browser_download_url": download}]}
            ]
        },
    )
    key, settings = next(iter(registry.items()))
    historical = tmp_path / settings["cache_path"]
    write(historical.with_name(f"{key}-patches-list.json"), patches)
    write(historical.with_name(f"{key}-extraction.json"), proof)
    manifest = db.build_database(tmp_path)
    bundles = db.read_json(tmp_path / "database" / manifest["snapshot"] / "bundles.json")
    assert len(bundles) == 1
    assert bundles[0]["integrations"] == integrations


def test_release_redirect_does_not_forward_token_to_another_host():
    seen = []

    def handler(request):
        seen.append((request.url.host, request.headers.get("private-token")))
        if request.url.host == "gitlab.com":
            return httpx.Response(302, headers={"location": "https://other.test/releases"})
        return httpx.Response(200, json=[])

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            with pytest.raises(ValueError, match="authority"):
                await discovery._get_with_retries(
                    client,
                    "https://gitlab.com/api/v4/projects/team%2Frepo/releases",
                    {"PRIVATE-TOKEN": "scoped-token"},
                )

    asyncio.run(run())
    assert seen == [("gitlab.com", "scoped-token")]


def test_github_discovery_honors_scoped_token(monkeypatch):
    monkeypatch.setenv("GH_PAT", "fallback-token")
    monkeypatch.setenv("GIT_HOST_TOKENS", '{"github.com":"scoped-token"}')
    headers = discovery._headers_for_url("https://api.github.com/repos/owner/repo/releases")
    assert headers["Authorization"] == "Bearer scoped-token"


def test_gitlab_pagination_keeps_page_size(monkeypatch):
    monkeypatch.setattr(discovery, "RELEASE_CACHE", {})
    seen = []

    def handler(request):
        seen.append(dict(request.url.params))
        page = request.url.params.get("page", "1")
        headers = {"x-next-page": "2"} if page == "1" else {}
        return httpx.Response(200, headers=headers, json=[{"tag_name": "v" + page}])

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            releases = await discovery._fetch_releases(
                client, "https://gitlab.com/api/v4/projects/team%2Frepo/releases"
            )
            assert [r["tag_name"] for r in releases] == ["v1", "v2"]

    asyncio.run(run())
    assert seen == [{"per_page": "100"}, {"per_page": "100", "page": "2"}]


@pytest.mark.parametrize(
    ("tag", "prerelease", "expected"),
    [
        ("v1-rc1", None, True),
        ("v1-dev", None, True),
        ("v1-beta", None, True),
        ("v1-dev-build", False, False),
        ("v1", True, True),
    ],
)
def test_historical_prerelease_matches_discovery(tmp_path, tag, prerelease, expected):
    fixture(tmp_path)
    inventory = db.read_json(tmp_path / "config/sources.json")
    release = {
        "tag_name": tag,
        "assets": [{"browser_download_url": "https://example.test/old.rvp"}],
    }
    if prerelease is not None:
        release["prerelease"] = prerelease
    registry = save_history(tmp_path, inventory, {"https://github.com/owner/demo": [release]})
    assert all(item["prerelease"] is expected for item in registry.values())
    manifest = db.build_database(tmp_path)
    bundles = db.read_json(tmp_path / "database" / manifest["snapshot"] / "bundles.json")
    assert (
        next(b for b in bundles if b["download_url"] == "https://example.test/old.rvp")[
            "is_prerelease"
        ]
        is expected
    )


def test_historical_signature_urls_can_have_independent_queries(tmp_path):
    artifact = "https://example.test/patches.rvp?download=1"
    signature = "https://example.test/patches.rvp.asc?token=signature"
    inventory = {"demo-stable": {"patches": "https://github.com/owner/demo"}}
    registry = save_history(
        tmp_path,
        inventory,
        {
            "https://github.com/owner/demo": [
                {
                    "tag_name": "v0",
                    "assets": [{"browser_download_url": url} for url in [artifact, signature]],
                }
            ]
        },
    )
    settings = next(iter(registry.values()))
    raw = db.read_json(tmp_path / settings["cache_path"])
    assert raw["download_url"] == artifact
    assert raw["signature_download_url"] == signature


def test_history_latest_flags_match_catalog_categories_and_survive_restoration(tmp_path):
    fixture(tmp_path)
    inventory = db.read_json(tmp_path / "config/sources.json")
    source = "https://github.com/owner/demo"
    releases = [
        {
            "tag_name": "older",
            "created_at": "2025-01-01T00:00:00Z",
            "published_at": "2028-01-01T00:00:00Z",
        },
        {"tag_name": "stable", "created_at": "2027-01-01T02:00:00+02:00"},
        {"tag_name": "dev", "created_at": "2026-02-01T00:00:00.123Z", "prerelease": True},
        {"tag_name": "old-dev", "created_at": "2026-01-01T00:00:00Z", "prerelease": True},
    ]
    for release in releases:
        release["assets"] = [
            {"browser_download_url": f"https://example.test/{release['tag_name']}.rvp"}
        ]
    registry = save_history(tmp_path, inventory, {source: releases})

    def versions(registry):
        return {
            db.read_json(tmp_path / item["cache_path"])["version"]
            for item in registry.values()
            if item.get("is_latest")
        }

    assert versions(registry) == {"stable", "dev"}
    manifest = db.build_database(tmp_path, restore=False)
    _, bundles = snapshot(tmp_path, manifest)
    assert {b["version"] for b in bundles if b["is_latest"]} == versions(registry)
    # A provider outage retains the computed latest work instead of dropping it.
    assert versions(save_history(tmp_path, inventory, {})) == {"stable", "dev"}
    shutil.rmtree(tmp_path / "internal/cache")
    db.restore_catalog_cache(tmp_path)
    assert versions(db.read_json(tmp_path / "internal/cache/history/sources.json")) == {
        "stable",
        "dev",
    }
    # Current channel inputs win equal timestamps and need no extra latest pass.
    folder = tmp_path / "internal/cache/bundles/demo-patch-bundles"
    for channel in ("latest", "stable"):
        write(
            folder / f"demo-{channel}-patches-bundle.json",
            {
                "version": "stable",
                "created_at": "2027-01-01T00:00:00Z",
                "download_url": "https://example.test/stable.rvp",
                "is_prerelease": False,
            },
        )
    assert versions(save_history(tmp_path, inventory, {source: releases})) == {"dev"}


@pytest.mark.parametrize(
    "replacement",
    [
        {"browser_download_url": "https://example.test/replacement.rvp"},
        {"browser_download_url": "https://example.test/demo.rvp", "digest": "sha256:" + "b" * 64},
        {"browser_download_url": "https://example.test/replacement.mpp"},
    ],
)
def test_latest_history_replacement_is_not_covered_by_a_stale_channel_pointer(
    tmp_path, replacement
):
    fixture(tmp_path)
    registry = save_history(
        tmp_path,
        db.read_json(tmp_path / "config/sources.json"),
        {
            "https://github.com/owner/demo": [
                {
                    "tag_name": "v1",
                    "created_at": "2026-01-01T00:00:00Z",
                    "assets": [replacement],
                }
            ],
        },
    )
    assert next(iter(registry.values()))["is_latest"]
    _, bundles = snapshot(tmp_path, db.build_database(tmp_path, restore=False))
    assert bundles[0]["is_latest"] and bundles[0]["need_patches_update"]
    assert bundles[0]["download_url"] == replacement["browser_download_url"]
    assert bundles[0]["provider_digest"] == replacement.get("digest")
