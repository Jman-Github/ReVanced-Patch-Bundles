"""Restore historical extraction inputs from the committed catalog on fresh CI runners."""

import hashlib
import json


def restore_history(root, history, inventory):
    directory = root / "internal/cache/history"
    registry_path = directory / "sources.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        registry = {}
    active = set(inventory)
    for item in sorted(
        history.values(),
        key=lambda item: item["bundle"]["metadata_status"] == "verified",
        reverse=True,
    ):
        bundle = item["bundle"]
        source = inventory.get(bundle["source_id"])
        if bundle["source_id"] not in active or source is None:
            continue
        identity = hashlib.sha256(
            json.dumps(
                [source["url"].lower(), bundle["version"], bundle["download_url"]],
                separators=(",", ":"),
            ).encode()
        ).hexdigest()[:24]
        key = f"history-{identity}-stable"
        folder = directory / f"history-{identity}-patch-bundles"
        folder.mkdir(parents=True, exist_ok=True)
        raw_path = folder / f"{key}-patches-bundle.json"
        patch_path = folder / f"{key}-patches-list.json"
        if patch_path.exists():
            existing = json.loads(patch_path.read_text(encoding="utf-8"))
            if existing.get("version") is None and not existing.get("patches"):
                patch_path.unlink()
        if raw_path.exists():
            continue
        raw = {
            field: bundle.get(field)
            for field in (
                "created_at",
                "description",
                "version",
                "download_url",
                "provider_digest",
                "bundle_type",
                "signature_download_url",
                "is_prerelease",
                "integrations",
            )
        }
        if raw.get("integrations") is None:
            raw.pop("integrations", None)
        if bundle["bundle_type"] == "ReVanced:V3":
            raw["patches"] = {"version": raw["version"], "url": raw.pop("download_url")}
        raw_path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
        patch_path = folder / f"{key}-patches-list.json"
        if isinstance(bundle["patch_metadata_version"], str):
            patch_path.write_text(
                json.dumps(
                    {
                        "version": bundle["patch_metadata_version"],
                        "patches": item["patches"],
                        "metadata_schema_version": bundle.get("patch_metadata_schema_version", 0),
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        status = {
            "version": bundle["version"],
            "download_url": bundle["download_url"],
            "status": bundle["extraction_status"],
            "runtime": bundle["patcher_runtime"],
            "provider_digest": bundle.get("extracted_provider_digest"),
            "file_hash": bundle["file_hash"],
            "attempted_at": bundle.get("patch_refresh_attempted_at"),
            "failure_fingerprint": bundle.get("patcher_failure_fingerprint"),
            "terminal": bundle.get("extraction_terminal", False),
            "bundle_type": bundle.get("bundle_type"),
            "runtime_config_hash": bundle.get("patcher_failure_config_hash"),
            "patch_list_hash": hashlib.sha256(patch_path.read_bytes()).hexdigest()
            if bundle["metadata_status"] == "verified"
            else None,
        }
        (folder / f"{key}-extraction.json").write_text(
            json.dumps(status, indent=2) + "\n", encoding="utf-8"
        )
        registry[key] = {
            "patches": source["url"],
            "historical": True,
            "alias": source["aliases"][0],
            "cache_path": raw_path.relative_to(root).as_posix(),
            "prerelease": bundle["is_prerelease"],
            "is_latest": bool(bundle.get("is_latest")),
        }
    directory.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
