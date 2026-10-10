import importlib.util
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "database_builder", Path(__file__).resolve().parents[1] / "scripts/generate_database.py"
)
db = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(db)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(db.encoded(value))


def fixture(root, verified=True, metadata_schema_version=db.PATCH_METADATA_SCHEMA_VERSION):
    write(
        root / "config/site.json",
        {
            "website": "https://example.test",
            "api": "https://api.example.test",
            "repository": "owner/catalog",
            "data_branch": "bundles",
            "page_size": 2,
        },
    )
    write(
        root / "config/sources.json",
        {
            "demo-latest": {"patches": "https://api.github.com/repos/owner/demo", "latest": True},
            "demo-stable": {"patches": "https://github.com/owner/demo"},
            "empty-dev": {
                "patches": "https://gitlab.com/api/v4/projects/team%2Fempty",
                "prerelease": True,
            },
        },
    )
    folder = root / "internal/cache/bundles/demo-patch-bundles"
    patches = [
        {
            "name": "Hide ads",
            "description": "Remove video ads",
            "use": True,
            "compatiblePackages": {"com.video": ["1.0", "2.0"]},
            "dependencies": [],
            "options": [],
        }
    ]
    for channel in ("latest", "stable"):
        write(
            folder / f"demo-{channel}-patches-bundle.json",
            {
                "version": "v1",
                "download_url": "https://example.test/demo.rvp",
                "description": "Release notes",
                "created_at": "2026-01-01T00:00:00",
            },
        )
        patch_path = folder / f"demo-{channel}-patches-list.json"
        write(
            patch_path,
            {
                "version": "v1",
                "patches": patches,
                "metadata_schema_version": metadata_schema_version,
            },
        )
        if verified:
            write(
                folder / f"demo-{channel}-extraction.json",
                {
                    "status": "verified",
                    "version": "v1",
                    "download_url": "https://example.test/demo.rvp",
                    "file_hash": "a" * 64,
                    "runtime": "app.revanced:patcher:22.0.1",
                    "patch_list_hash": db.digest(patch_path.read_bytes()),
                },
            )
    return folder


def snapshot(root, manifest):
    path = root / "database" / manifest["snapshot"]
    return path, db.read_json(path / "bundles.json")


def test_verified_artifact_deduplicates_channels_and_indexes_packages(tmp_path):
    fixture(tmp_path)
    manifest = db.build_database(tmp_path)
    path, bundles = snapshot(tmp_path, manifest)
    assert len(bundles) == 1
    assert bundles[0]["channels"] == ["latest", "stable"]
    assert bundles[0]["metadata_status"] == "verified"
    assert bundles[0]["extraction_status"] == "verified"
    assert bundles[0]["patcher_runtime"] == "app.revanced:patcher:22.0.1"
    assert not bundles[0]["need_patches_update"]
    index = db.read_json(path / "patch-index.json")
    assert index["packages"]["com.video"] == index["pages"]
    assert db.read_json(path / "packages.json")[0]["versions"] == ["1.0", "2.0"]
    assert len(db.read_json(path / "availability.json")["missing"]) == 1


def test_generation_is_deterministic_and_old_snapshots_survive(tmp_path):
    folder = fixture(tmp_path)
    first = db.build_database(tmp_path)
    assert db.build_database(tmp_path) == first
    raw = db.read_json(folder / "demo-latest-patches-bundle.json")
    raw.update(version="v2", download_url="https://example.test/v2.rvp")
    write(folder / "demo-latest-patches-bundle.json", raw)
    second = db.build_database(tmp_path)
    assert second["generation"] != first["generation"]
    assert (tmp_path / "database" / first["snapshot"] / "bundles.json").is_file()
    _, bundles = snapshot(tmp_path, second)
    stale = next(b for b in bundles if b["version"] == "v2")
    assert stale["metadata_status"] == "stale" and stale["patch_count"] == 0
    assert stale["file_hash"] is None
    assert stale["patcher_runtime"] is None
    assert stale["extraction_status"] == "unverified"


def test_replaced_artifact_does_not_inherit_previous_extraction(tmp_path):
    folder = fixture(tmp_path)
    raw_path = folder / "demo-latest-patches-bundle.json"
    raw = db.read_json(raw_path)
    raw["download_url"] = "https://example.test/replaced.rvp"
    write(raw_path, raw)
    _, bundles = snapshot(tmp_path, db.build_database(tmp_path))
    replaced = next(b for b in bundles if b["download_url"] == raw["download_url"])
    assert replaced["metadata_status"] == "unverified"
    assert replaced["file_hash"] is None
    assert replaced["patcher_runtime"] is None
    assert replaced["extraction_status"] == "unverified"


