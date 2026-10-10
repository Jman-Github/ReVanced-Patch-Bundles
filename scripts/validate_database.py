"""Validate snapshot integrity, relationships, and extraction freshness."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(root=ROOT):
    output = root / "database"
    manifest = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 1
    assert manifest["snapshot"] == "snapshots/" + manifest["generation"]
    reference = manifest.get("snapshot_ref")
    if reference is not None:
        assert isinstance(reference, str) and re.fullmatch(r"[a-f0-9]{40}", reference)
    snapshot = output / manifest["snapshot"]
    for name, metadata in manifest["files"].items():
        assert ".." not in name and not name.startswith("/")
        data = (snapshot / name).read_bytes()
        assert len(data) == metadata["bytes"], name
        assert hashlib.sha256(data).hexdigest() == metadata["sha256"], name
        json.loads(data)
    sources = json.loads((snapshot / "sources.json").read_text(encoding="utf-8"))
    bundles = json.loads((snapshot / "bundles.json").read_text(encoding="utf-8"))
    source_ids = {source["id"] for source in sources}
    bundle_ids = {bundle["id"] for bundle in bundles}
    assert len(source_ids) == len(sources) == manifest["counts"]["sources"]
    assert len(bundle_ids) == len(bundles) == manifest["counts"]["bundles"]
    for bundle in bundles:
        assert bundle["source_id"] in source_ids
        if bundle["metadata_status"] == "verified":
            assert bundle["file_hash"] and not bundle["need_patches_update"]
            assert bundle["patch_metadata_version"] == bundle["version"]
        else:
            assert bundle["patch_count"] == 0
            if bundle.get("extraction_terminal"):
                assert not bundle["need_patches_update"]
                assert bundle["file_hash"] and bundle["patcher_failure_fingerprint"]
                assert bundle["patcher_failure_config_hash"]
            else:
                assert bundle["need_patches_update"]
    index = json.loads((snapshot / "patch-index.json").read_text(encoding="utf-8"))
    count = 0
    for page in index["pages"]:
        rows = json.loads((snapshot / page).read_text(encoding="utf-8"))
        count += len(rows)
        for row in rows:
            assert row["bundle_id"] in bundle_ids
            assert row["source_id"] in source_ids
            assert page in index["bundles"][row["bundle_id"]]
            for package in row["packages"]:
                assert page in index["packages"][package["name"]]
    assert count == manifest["counts"]["patches"]
    print(f"Validated catalog {manifest['generation']}: {count} patch records")
    return manifest


if __name__ == "__main__":
    validate()
