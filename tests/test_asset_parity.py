import asyncio
import hashlib
import json
import shutil

import httpx
import pytest
from test_generate_database import fixture, snapshot

from scripts import discover_releases as discovery
from scripts import generate_database as db
from scripts.postgres_collation import text_key
from scripts.release_assets import artifact_signature, asset_extension
from scripts.release_history import save_history


@pytest.mark.parametrize(
    ("url", "name", "expected"),
    [
        ("https://example.test/download/123", "patches.MPP", ".mpp"),
        ("https://example.test/patches.rvp?token=1", "arbitrary title", ".rvp"),
        ("https://example.test/checksum.txt", "patches.rvp", ".txt"),
        ("https://example.test/patches.rvp.asc", "patches.rvp", ".asc"),
    ],
)
def test_asset_name_fallback_keeps_concrete_url_authoritative(url, name, expected):
    assert asset_extension({"url": url, "name": name}) == expected


def test_signatures_use_query_then_unique_names_and_single_bundle_fallback():
    url = "https://example.test/patches.rvp?arch=arm"
    other = "https://example.test/patches.rvp?arch=x86"
    assets = [
        {"url": item, "name": ""}
        for item in [
            url,
            other,
            url.replace(".rvp?", ".rvp.asc?"),
            other.replace(".rvp?", ".rvp.asc?"),
        ]
    ]
    assert artifact_signature(url, assets) == url.replace(".rvp?", ".rvp.asc?")
    ambiguous = assets[:2] + [{"url": "https://example.test/patches.rvp.asc", "name": ""}]
    assert artifact_signature(url, ambiguous) is None
    named = [
        {"url": "https://example.test/download/123", "name": "patches.rvp"},
        {"url": "https://example.test/download/124", "name": "patches.rvp.asc"},
    ]
    assert artifact_signature(named[0]["url"], named) == named[1]["url"]
    arbitrary = [
        {"url": url, "name": ""},
        {"url": "https://example.test/signature.asc", "name": ""},
    ]
    assert artifact_signature(url, arbitrary) == arbitrary[1]["url"]
    duplicate = [*named, {"url": "https://example.test/download/125", "name": "patches.rvp.asc"}]
    assert artifact_signature(named[0]["url"], duplicate) is None


@pytest.mark.parametrize(
    "date",
    [
        "2026-10-09T00:00:00.123456Z",
        "2026-10-09T01:00:00.987+01:00",
    ],
)
@pytest.mark.parametrize("extension", ["rvp", "mpp", "jar"])
def test_extensionless_assets_survive_discovery_history_and_restore(
    tmp_path, monkeypatch, extension, date
):
    fixture(tmp_path, verified=False)
    inventory = db.read_json(tmp_path / "config/sources.json")
    release = {
        "tag_name": "v5",
        "prerelease": False,
        "published_at": date,
        "assets": {
            "links": [
                {"name": "patches." + extension, "direct_asset_url": "https://example.test/123"},
                {"name": "patches." + extension + ".asc", "url": "https://example.test/124"},
            ]
        },
    }
    monkeypatch.setattr(discovery, "RELEASE_REQUESTS", {})
    monkeypatch.setattr(discovery, "RELEASE_CACHE", {})
    monkeypatch.setattr(discovery, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(discovery, "PATCH_BUNDLES_DIR", tmp_path / "internal/cache/bundles")
    monkeypatch.setattr(discovery, "BUNDLE_METADATA", {})
    monkeypatch.setattr(discovery, "DISCOVERY_STATUS", {})
    monkeypatch.setattr(discovery, "DISABLED_ALIASES", set())

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json=[release]))
        ) as client:
            assert await discovery.fetch_release_data(
                client, "demo-stable", inventory["demo-stable"]
            )

    asyncio.run(run())
    save_history(tmp_path, inventory, {"https://github.com/owner/demo": [release]})
    manifest = db.build_database(tmp_path, restore=False)
    _, bundles = snapshot(tmp_path, manifest)
    current = next(row for row in bundles if row["version"] == "v5")
    assert "stable" in current["channels"]
    assert (
        current["bundle_type"]
        == {"rvp": "ReVanced:V4", "mpp": "Morphe:V1", "jar": "ReVanced:V3"}[extension]
    )
    assert current["signature_download_url"] == "https://example.test/124"
    assert current["created_at"] == release["published_at"]
    raw_path = (
        tmp_path / "internal/cache/bundles/demo-patch-bundles/demo-stable-patches-bundle.json"
    )
    raw_path.unlink()
    db.restore_catalog_cache(tmp_path)
    restored = json.loads(raw_path.read_text())
    assert restored["bundle_type"] == current["bundle_type"]
    assert restored["created_at"] == date
    regenerated = next(
        row
        for row in snapshot(tmp_path, db.build_database(tmp_path))[1]
        if row["id"] == current["id"]
    )
    assert regenerated["bundle_type"] == current["bundle_type"]
    assert regenerated["created_at"] == date