def test_same_version_artifact_failure_revokes_freshness(tmp_path):
    folder = fixture(tmp_path)
    for channel in ("latest", "stable"):
        path = folder / f"demo-{channel}-extraction.json"
        record = db.read_json(path)
        record["status"] = "runtime_parsing_failure"
        write(path, record)
    manifest = db.build_database(tmp_path)
    path, bundles = snapshot(tmp_path, manifest)
    assert bundles[0]["metadata_status"] == "unverified"
    assert bundles[0]["need_patches_update"]
    assert db.read_json(path / "patches/00000.json")[0]["metadata_status"] == "unverified"


def test_patch_list_digest_mismatch_cannot_be_verified(tmp_path):
    folder = fixture(tmp_path)
    for channel in ("latest", "stable"):
        path = folder / f"demo-{channel}-patches-list.json"
        patches = db.read_json(path)
        patches["patches"][0]["description"] = "Changed independently"
        write(path, patches)
    _, bundles = snapshot(tmp_path, db.build_database(tmp_path))
    assert bundles[0]["metadata_status"] == "unverified"


def test_inventory_is_authoritative_and_orphans_are_not_exposed(tmp_path):
    folder = fixture(tmp_path)
    write(
        folder / "orphan-latest-patches-bundle.json",
        {"version": "v42", "download_url": "https://example.test/orphan.rvp"},
    )
    db.build_database(tmp_path)
    write(
        tmp_path / "config/sources.json",
        {
            "empty-dev": {
                "patches": "https://gitlab.com/api/v4/projects/team%2Fempty",
                "prerelease": True,
            }
        },
    )
    _, bundles = snapshot(tmp_path, db.build_database(tmp_path))
    assert bundles == []


def test_discovery_no_release_does_not_expose_old_file_as_current(tmp_path):
    fixture(tmp_path)
    write(
        tmp_path / "internal/cache/bundles/discovery-status.json",
        {"demo-latest": "no_matching_release", "demo-stable": "no_matching_release"},
    )
    _, bundles = snapshot(tmp_path, db.build_database(tmp_path))
    assert bundles == []


def test_old_lists_are_explicitly_unverified(tmp_path):
    fixture(tmp_path, verified=False)
    path, bundles = snapshot(tmp_path, db.build_database(tmp_path))
    assert bundles[0]["metadata_status"] == "unverified"
    assert bundles[0]["file_hash"] is None
    assert db.read_json(path / "patches/00000.json")[0]["metadata_status"] == "unverified"


def test_gitlab_nested_group_and_api_urls():
    assert db.normalize_source("https://gitlab.com/api/v4/projects/group%2Fteam%2Frepo") == (
        "https://gitlab.com/group/team/repo"
    )
    assert db.normalize_source("github.com/Owner/Repo.git/") == "https://github.com/Owner/Repo"


def test_malformed_compatibility_does_not_break_unrelated_records():
    assert db.packages_for({"compatiblePackages": 42}) == []
    assert db.packages_for({"compatiblePackages": {"com.video": "1.0"}}) == [
        {"name": "com.video", "versions": ["1.0"]}
    ]
    assert db.packages_for(
        {"compatiblePackages": [{"name": "com.video", "targets": [None, {"version": "2.0"}]}]}
    ) == [{"name": "com.video", "versions": ["2.0"]}]


def test_invalid_sidecar_shapes_remain_unverified(tmp_path):
    folder = fixture(tmp_path)
    for channel in ("latest", "stable"):
        write(folder / f"demo-{channel}-extraction.json", [])
    _, bundles = snapshot(tmp_path, db.build_database(tmp_path))
    assert bundles[0]["metadata_status"] == "unverified"


