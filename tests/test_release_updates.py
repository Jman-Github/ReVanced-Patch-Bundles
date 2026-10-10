"""Release updates retain identity while refreshing provider state."""

import importlib.util
import shutil
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest
from test_generate_database import db, fixture, snapshot, write

from scripts.release_assets import digest_matches, release_assets
from scripts.release_history import save_history
from scripts.source_policy import (
    PERMANENT_STATUS,
    save_availability,
    source_availability,
    write_extraction_policy,
)


def metadata_module():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "release_update_metadata",
        Path(__file__).resolve().parents[1] / "scripts/refresh_source_metadata.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_replacement_preserves_public_and_numeric_ids(tmp_path):
    folder = fixture(tmp_path)
    _, original = snapshot(tmp_path, db.build_database(tmp_path))
    original = original[0]
    for channel in ("latest", "stable"):
        path = folder / f"demo-{channel}-patches-bundle.json"
        raw = db.read_json(path)
        raw["download_url"] = "https://example.test/replacement.rvp"
        write(path, raw)
    _, rows = snapshot(tmp_path, db.build_database(tmp_path, restore=False))
    assert len(rows) == 1
    assert (rows[0]["id"], rows[0]["legacy_id"]) == (original["id"], original["legacy_id"])
    assert rows[0]["download_url"].endswith("/replacement.rvp")
    assert rows[0]["need_patches_update"]
    assert rows[0]["metadata_status"] != "verified"


def test_provider_digest_invalidates_historical_proof_and_survives_restore(tmp_path):
    root = tmp_path / "original"
    fixture(root)
    inventory = db.read_json(root / "config/sources.json")
    release = {
        "tag_name": "v0",
        "created_at": "2025-01-01T00:00:00Z",
        "assets": [
            {
                "browser_download_url": "https://example.test/history.rvp",
                "digest": "sha256:" + "a" * 64,
            }
        ],
    }
    registry = save_history(root, inventory, {"https://github.com/owner/demo": [release]})
    key, settings = next(iter(registry.items()))
    folder = (root / settings["cache_path"]).parent
    patches = folder / f"{key}-patches-list.json"
    write(
        patches,
        {
            "version": "v0",
            "patches": [{"name": "Old patch"}],
            "metadata_schema_version": db.PATCH_METADATA_SCHEMA_VERSION,
        },
    )
    write(
        folder / f"{key}-extraction.json",
        {
            "version": "v0",
            "download_url": release["assets"][0]["browser_download_url"],
            "status": "verified",
            "file_hash": "a" * 64,
            "patch_list_hash": db.digest(patches.read_bytes()),
        },
    )
    _, rows = snapshot(root, db.build_database(root, restore=False))
    old = next(row for row in rows if row["version"] == "v0")
    assert old["metadata_status"] == "verified"
    release["assets"][0]["digest"] = "sha256:" + "b" * 64
    save_history(root, inventory, {"https://github.com/owner/demo": [release]})
    _, rows = snapshot(root, db.build_database(root, restore=False))
    changed = next(row for row in rows if row["version"] == "v0")
    assert changed["id"] == old["id"]
    assert changed["need_patches_update"]
    assert changed["metadata_status"] != "verified"
    fresh = tmp_path / "fresh"
    for directory in ("config", "database"):
        shutil.copytree(root / directory, fresh / directory)
    _, restored = snapshot(fresh, db.build_database(fresh))
    row = next(row for row in restored if row["version"] == "v0")
    assert row["provider_digest"] == "sha256:" + "b" * 64
    assert row["need_patches_update"]
    assert row["id"] == old["id"]


def test_provider_digests_are_retained_and_compared():
    asset = release_assets(
        {"assets": [{"url": "https://example.test/a.rvp", "digest": "SHA256:" + "A" * 64}]}
    )[0]
    assert digest_matches(asset["provider_digest"], "a" * 64)
    assert not digest_matches(asset["provider_digest"], "b" * 64)
    assert not digest_matches("opaque-new", "a" * 64, "opaque-old")
    assert digest_matches("opaque-new", "a" * 64, "opaque-new")


@pytest.mark.parametrize("code", [404, 410, 451])
def test_permanent_repository_errors_publish_reason_without_disabling(tmp_path, code):
    fixture(tmp_path)
    module = metadata_module()
    with httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(code))
    ) as client:
        module.refresh(tmp_path, client)
    assert source_availability(tmp_path)["https://github.com/owner/demo"] == PERMANENT_STATUS[code]
    folders = write_extraction_policy(tmp_path)
    assert "demo-patch-bundles" in folders
    path, rows = snapshot(tmp_path, db.build_database(tmp_path, restore=False))
    source = next(row for row in db.read_json(path / "sources.json") if row["repo"] == "demo")
    assert source["enabled"]
    assert source["unavailable_reason"] == PERMANENT_STATUS[code]
    assert rows


