import importlib
import json

import pytest
from test_generate_database import db, fixture, snapshot, write

from scripts.source_policy import disabled_sources, write_extraction_policy


def test_disabled_source_retains_history_and_permissions_survive_reenable(tmp_path):
    fixture(tmp_path)
    original = db.build_database(tmp_path)
    _, old_bundles = snapshot(tmp_path, original)
    inventory = json.loads((tmp_path / "config/sources.json").read_text())
    inventory["demo-stable"]["disabled"] = True
    write(tmp_path / "config/sources.json", inventory)
    disabled = db.build_database(tmp_path)
    path, bundles = snapshot(tmp_path, disabled)
    source = next(row for row in db.read_json(path / "sources.json") if row["repo"] == "demo")
    assert not source["enabled"] and source["unavailable_reason"]
    assert bundles[0]["legacy_id"] == old_bundles[0]["legacy_id"]
    assert bundles[0]["channels"] == old_bundles[0]["channels"]
    assert db.read_json(path / "patch-statistics.json")["count"] == 0
    assert db.read_json(path / "patch-index.json")["patch_ids"] == {}
    assert "demo-patch-bundles" in write_extraction_policy(tmp_path)
    inventory["demo-stable"]["disabled"] = False
    write(tmp_path / "config/sources.json", inventory)
    enabled = db.build_database(tmp_path)
    path, bundles = snapshot(tmp_path, enabled)
    source = next(row for row in db.read_json(path / "sources.json") if row["repo"] == "demo")
    assert source["enabled"]
    assert db.read_json(path / "patch-statistics.json")["count"] == 1


def test_source_switches_validate_boolean_and_apply_to_canonical_aliases(tmp_path):
    fixture(tmp_path)
    inventory = db.read_json(tmp_path / "config/sources.json")
    inventory["demo-stable"]["disabled"] = "false"
    with pytest.raises(ValueError, match="boolean"):
        disabled_sources(inventory, tmp_path)
    inventory["demo-stable"]["disabled"] = True
    assert "https://github.com/owner/demo" in disabled_sources(inventory, tmp_path)


def test_refresh_phase_records_have_stable_ids_and_are_published(tmp_path, monkeypatch):
    fixture(tmp_path)
    monkeypatch.syspath_prepend(str(db.ROOT / "scripts"))
    module = importlib.import_module("run_catalog_refresh")
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    # Separate jobs have independent timestamps even when their IDs are stable.
    clock = iter(f"2026-10-08T00:00:{tick:02d}Z" for tick in range(60))
    monkeypatch.setattr(module, "instant", lambda: next(clock))
    first = module.Refresh(tmp_path)
    second = module.Refresh(tmp_path)
    assert [job["job_id"] for job in first.jobs] == [job["job_id"] for job in second.jobs]
    assert first.jobs[0]["started_at"] != second.jobs[0]["started_at"]
    first.jobs[0].update(status="STARTED", started_at=module.instant())
    write(
        tmp_path / "internal/cache/bundle-run-metadata.json",
        {"generated_at": module.instant(), "status": "COMPLETED"},
    )
    first.checkpoint(force=True)
    manifest = db.read_json(tmp_path / "database/manifest.json")
    rows = db.read_json(tmp_path / "database" / manifest["snapshot"] / "refresh-jobs.json")
    assert [row["job_type"] for row in rows] == ["BUNDLES", "PATCHES"]
    assert [row["status"] for row in rows] == ["STARTED", "STARTED"]
    first.jobs[0].update(status="COMPLETED", completed_at=module.instant())
    first.checkpoint(force=True)
    current = db.read_json(tmp_path / "database/manifest.json")
    assert current["generation"] != manifest["generation"]
    rows = db.read_json(tmp_path / "database" / current["snapshot"] / "refresh-jobs.json")
    assert rows[0]["status"] == "COMPLETED"


def test_publishing_is_never_enabled_outside_actions(tmp_path, monkeypatch):
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    monkeypatch.delenv("GIT_TOKEN", raising=False)
    monkeypatch.syspath_prepend(str(db.ROOT / "scripts"))
    module = importlib.import_module("run_catalog_refresh")
    with pytest.raises(ValueError, match="GitHub Actions"):
        module.Refresh(tmp_path, publish=True)


def test_refresh_failure_finishes_pending_phases(tmp_path, monkeypatch):
    fixture(tmp_path)
    monkeypatch.syspath_prepend(str(db.ROOT / "scripts"))
    module = importlib.import_module("run_catalog_refresh")
    runner = module.Refresh(tmp_path)

    def fail():
        runner.jobs[0].update(status="STARTED", started_at=module.instant())
        raise RuntimeError("simulated runner failure")

    monkeypatch.setattr(runner, "_run", fail)
    with pytest.raises(RuntimeError, match="simulated"):
        runner.run()
    assert all(job["status"] == "FAILED" for job in runner.jobs)
    assert all(job["completed_at"] for job in runner.jobs)
    published = db.read_json(tmp_path / "internal/cache/refresh-jobs.json")
    assert published == runner.jobs