def test_latest_only_prerelease_survives_rebuild_without_run_metadata(tmp_path):
    fixture(tmp_path, verified=False)
    inventory_path = tmp_path / "config/sources.json"
    inventory = db.read_json(inventory_path)
    del inventory["demo-stable"]
    write(inventory_path, inventory)
    run_path = tmp_path / "internal/cache/bundle-run-metadata.json"
    release_url = "https://github.com/owner/demo/releases/tag/v1"
    write(
        run_path,
        {
            "bundles": {
                "demo-latest": {
                    "is_prerelease": True,
                    "patches": {"release_url": release_url},
                }
            }
        },
    )
    first = db.build_database(tmp_path)
    _, bundles = snapshot(tmp_path, first)
    assert bundles[0]["is_prerelease"] is True

    run_path.unlink()
    second = db.build_database(tmp_path)
    _, bundles = snapshot(tmp_path, second)
    assert bundles[0]["is_prerelease"] is True
    assert bundles[0]["release_url"] == release_url
    assert first == second

    write(run_path, {"bundles": {"demo-latest": {"is_prerelease": False}}})
    _, bundles = snapshot(tmp_path, db.build_database(tmp_path))
    assert bundles[0]["is_prerelease"] is False


def test_fresh_checkout_restores_current_channels_and_proof_from_snapshot(tmp_path):
    import shutil

    fixture(tmp_path)
    first = db.build_database(tmp_path)
    shutil.rmtree(tmp_path / "internal/cache")
    second = db.build_database(tmp_path)
    assert second == first
    _, bundles = snapshot(tmp_path, second)
    assert bundles[0]["channels"] == ["latest", "stable"]
    assert bundles[0]["metadata_status"] == "verified"
    assert bundles[0]["patch_count"] == 1
    assert all(
        url.startswith("https://api.example.test/api/v3/bundle?")
        for url in bundles[0]["import_urls"].values()
    )


def test_fresh_checkout_preserves_legacy_integrations(tmp_path):
    import shutil

    folder = fixture(tmp_path)
    integration = {"version": "v5", "url": "https://example.test/integrations.apk"}
    for channel in ("latest", "stable"):
        write(
            folder / f"demo-{channel}-patches-bundle.json",
            {
                "patches": {"version": "v1", "url": "https://example.test/demo.jar"},
                "integrations": integration,
            },
        )
    first = db.build_database(tmp_path)
    shutil.rmtree(tmp_path / "internal/cache")
    assert db.build_database(tmp_path) == first
    restored = db.read_json(folder / "demo-latest-patches-bundle.json")
    assert restored["integrations"] == integration


def test_snapshot_restore_preserves_new_discovery_results(tmp_path):
    import shutil

    for status in ("no_matching_release", "upstream_unavailable"):
        root = tmp_path / status
        fixture(root)
        db.build_database(root)
        shutil.rmtree(root / "internal/cache")
        write(
            root / "internal/cache/bundles/discovery-status.json",
            {
                "demo-latest": status,
                "demo-stable": status,
            },
        )
        path, bundles = snapshot(root, db.build_database(root))
        if status == "no_matching_release":
            assert all(bundle["channels"] == [] for bundle in bundles)
            unavailable = db.read_json(path / "availability.json")["missing"]
            assert len([row for row in unavailable if row["reason"] == "no_release"]) == 2
        else:
            assert bundles[0]["channels"] == ["latest", "stable"]
            assert bundles[0]["release_status"] == status


def test_fresh_checkout_preserves_known_missing_channels(tmp_path):
    import shutil

    fixture(tmp_path)
    write(
        tmp_path / "internal/cache/bundles/discovery-status.json",
        {
            "empty-dev": "no_matching_release",
        },
    )
    first = db.build_database(tmp_path)
    shutil.rmtree(tmp_path / "internal/cache")
    assert db.build_database(tmp_path) == first


def test_pruning_generations_preserves_all_known_release_versions(tmp_path, monkeypatch):
    from scripts import snapshot_retention

    monkeypatch.setattr(snapshot_retention, "MAX_SNAPSHOT_GENERATIONS", 2)
    folder = fixture(tmp_path)
    first = db.build_database(tmp_path)
    for version in ("v2", "v3", "v4"):
        for channel in ("latest", "stable"):
            path = folder / f"demo-{channel}-patches-bundle.json"
            raw = db.read_json(path)
            raw.update(version=version, download_url=f"https://example.test/{version}.rvp")
            write(path, raw)
        current = db.build_database(tmp_path)
    assert not (tmp_path / "database" / first["snapshot"]).exists()
    assert len(list((tmp_path / "database/snapshots").iterdir())) == 2
    _, bundles = snapshot(tmp_path, current)
    assert {bundle["version"] for bundle in bundles} == {"v1", "v2", "v3", "v4"}