def test_availability_clears_only_after_metadata_and_release_recovery(tmp_path):
    fixture(tmp_path)
    url = "https://github.com/owner/demo"
    save_availability(tmp_path, {url: PERMANENT_STATUS[404]})
    module = metadata_module()
    now = datetime(2026, 10, 9, tzinfo=UTC)
    with httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={}))
    ) as client:
        module.refresh(tmp_path, client, now=now)
    assert source_availability(tmp_path)[url] == PERMANENT_STATUS[404]
    write(tmp_path / "internal/cache/release-checks.json", {url: True})
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(503))) as client:
        module.refresh(tmp_path, client, now=now)
    assert source_availability(tmp_path)[url] == PERMANENT_STATUS[404]
    with httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={}))
    ) as client:
        module.refresh(tmp_path, client, now=now)
    assert url not in source_availability(tmp_path)
    assert "demo-patch-bundles" not in write_extraction_policy(tmp_path)


def test_job_history_retains_older_phase_ids_across_fresh_runners(tmp_path):
    fixture(tmp_path)
    jobs = [
        {
            "job_id": str(uuid.uuid5(uuid.NAMESPACE_URL, str(i))),
            "job_type": "PATCHES",
            "status": "COMPLETED",
            "started_at": "2026-01-01T00:00:00Z",
            "completed_at": "2026-01-01T00:01:00Z",
            "error": None,
        }
        for i in range(130)
    ]
    write(tmp_path / "internal/cache/refresh-jobs.json", jobs)
    path, _ = snapshot(tmp_path, db.build_database(tmp_path))
    published = db.read_json(path / "refresh-jobs.json")
    assert len(published) == 130
    oldest = next(row for row in published if row["job_id"] == jobs[0]["job_id"])
    write(tmp_path / "internal/cache/refresh-jobs.json", [])
    path, _ = snapshot(tmp_path, db.build_database(tmp_path))
    assert (
        next(
            row
            for row in db.read_json(path / "refresh-jobs.json")
            if row["job_id"] == oldest["job_id"]
        )
        == oldest
    )


def test_restored_channel_status_does_not_clear_an_unavailable_reason(tmp_path):
    fixture(tmp_path)
    url = "https://github.com/owner/demo"
    save_availability(tmp_path, {url: PERMANENT_STATUS[404]})
    write(tmp_path / "internal/cache/bundles/discovery-status.json", {"demo-latest": "available"})
    module = metadata_module()
    with httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={}))
    ) as client:
        module.refresh(tmp_path, client)
    assert source_availability(tmp_path)[url] == PERMANENT_STATUS[404]


def test_failed_new_binary_does_not_inherit_old_historical_proof(tmp_path):
    folder = fixture(tmp_path)
    inventory = db.read_json(tmp_path / "config/sources.json")
    release = {
        "tag_name": "v1",
        "created_at": "2026-01-01T00:00:00Z",
        "assets": [{"browser_download_url": "https://example.test/demo.rvp"}],
    }
    registry = save_history(tmp_path, inventory, {"https://github.com/owner/demo": [release]})
    key, item = next(iter(registry.items()))
    historical = (tmp_path / item["cache_path"]).parent
    patches = historical / f"{key}-patches-list.json"
    write(patches, {"version": "v1", "patches": [{"name": "Old binary patch"}]})
    write(
        historical / f"{key}-extraction.json",
        {
            "version": "v1",
            "download_url": release["assets"][0]["browser_download_url"],
            "status": "verified",
            "file_hash": "a" * 64,
            "attempted_at": "2026-01-01T00:00:00Z",
            "patch_list_hash": db.digest(patches.read_bytes()),
        },
    )
    _, original = snapshot(tmp_path, db.build_database(tmp_path, restore=False))
    for channel in ("latest", "stable"):
        path = folder / f"demo-{channel}-extraction.json"
        status = db.read_json(path)
        status.update(
            status="runtime_parsing_failure",
            file_hash="b" * 64,
            attempted_at="2026-01-02T00:00:00Z",
            patch_list_hash=None,
        )
        write(path, status)
    for _ in range(2):
        _, rows = snapshot(tmp_path, db.build_database(tmp_path, restore=False))
        assert len(rows) == 1
        assert rows[0]["id"] == original[0]["id"]
        assert rows[0]["file_hash"] == "b" * 64
        assert rows[0]["need_patches_update"]
        assert rows[0]["metadata_status"] != "verified"


def test_newer_historical_extraction_supersedes_a_channel_binary_observation(tmp_path):
    folder = fixture(tmp_path)
    registry = save_history(
        tmp_path,
        db.read_json(tmp_path / "config/sources.json"),
        {
            "https://github.com/owner/demo": [
                {
                    "tag_name": "v1",
                    "created_at": "2026-01-01T00:00:00Z",
                    "assets": [{"browser_download_url": "https://example.test/demo.rvp"}],
                }
            ],
        },
    )
    key, item = next(iter(registry.items()))
    historical = (tmp_path / item["cache_path"]).parent
    patches = historical / f"{key}-patches-list.json"
    write(
        patches,
        {
            "version": "v1",
            "patches": [{"name": "New binary patch"}],
            "metadata_schema_version": db.PATCH_METADATA_SCHEMA_VERSION,
        },
    )
    write(
        historical / f"{key}-extraction.json",
        {
            "version": "v1",
            "download_url": "https://example.test/demo.rvp",
            "status": "verified",
            "file_hash": "b" * 64,
            "attempted_at": "2026-01-02T00:00:00Z",
            "patch_list_hash": db.digest(patches.read_bytes()),
        },
    )
    for channel in ("latest", "stable"):
        path = folder / f"demo-{channel}-extraction.json"
        status = db.read_json(path)
        status["attempted_at"] = "2026-01-01T00:00:00Z"
        write(path, status)
    _, rows = snapshot(tmp_path, db.build_database(tmp_path, restore=False))
    assert rows[0]["file_hash"] == "b" * 64
    assert rows[0]["metadata_status"] == "verified"