def test_latest_flags_rank_history_separately_without_changing_channel_pointers(tmp_path):
    fixture(tmp_path)
    inventory = db.read_json(tmp_path / "config/sources.json")
    save_history(
        tmp_path,
        inventory,
        {
            "https://github.com/owner/demo": [
                {
                    "tag_name": "v2",
                    "published_at": "2026-01-03T00:00:00Z",
                    "assets": [{"browser_download_url": "https://example.test/v2.rvp"}],
                },
                {
                    "tag_name": "v3-dev",
                    "published_at": "2026-01-04T00:00:00Z",
                    "prerelease": True,
                    "assets": [{"browser_download_url": "https://example.test/v3.mpp"}],
                },
            ]
        },
    )
    _, bundles = snapshot(tmp_path, db.build_database(tmp_path))
    assert {row["version"] for row in bundles if row["is_latest"]} == {"v2", "v3-dev"}
    assert next(row for row in bundles if row["version"] == "v1")["channels"] == [
        "latest",
        "stable",
    ]


def test_statistics_use_the_same_collation_as_text_ranges(tmp_path):
    from scripts.catalog_statistics import patch_statistics

    rows = [
        {"id": str(i), "legacy_id": i, "bundle_id": "bundle", "name": name}
        for i, name in enumerate(["a", "Z", "AAAD Premium"], 1)
    ]
    result = patch_statistics(rows, {"bundle": {"legacy_id": 1}})
    assert result["aggregate"]["min"]["name"] == "a"
    assert result["aggregate"]["max"]["name"] == "Z"
    assert text_key("a") < text_key("AAAD Premium") < text_key("b")
    assert text_key("Z", "C") < text_key("a", "C")
    assert text_key("\U0001f600", "C") < text_key("\U0001f601", "C")


def test_collation_matches_native_strcoll_backward_runs_and_combining_marks():
    # Native strcoll with the pinned glibc 2.36 LC_COLLATE data; strxfrm
    # produces a different order for backward runs followed by letters.
    expected = [
        "00_a",
        "00a",
        "0!a",
        "0_a",
        "0_a_",
        "0_A",
        "0..a.",
        "0._a",
        "0a",
        "0a ",
        "0\u0301_a",
        "0_\u0301a",
        "0\u0306\u0301a",
        "0\u0301\u0306a",
        "a-b",
        "ab",
    ]
    assert sorted(reversed(expected), key=text_key) == expected

    from scripts.catalog_statistics import patch_statistics

    rows = [
        {"id": str(i), "legacy_id": i, "bundle_id": "bundle", "name": name}
        for i, name in enumerate(["0a", "0_a"], 1)
    ]
    result = patch_statistics(rows, {"bundle": {"legacy_id": 1}})
    assert result["aggregate"]["min"]["name"] == "0_a"
    assert result["aggregate"]["max"]["name"] == "0a"


@pytest.mark.parametrize(
    ("names", "expected"),
    [
        (["first.rvp", "second.rvp"], "first.rvp"),
        (["first.rvp", "second.mpp"], "first.rvp"),
        (["first.mpp", "second.rvp"], "first.mpp"),
        (["first.jar", "second.rvp"], "second.rvp"),
        (["first.jar", "second.jar"], "first.jar"),
    ],
)
def test_multi_asset_selection_agrees_across_current_history_and_catalog(
    tmp_path, monkeypatch, names, expected
):
    fixture(tmp_path, verified=False)
    inventory = db.read_json(tmp_path / "config/sources.json")
    release = {
        "tag_name": "v5",
        "prerelease": False,
        "published_at": "2026-10-09T00:00:00Z",
        "assets": [
            {"browser_download_url": "https://example.test/" + name}
            for name in [*names, expected + ".asc"]
        ],
    }
    monkeypatch.setattr(discovery, "RELEASE_REQUESTS", {})
    monkeypatch.setattr(discovery, "RELEASE_CACHE", {})
    monkeypatch.setattr(discovery, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(discovery, "PATCH_BUNDLES_DIR", tmp_path / "internal/cache/bundles")
    monkeypatch.setattr(discovery, "BUNDLE_METADATA", {})
    monkeypatch.setattr(discovery, "DISCOVERY_STATUS", {})
    monkeypatch.setattr(discovery, "DISABLED_ALIASES", set())

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(200, json=[release]))
        ) as client:
            assert await discovery.fetch_release_data(
                client, "demo-stable", inventory["demo-stable"]
            )

    asyncio.run(run())
    registry = save_history(tmp_path, inventory, {"https://github.com/owner/demo": [release]})
    assert len(registry) == 1
    raw = db.read_json(tmp_path / next(iter(registry.values()))["cache_path"])
    assert (raw.get("download_url") or raw["patches"]["url"]) == "https://example.test/" + expected
    _, bundles = snapshot(tmp_path, db.build_database(tmp_path, restore=False))
    selected = [row for row in bundles if row["version"] == "v5"]
    assert len(selected) == 1
    assert selected[0]["download_url"] == "https://example.test/" + expected
    assert selected[0]["signature_download_url"] == "https://example.test/" + expected + ".asc"
    assert selected[0]["is_latest"]