def test_oversized_generation_keeps_published_manifest(tmp_path, monkeypatch):
    import pytest

    from scripts import snapshot_retention

    folder = fixture(tmp_path)
    first = db.build_database(tmp_path)
    raw_path = folder / "demo-latest-patches-bundle.json"
    raw = db.read_json(raw_path)
    raw.update(version="v2", download_url="https://example.test/v2.rvp")
    write(raw_path, raw)
    monkeypatch.setattr(snapshot_retention, "MAX_SNAPSHOT_BYTES", 1)
    with pytest.raises(ValueError, match="publication budget"):
        db.build_database(tmp_path)
    assert db.read_json(tmp_path / "database/manifest.json") == first


def test_site_publishes_retained_catalog_files_without_private_build_data(tmp_path):
    fixture(tmp_path)
    (tmp_path / "web").mkdir()
    (tmp_path / "shared").mkdir()
    (tmp_path / "web/index.html").write_text("Catalog")
    manifest = db.build_database(tmp_path)
    write(tmp_path / "database/repository-metadata.json", {"private": True})
    db.build_site(tmp_path)
    public = tmp_path / "site-dist/database"
    assert db.read_json(public / "manifest.json") == manifest
    assert not (public / "ids.json").exists()
    assert not (public / "repository-metadata.json").exists()
    assert not (public / "snapshot-history.json").exists()
    current = public / manifest["snapshot"]
    assert not (current / "history.json").exists()
    assert all((current / name).is_file() for name in manifest["files"])


def test_bundle_index_retains_full_descriptions_for_api_comparisons(tmp_path):
    folder = fixture(tmp_path)
    description = "Release notes\n" + "a" * 1000 + "\ntail-marker"
    for channel in ("latest", "stable"):
        path = folder / f"demo-{channel}-patches-bundle.json"
        raw = db.read_json(path)
        write(path, {**raw, "description": description})
    path, bundles = snapshot(tmp_path, db.build_database(tmp_path))
    assert bundles[0]["description"] == description
    assert db.read_json(path / bundles[0]["detail_file"])["description"] == description


def test_unnamed_patches_and_empty_verified_bundles_survive_publication_and_restore(tmp_path):
    from scripts.validate_database import validate

    folder = fixture(tmp_path)
    for entries in (
        [
            {
                "name": None,
                "description": "Unnamed patch",
                "compatiblePackages": {"com.video": ["3.0"]},
            },
            {"description": "No name property"},
            {"name": ""},
        ],
        [],
    ):
        for channel in ("latest", "stable"):
            patch_path = folder / f"demo-{channel}-patches-list.json"
            write(
                patch_path,
                {
                    "version": "v1",
                    "patches": entries,
                    "metadata_schema_version": db.PATCH_METADATA_SCHEMA_VERSION,
                },
            )
            status_path = folder / f"demo-{channel}-extraction.json"
            status = db.read_json(status_path)
            status["patch_list_hash"] = db.digest(patch_path.read_bytes())
            write(status_path, status)
        manifest = db.build_database(tmp_path)
        path, bundles = snapshot(tmp_path, manifest)
        validate(tmp_path)
        assert bundles[0]["metadata_status"] == "verified"
        assert not bundles[0]["need_patches_update"]
        assert bundles[0]["patch_list_available"]
        assert bundles[0]["patch_count"] == len(entries)
        assert manifest["counts"]["patches"] == len(entries)
        stats = db.read_json(path / "patch-statistics.json")
        assert stats["nonnull"]["name"] == (1 if entries else 0)
        for file in folder.iterdir():
            file.unlink()
        db.restore_catalog_cache(tmp_path)
        restored = db.read_json(folder / "demo-latest-patches-list.json")
        assert restored["patches"] == entries
        assert db.read_json(folder / "demo-latest-extraction.json")["status"] == "verified"
        assert (
            snapshot(tmp_path, db.build_database(tmp_path))[1][0]["metadata_status"] == "verified"
        )


def terminal_fixture(root):
    folder = fixture(root, verified=False)
    write(root / "config/patcher-runtimes.json", {"worker": {}, "runtimes": []})
    for channel in ("latest", "stable"):
        write(
            folder / f"demo-{channel}-extraction.json",
            {
                "status": "runtime_parsing_failure",
                "version": "v1",
                "download_url": "https://example.test/demo.rvp",
                "file_hash": "a" * 64,
                "terminal": True,
                "bundle_type": "ReVanced:V4",
                "failure_fingerprint": db.runtime_fingerprint(root),
                "runtime_config_hash": db.runtime_config_hash(root),
                "attempted_at": "2026-10-10T00:00:00Z",
            },
        )
    return folder