def test_current_cache_restore_preserves_binary_observation_time(tmp_path):
    folder = fixture(tmp_path)
    for channel in ("latest", "stable"):
        path = folder / f"demo-{channel}-extraction.json"
        value = db.read_json(path)
        value["attempted_at"] = "2026-01-02T00:00:00Z"
        write(path, value)
    db.build_database(tmp_path, restore=False)
    # Keep the history cache while restoring a missing current-channel cache.
    shutil.rmtree(folder)
    db.restore_catalog_cache(tmp_path)
    status = db.read_json(folder / "demo-latest-extraction.json")
    assert status["attempted_at"] == "2026-01-02T00:00:00Z"


@pytest.mark.parametrize("has_integration", [False, True])
@pytest.mark.parametrize("shared_identity", [False, True])
def test_historical_extraction_keeps_current_legacy_integration_metadata(
    tmp_path, has_integration, shared_identity
):
    original = fixture(tmp_path, verified=False)
    # Visit history before current channels to exercise identity coalescing.
    inventory = db.read_json(tmp_path / "config/sources.json")
    write(
        tmp_path / "config/sources.json",
        {key.replace("demo-", "zzdemo-"): value for key, value in inventory.items()},
    )
    folder = original.with_name("zzdemo-patch-bundles")
    original.rename(folder)
    integrations = (
        {"version": "v1", "url": "https://example.test/integrations.apk"}
        if has_integration
        else None
    )
    for channel in ("latest", "stable"):
        write(
            folder / f"zzdemo-{channel}-patches-bundle.json",
            {
                "patches": {"version": "v1", "url": "https://example.test/patches.jar"},
                "integrations": integrations,
                "bundle_type": "ReVanced:V3",
            },
        )
    registry = save_history(
        tmp_path,
        db.read_json(tmp_path / "config/sources.json"),
        {
            "https://github.com/owner/demo": [
                {
                    "tag_name": "v1",
                    "created_at": "2026-01-01T00:00:00Z",
                    "assets": [{"browser_download_url": "https://example.test/patches.jar"}],
                }
            ],
        },
    )
    key, item = next(iter(registry.items()))
    historical = (tmp_path / item["cache_path"]).parent
    # An older channel configuration must not bring back removed integrations.
    raw = db.read_json(tmp_path / item["cache_path"])
    raw["integrations"] = {"version": "v0", "url": "https://example.test/old.apk"}
    write(tmp_path / item["cache_path"], raw)
    patches = historical / f"{key}-patches-list.json"
    write(
        patches,
        {
            "version": "v1",
            "metadata_schema_version": db.PATCH_METADATA_SCHEMA_VERSION,
            "patches": [{"name": "Legacy patch"}],
        },
    )
    write(
        historical / f"{key}-extraction.json",
        {
            "version": "v1",
            "download_url": "https://example.test/patches.jar",
            "status": "verified",
            "file_hash": "a" * 64,
            "patch_list_hash": db.digest(patches.read_bytes()),
        },
    )
    if shared_identity:
        for channel in ("latest", "stable"):
            current_patches = folder / f"zzdemo-{channel}-patches-list.json"
            shutil.copyfile(patches, current_patches)
            shutil.copyfile(
                historical / f"{key}-extraction.json",
                folder / f"zzdemo-{channel}-extraction.json",
            )
    _, rows = snapshot(tmp_path, db.build_database(tmp_path, restore=False))
    assert rows[0]["metadata_status"] == "verified"
    assert rows[0]["integrations"] == integrations


@pytest.mark.parametrize("digest", [None, "sha256:" + "a" * 64])
@pytest.mark.parametrize("legacy", [False, True])
def test_generated_provider_digest_is_accepted_by_bundle_schema(tmp_path, digest, legacy):
    from scripts.validate_json import BUNDLE_VALIDATOR

    fixture(tmp_path)
    registry = save_history(
        tmp_path,
        db.read_json(tmp_path / "config/sources.json"),
        {
            "https://github.com/owner/demo": [
                {
                    "tag_name": "v0",
                    "created_at": "2025-01-01T00:00:00Z",
                    "assets": [
                        {
                            "browser_download_url": "https://example.test/history."
                            + ("jar" if legacy else "rvp"),
                            "digest": digest,
                        }
                    ],
                }
            ],
        },
    )
    raw = db.read_json(tmp_path / next(iter(registry.values()))["cache_path"])
    assert raw["provider_digest"] == digest
    assert not list(BUNDLE_VALIDATOR.iter_errors(raw))