def test_checkpoint_retries_push_even_without_a_new_commit(tmp_path, monkeypatch):
    fixture(tmp_path)
    manifest = db.build_database(tmp_path)
    manifest["snapshot_ref"] = "a" * 40
    write(tmp_path / "database/manifest.json", manifest)
    monkeypatch.syspath_prepend(str(db.ROOT / "scripts"))
    module = importlib.import_module("run_catalog_refresh")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GIT_TOKEN", "test-token")
    monkeypatch.setattr(module.shutil, "which", lambda _: "git")
    calls = []

    def command(args, **kwargs):
        calls.append((args, kwargs))
        return module.subprocess.CompletedProcess(args, 0)

    monkeypatch.setattr(module.subprocess, "run", command)
    module.Refresh(tmp_path, publish=True).push()
    assert calls[-1][0][1] == "push"
    assert not any("commit" in args for args, _ in calls)
    assert all("test-token" not in str(args) for args, _ in calls)
    assert calls[-1][1]["env"]["GIT_CONFIG_KEY_0"] == "http.https://github.com/.extraheader"


def test_phase_publishes_progress_before_the_child_finishes(tmp_path, monkeypatch):
    fixture(tmp_path)
    monkeypatch.syspath_prepend(str(db.ROOT / "scripts"))
    module = importlib.import_module("run_catalog_refresh")
    runner = module.Refresh(tmp_path)
    published = []

    class Child:
        returncode = None

        def poll(self):
            if len(published) >= 2:
                self.returncode = 0
            return self.returncode

    monkeypatch.setattr(module.subprocess, "Popen", lambda *a, **kw: Child())
    monkeypatch.setattr(module.time, "sleep", lambda _: None)
    monkeypatch.setattr(
        runner, "checkpoint", lambda **kw: published.append([row["status"] for row in runner.jobs])
    )
    runner.phase("BUNDLES", ["fixed-command"])
    assert published == [["STARTED", "STARTED"], ["STARTED", "STARTED"], ["COMPLETED", "STARTED"]]


def test_workflow_retry_gets_new_phase_ids(tmp_path, monkeypatch):
    fixture(tmp_path)
    monkeypatch.syspath_prepend(str(db.ROOT / "scripts"))
    module = importlib.import_module("run_catalog_refresh")
    monkeypatch.setenv("GITHUB_RUN_ID", "123")
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "1")
    first = module.Refresh(tmp_path)
    monkeypatch.setenv("GITHUB_RUN_ATTEMPT", "2")
    retry = module.Refresh(tmp_path)
    assert first.jobs[0]["job_id"] != retry.jobs[0]["job_id"]
    assert retry.jobs[0]["actions_run_attempt"] == 2


def test_checkpoints_do_not_rewrite_inputs_while_discovery_runs(tmp_path, monkeypatch):
    fixture(tmp_path)
    monkeypatch.syspath_prepend(str(db.ROOT / "scripts"))
    module = importlib.import_module("run_catalog_refresh")
    runner = module.Refresh(tmp_path)

    def forbidden(*args):
        pytest.fail("checkpoint must not restore or rewrite extraction inputs")

    database_module = importlib.import_module(module.build_database.__module__)
    monkeypatch.setattr(database_module, "restore_catalog_cache", forbidden)
    runner.checkpoint(force=True)


def test_snapshot_anchor_survives_rebuilds_but_not_changed_generations(tmp_path):
    folder = fixture(tmp_path)
    first = db.build_database(tmp_path)
    first["snapshot_ref"] = "a" * 40
    write(tmp_path / "database/manifest.json", first)
    assert db.build_database(tmp_path)["snapshot_ref"] == first["snapshot_ref"]
    path = folder / "demo-latest-patches-bundle.json"
    raw = db.read_json(path)
    raw["description"] = "A new description"
    write(path, raw)
    assert "snapshot_ref" not in db.build_database(tmp_path)


def test_publication_anchor_remains_readable_after_branch_retention(tmp_path, monkeypatch):
    fixture(tmp_path)
    monkeypatch.syspath_prepend(str(db.ROOT / "scripts"))
    module = importlib.import_module("run_catalog_refresh")
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.setenv("GIT_TOKEN", "test-token")
    executable = module.shutil.which("git")
    assert executable
    actual_run = module.subprocess.run
    actual_run([executable, "init", str(tmp_path)], check=True, capture_output=True)
    for key, value in (("commit.gpgsign", "false"), ("core.autocrlf", "false")):
        actual_run(
            [executable, "-C", str(tmp_path), "config", key, value], check=True, capture_output=True
        )
    pushes = []

    def command(args, **kwargs):
        if args[1] == "push":
            pushes.append(args)
            return module.subprocess.CompletedProcess(args, 0)
        return actual_run(args, **kwargs)

    monkeypatch.setattr(module.subprocess, "run", command)
    runner = module.Refresh(tmp_path, publish=True)
    first = db.build_database(tmp_path)
    runner.push()
    pinned = db.read_json(tmp_path / "database/manifest.json")
    assert len(pinned["snapshot_ref"]) == 40
    for index in range(9):
        path = (
            tmp_path
            / "internal/cache/bundles/demo-patch-bundles"
            / "demo-latest-patches-bundle.json"
        )
        raw = db.read_json(path)
        raw["description"] = str(index)
        write(path, raw)
        db.build_database(tmp_path, restore=False)
        runner.push()
    assert not (tmp_path / "database" / first["snapshot"]).exists()
    # No remote calls: only the temporary repository contains these test commits.
    old = actual_run(
        [
            executable,
            "show",
            pinned["snapshot_ref"] + ":database/" + first["snapshot"] + "/bundles.json",
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(old.stdout)[0]["version"] == "v1"
    assert len(pushes) == 10