def test_terminal_rejection_survives_fresh_runner_restore_without_reporting_verified(tmp_path):
    from scripts.validate_database import validate

    folder = terminal_fixture(tmp_path)
    path, bundles = snapshot(tmp_path, db.build_database(tmp_path))
    bundle = bundles[0]
    assert bundle["extraction_terminal"]
    assert not bundle["need_patches_update"]
    assert bundle["metadata_status"] == "unverified"
    assert bundle["patch_count"] == 0
    validate(tmp_path)
    for file in folder.iterdir():
        file.unlink()
    db.restore_catalog_cache(tmp_path)
    for location in (folder, tmp_path / "internal/cache/history"):
        statuses = [db.read_json(p) for p in location.rglob("*-extraction.json")]
        assert statuses and all(s["terminal"] for s in statuses)
        assert all(s["runtime_config_hash"] == db.runtime_config_hash(tmp_path) for s in statuses)
    assert not snapshot(tmp_path, db.build_database(tmp_path))[1][0]["need_patches_update"]


def test_changed_runtime_configuration_or_availability_requeues_terminal_rejections(tmp_path):
    folder = terminal_fixture(tmp_path)
    db.build_database(tmp_path)
    config = tmp_path / "config/patcher-runtimes.json"
    config.write_bytes(config.read_bytes() + b" ")
    bundle = snapshot(tmp_path, db.build_database(tmp_path))[1][0]
    assert bundle["need_patches_update"] and not bundle["extraction_terminal"]
    # A changed installation manifest is sufficient even when config is identical.
    terminal_fixture(tmp_path)
    write(
        tmp_path / "bundle-parser/build/runtime-classpaths.json",
        {"new-runtime": {"available": True}},
    )
    bundle = snapshot(tmp_path, db.build_database(tmp_path))[1][0]
    assert bundle["need_patches_update"] and not bundle["extraction_terminal"]
    # Transient failures never inherit the permanent-failure pause.
    for channel in ("latest", "stable"):
        status_path = folder / f"demo-{channel}-extraction.json"
        status = db.read_json(status_path)
        status.update(terminal=False, status="runtime_initialization_failure")
        write(status_path, status)
    assert snapshot(tmp_path, db.build_database(tmp_path))[1][0]["need_patches_update"]


def test_replaced_artifact_requeues_terminal_rejection(tmp_path):
    folder = terminal_fixture(tmp_path)
    db.build_database(tmp_path)
    for channel in ("latest", "stable"):
        raw_path = folder / f"demo-{channel}-patches-bundle.json"
        raw = db.read_json(raw_path)
        raw["provider_digest"] = "sha256:" + "b" * 64
        write(raw_path, raw)
    bundle = snapshot(tmp_path, db.build_database(tmp_path, restore=False))[1][0]
    assert bundle["need_patches_update"] and not bundle["extraction_terminal"]


def test_unversioned_empty_placeholder_is_missing_metadata(tmp_path):
    folder = fixture(tmp_path, verified=False)
    for channel in ("latest", "stable"):
        write(folder / f"demo-{channel}-patches-list.json", {"version": None, "patches": []})
    bundle = snapshot(tmp_path, db.build_database(tmp_path))[1][0]
    assert bundle["metadata_status"] == "missing"
    assert not bundle["patch_list_available"] and bundle["need_patches_update"]