def test_history_replaces_previous_asset_input_but_preserves_published_versions(tmp_path):
    fixture(tmp_path, verified=False)
    inventory = db.read_json(tmp_path / "config/sources.json")
    release = {
        "tag_name": "v5",
        "published_at": "2026-10-09T00:00:00Z",
        "assets": [{"browser_download_url": "https://example.test/old.rvp"}],
    }
    releases = {"https://github.com/owner/demo": [release]}
    save_history(tmp_path, inventory, releases)
    db.build_database(tmp_path, restore=False)
    release["assets"] = [
        {"browser_download_url": "https://example.test/new.rvp"},
        {"browser_download_url": "https://example.test/old.rvp"},
    ]
    registry = save_history(tmp_path, inventory, releases)
    assert len(registry) == 1
    raw = db.read_json(tmp_path / next(iter(registry.values()))["cache_path"])
    assert raw["download_url"] == "https://example.test/new.rvp"
    _, bundles = snapshot(tmp_path, db.build_database(tmp_path, restore=False))
    v5 = [row for row in bundles if row["version"] == "v5"]
    assert [row["download_url"] for row in v5] == ["https://example.test/new.rvp"]
    assert [row["download_url"] for row in v5 if row["is_latest"]] == [
        "https://example.test/new.rvp"
    ]


@pytest.mark.parametrize("prerelease", [False, True])
def test_fresh_runner_preserves_selected_asset_and_allows_rediscovery(tmp_path, prerelease):
    original = tmp_path / "original"
    fixture(original, verified=False)
    inventory = db.read_json(original / "config/sources.json")
    source = "https://github.com/owner/demo"

    def history_key(url):
        value = json.dumps([source, "v5", url], separators=(",", ":"))
        return hashlib.sha256(value.encode()).hexdigest()

    # Put the obsolete asset first in restored hash order to expose tie bugs.
    urls = sorted((f"https://example.test/bundle{i}.rvp" for i in range(10)), key=history_key)
    old, selected = urls[0], urls[-1]
    release = {
        "tag_name": "v5",
        "published_at": "2026-10-09T00:00:00Z",
        "prerelease": prerelease,
        "assets": [{"browser_download_url": old}],
    }
    releases = {source: [release]}
    save_history(original, inventory, releases)
    db.build_database(original, restore=False)
    release["assets"] = [{"browser_download_url": url} for url in (selected, old)]
    save_history(original, inventory, releases)
    db.build_database(original, restore=False)

    fresh = tmp_path / "fresh"
    for directory in ("config", "database"):
        shutil.copytree(original / directory, fresh / directory)
    _, bundles = snapshot(fresh, db.build_database(fresh))
    v5 = [row for row in bundles if row["version"] == "v5"]
    assert {row["download_url"] for row in v5} == {selected}
    assert [row["download_url"] for row in v5 if row["is_latest"]] == [selected]

    # A successful later refresh can choose the previously retained asset again.
    release["assets"].reverse()
    save_history(fresh, inventory, releases)
    _, bundles = snapshot(fresh, db.build_database(fresh, restore=False))
    assert [
        row["download_url"] for row in bundles if row["version"] == "v5" and row["is_latest"]
    ] == [old]


def test_release_dates_follow_provider_semantics():
    earlier_created = {"created_at": "2026-01-01T00:00:00Z", "published_at": "2026-03-01T00:00:00Z"}
    later_created = {"created_at": "2026-02-01T00:00:00Z", "published_at": "2026-02-01T00:00:00Z"}
    assert discovery._release_sort_time(earlier_created) < discovery._release_sort_time(
        later_created
    )
    assert discovery._release_time(earlier_created) == earlier_created["created_at"]
    gitlab = {**earlier_created, "released_at": "2026-04-01T00:00:00Z"}
    assert discovery._release_time(gitlab) == gitlab["released_at"]