def test_newer_rejection_replaces_older_extracted_provider_digest(tmp_path):
    from scripts.validate_database import validate

    folder = terminal_fixture(tmp_path)
    raw = db.read_json(folder / "demo-latest-patches-bundle.json")
    raw["provider_digest"] = "new-provider-digest"
    for channel in ("latest", "stable"):
        write(folder / f"demo-{channel}-patches-bundle.json", raw)
        status_path = folder / f"demo-{channel}-extraction.json"
        status = db.read_json(status_path)
        status.update(provider_digest="new-provider-digest", runtime="test:new-runtime")
        write(status_path, status)
    # Visit an obsolete extraction before the fresh channel extraction, while
    # discovery has already updated both inputs to the same provider digest.
    history = tmp_path / "internal/cache/history/aaa-patch-bundles"
    key = "aaa-stable"
    raw_path = history / f"{key}-patches-bundle.json"
    write(raw_path, raw)
    write(
        history / f"{key}-extraction.json",
        {
            **status,
            "provider_digest": "old-provider-digest",
            "runtime": "test:old-runtime",
            "attempted_at": "2026-10-01T00:00:00Z",
        },
    )
    write(
        tmp_path / "internal/cache/history/sources.json",
        {
            key: {
                "patches": "https://github.com/owner/demo",
                "alias": "demo",
                "historical": True,
                "cache_path": raw_path.relative_to(tmp_path).as_posix(),
            },
        },
    )
    _, bundles = snapshot(tmp_path, db.build_database(tmp_path, restore=False))
    bundle = bundles[0]
    assert bundle["extraction_terminal"] and not bundle["need_patches_update"]
    assert bundle["extracted_provider_digest"] == "new-provider-digest"
    assert bundle["patcher_runtime"] == "test:new-runtime"
    validate(tmp_path)
    # Fresh-runner restoration must retain the newer context as well.
    for file in folder.iterdir():
        file.unlink()
    db.restore_catalog_cache(tmp_path)
    restored = db.read_json(folder / "demo-latest-extraction.json")
    assert restored["terminal"] and restored["provider_digest"] == "new-provider-digest"


def test_valid_fallback_metadata_wins_over_missing_or_stale_history(tmp_path):
    for history_state in ("missing", "stale"):
        for label, entries in (
            ("named", [{"name": "New fallback", "description": "Current metadata"}]),
            ("unnamed", [{"name": None, "description": "Current unnamed metadata"}]),
            ("empty", []),
        ):
            root = tmp_path / history_state / label
            folder = fixture(root, verified=False)
            for channel in ("latest", "stable"):
                write(
                    folder / f"demo-{channel}-patches-list.json",
                    {
                        "version": "v1",
                        "patches": entries,
                    },
                )
            history = root / "internal/cache/history/aaa-patch-bundles"
            key = "aaa-stable"
            raw_path = history / f"{key}-patches-bundle.json"
            write(raw_path, db.read_json(folder / "demo-latest-patches-bundle.json"))
            if history_state == "stale":
                write(
                    history / f"{key}-patches-list.json",
                    {
                        "version": "v0",
                        "patches": [{"name": "Obsolete fallback"}],
                    },
                )
            write(
                root / "internal/cache/history/sources.json",
                {
                    key: {
                        "patches": "https://github.com/owner/demo",
                        "alias": "demo",
                        "historical": True,
                        "cache_path": raw_path.relative_to(root).as_posix(),
                    },
                },
            )
            manifest = db.build_database(root, restore=False)
            path, bundles = snapshot(root, manifest)
            bundle = bundles[0]
            assert bundle["metadata_status"] == "unverified"
            assert bundle["patch_list_available"] and bundle["need_patches_update"]
            assert bundle["patch_metadata_version"] == "v1"
            assert manifest["counts"]["patches"] == len(entries)
            index = db.read_json(path / "patch-index.json")
            rows = [row for page in index["pages"] for row in db.read_json(path / page)]
            assert [row["description"] for row in rows] == [
                entry["description"] for entry in entries
            ]
            for file in folder.iterdir():
                file.unlink()
            db.restore_catalog_cache(root)
            restored = db.read_json(folder / "demo-latest-patches-list.json")
            assert restored["version"] == "v1" and restored["patches"] == entries


def test_empty_compatible_versions_do_not_create_unrestricted_packages(tmp_path):
    from jsonschema import Draft202012Validator

    folder = fixture(tmp_path)
    entries = [
        {"name": "Any version", "compatiblePackages": {"com.any": None}},
        {"name": "No versions", "compatiblePackages": {"com.none": []}},
        {
            "name": "Restricted",
            "compatiblePackages": [{"name": "com.specific", "versions": ["1.0"]}],
        },
        {
            "name": None,
            "description": None,
            "compatiblePackages": [
                {"name": "com.array.any", "versions": None},
                {"name": "com.array.none", "versions": []},
            ],
        },
    ]
    payload = {
        "version": "v1",
        "metadata_schema_version": db.PATCH_METADATA_SCHEMA_VERSION,
        "patches": entries,
    }
    schema = db.read_json(db.ROOT / "schemas/patch_list.schema.json")
    Draft202012Validator(schema).validate(payload)
    for channel in ("latest", "stable"):
        path = folder / f"demo-{channel}-patches-list.json"
        write(path, payload)
        marker = folder / f"demo-{channel}-extraction.json"
        status = db.read_json(marker)
        status["patch_list_hash"] = db.digest(path.read_bytes())
        write(marker, status)
    manifest = db.build_database(tmp_path, restore=False)
    path, bundles = snapshot(tmp_path, manifest)
    records = db.read_json(path / "package-records.json")
    assert {(p["name"], p["version"]) for p in records} == {
        ("com.any", None),
        ("com.array.any", None),
        ("com.specific", "1.0"),
    }
    index = db.read_json(path / "patch-index.json")
    assert set(index["packages"]) == {"com.any", "com.array.any", "com.specific"}
    rows = [p for page in index["pages"] for p in db.read_json(path / page)]
    assert next(p for p in rows if p["name"] == "No versions")["packages"] == []
    assert manifest["counts"]["patches"] == len(entries)
    assert bundles[0]["patch_count"] == len(entries)
    for file in folder.iterdir():
        file.unlink()
    db.restore_catalog_cache(tmp_path)
    assert db.read_json(folder / "demo-latest-patches-list.json") == payload


def test_old_morphe_and_legacy_compatibility_proof_requires_reextraction(tmp_path):
    for family in ("Morphe:V1", "ReVanced:V3", "ReVanced:V4"):
        root = tmp_path / family.replace(":", "-")
        folder = fixture(root, metadata_schema_version=2)
        for channel in ("latest", "stable"):
            path = folder / f"demo-{channel}-patches-bundle.json"
            raw = db.read_json(path)
            raw["bundle_type"] = family
            write(path, raw)
        manifest = db.build_database(root, restore=False)
        path, bundles = snapshot(root, manifest)
        assert bundles[0]["metadata_status"] == "unverified"
        assert bundles[0]["need_patches_update"]
        assert bundles[0]["patch_list_available"]
        # Restoration must not silently label old normalized metadata as current.
        for file in folder.iterdir():
            file.unlink()
        db.restore_catalog_cache(root)
        assert (
            db.read_json(folder / "demo-latest-patches-list.json")["metadata_schema_version"] == 2
        )
        assert snapshot(root, db.build_database(root))[1][0]["need_patches_update"]
        for channel in ("latest", "stable"):
            patch_path = folder / f"demo-{channel}-patches-list.json"
            payload = db.read_json(patch_path)
            payload["metadata_schema_version"] = db.PATCH_METADATA_SCHEMA_VERSION
            write(patch_path, payload)
            marker = folder / f"demo-{channel}-extraction.json"
            status = db.read_json(marker)
            status["patch_list_hash"] = db.digest(patch_path.read_bytes())
            write(marker, status)
        _, bundles = snapshot(root, db.build_database(root, restore=False))
        assert bundles[0]["metadata_status"] == "verified"
        assert not bundles[0]["need_patches_update"]
        for file in folder.iterdir():
            file.unlink()
        db.restore_catalog_cache(root)
        assert (
            db.read_json(folder / "demo-latest-patches-list.json")["metadata_schema_version"]
            == db.PATCH_METADATA_SCHEMA_VERSION
        )


def test_repeated_package_compatibility_retains_all_public_relationships(tmp_path):
    folder = fixture(tmp_path)
    for channel in ("latest", "stable"):
        path = folder / f"demo-{channel}-patches-list.json"
        payload = db.read_json(path)
        payload["patches"][0]["compatiblePackages"] = [
            {"name": "com.app", "versions": ["1.0", "2.0"]},
            {"name": "com.app", "versions": None},
        ]
        write(path, payload)
        marker = folder / f"demo-{channel}-extraction.json"
        status = db.read_json(marker)
        status["patch_list_hash"] = db.digest(path.read_bytes())
        write(marker, status)
    path, bundles = snapshot(tmp_path, db.build_database(tmp_path, restore=False))
    assert bundles[0]["metadata_status"] == "verified"
    assert {(p["name"], p["version"]) for p in db.read_json(path / "package-records.json")} == {
        ("com.app", None),
        ("com.app", "1.0"),
        ("com.app", "2.0"),
    }
    index = db.read_json(path / "patch-index.json")
    rows = [p for page in index["pages"] for p in db.read_json(path / page)]
    assert rows[0]["packages"] == [
        {"name": "com.app", "versions": ["1.0", "2.0"]},
        {"name": "com.app", "versions": []},
    ]
