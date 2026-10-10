"""Import release history without changing current channel pointers.

Behavior reference: https://github.com/brosssh/revanced-external-bundles/tree/3a59398d667c83cd7033f859f3cb59237da92b3f/src/main/kotlin/me/brosssh/bundles
Independent implementation for the immutable catalog.
"""

import hashlib
import json
import re
from datetime import UTC, datetime

try:
    from scripts.git_hosts import normalize_source
    from scripts.release_assets import (
        BUNDLE_TYPES,
        artifact_signature,
        asset_extension,
        choose_patch_bundle,
        release_assets,
        release_date,
    )
except ModuleNotFoundError:
    from git_hosts import normalize_source
    from release_assets import (
        BUNDLE_TYPES,
        artifact_signature,
        asset_extension,
        choose_patch_bundle,
        release_assets,
        release_date,
    )


def release_is_prerelease(release):
    if "prerelease" in release:
        return bool(release["prerelease"])
    return any(
        re.search(
            r"(^|[-._])(dev|alpha|beta|rc|pre)([-._\d]|$)", str(release.get(field) or "").lower()
        )
        for field in ("tag_name", "name")
    )


def mark_latest_history(root, registry, inventory):
    """Rank both release categories against history and configured channel inputs."""
    newest = {}
    selected_history = {}

    def artifact(raw):
        legacy = raw.get("patches")
        legacy = legacy if isinstance(legacy, dict) else {}
        download = raw.get("download_url") or legacy.get("url")
        family = raw.get("bundle_type") or (
            "ReVanced:V3"
            if legacy
            else BUNDLE_TYPES.get(
                asset_extension({"url": download or "", "name": ""}), "ReVanced:V4"
            )
        )
        return (
            raw.get("version") or legacy.get("version"),
            download,
            family,
            raw.get("provider_digest"),
        )

    def consider(source, raw, key=None):
        if not isinstance(raw, dict):
            return
        try:
            stamp = datetime.fromisoformat(str(raw.get("created_at")).replace("Z", "+00:00"))
            rank = (stamp.replace(tzinfo=UTC) if stamp.tzinfo is None else stamp).timestamp()
        except (TypeError, ValueError, OverflowError):
            rank = float("-inf")
        category = (source.lower(), bool(raw.get("is_prerelease")))
        # Current channel pointers win date ties, as in the public catalog.
        candidate = (rank, key is None, bool(registry.get(key, {}).get("is_latest")))
        if category not in newest or candidate > newest[category][0]:
            newest[category] = (candidate, key)

    for key, item in registry.items():
        try:
            path = (root / item["cache_path"]).resolve()
            if not path.is_relative_to((root / "internal/cache/history").resolve()):
                continue
            source = normalize_source(item["patches"], root)
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                continue
            selected_history[(source.lower(), artifact(raw)[0], bool(raw.get("is_prerelease")))] = (
                raw
            )
            consider(source, raw, key)
        except (OSError, ValueError, KeyError):
            continue
    for alias, settings in inventory.items():
        if not isinstance(settings, dict) or not settings.get("patches"):
            continue
        base = re.sub(r"-(latest|stable|dev)$", "", alias)
        path = (
            root
            / "internal/cache/bundles"
            / f"{base}-patch-bundles"
            / f"{alias}-patches-bundle.json"
        )
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                continue
            raw.setdefault(
                "is_prerelease", bool(settings.get("prerelease")) and not settings.get("latest")
            )
            source = normalize_source(settings["patches"], root)
            identity = artifact(raw)
            selected = selected_history.get(
                (source.lower(), identity[0], bool(raw.get("is_prerelease")))
            )
            if selected is not None:
                # History chooses replacement assets for this release. A stale
                # pointer does not mean the selected binary gets a channel pass.
                if artifact(selected) != identity:
                    continue
                raw = selected
            consider(source, raw)
        except (OSError, ValueError, KeyError):
            continue
    latest = {key for _, key in newest.values() if key is not None}
    for key, item in registry.items():
        item["is_latest"] = key in latest


def save_history(root, inventory, release_sets):
    directory = root / "internal/cache/history"
    registry_path = directory / "sources.json"
    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        registry = {}
    active = {
        normalize_source(item["patches"], root).lower()
        for item in inventory.values()
        if isinstance(item, dict) and item.get("patches")
    }
    registry = {
        key: item
        for key, item in registry.items()
        if normalize_source(item["patches"], root).lower() in active
    }
    try:
        from scripts.source_policy import disabled_sources
    except ModuleNotFoundError:
        from source_policy import disabled_sources
    disabled = disabled_sources(inventory, root)
    by_source = {}
    for key, item in registry.items():
        canonical = normalize_source(item["patches"], root).lower()
        by_source.setdefault(canonical, []).append((key, item))
    visited = set()
    for alias, settings in sorted(inventory.items()):
        if not isinstance(settings, dict) or not settings.get("patches"):
            continue
        source = normalize_source(settings["patches"], root)
        if source.lower() in visited or source.lower() in disabled:
            continue
        visited.add(source.lower())
        releases = release_sets.get(source.lower())
        if releases is None:
            continue  # Preserve existing history when a host is unavailable.
        base = re.sub(r"-(latest|stable|dev)$", "", alias)
        previous_versions = {}
        for key, item in by_source.get(source.lower(), []):
            try:
                path = (root / item["cache_path"]).resolve()
                if not path.is_relative_to(directory.resolve()):
                    continue
                raw = json.loads(path.read_text(encoding="utf-8"))
                version = raw.get("version") or raw.get("patches", {}).get("version")
                previous_versions.setdefault(version, []).append(key)
            except (OSError, ValueError, KeyError):
                continue
        for release in releases:
            if (
                release.get("draft")
                or release.get("upcoming_release")
                or not release.get("tag_name")
            ):
                continue
            assets = release_assets(release)
            selected = choose_patch_bundle(assets)
            if selected:
                # Replace earlier multi-asset inputs for this version. Published
                # history remains available, but only this asset is refreshed.
                for key in previous_versions.get(str(release["tag_name"]), []):
                    registry.pop(key, None)
            for asset in [selected] if selected else []:
                extension = asset_extension(asset)
                download = asset["url"]
                version = str(release["tag_name"])
                identity = hashlib.sha256(
                    json.dumps([source.lower(), version, download], separators=(",", ":")).encode()
                ).hexdigest()[:24]
                key = f"history-{identity}-stable"
                folder = directory / f"history-{identity}-patch-bundles"
                folder.mkdir(parents=True, exist_ok=True)
                signature = artifact_signature(download, assets)
                raw = {
                    "created_at": release_date(release),
                    "provider_digest": asset.get("provider_digest"),
                    "description": release.get("body") or release.get("description") or "",
                    "download_url": download,
                    "bundle_type": BUNDLE_TYPES[extension],
                    "signature_download_url": signature,
                    "version": version,
                    "is_prerelease": release_is_prerelease(release),
                }
                if extension == ".jar":
                    raw = {**raw, "patches": {"version": version, "url": download}}
                    del raw["download_url"]  # Legacy extraction needs only the patches JAR.
                path = folder / f"{key}-patches-bundle.json"
                temporary = path.with_suffix(".tmp")
                temporary.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
                temporary.replace(path)
                registry[key] = {
                    "patches": source,
                    "historical": True,
                    "alias": base,
                    "cache_path": path.relative_to(root).as_posix(),
                    "prerelease": raw["is_prerelease"],
                }
    mark_latest_history(root, registry, inventory)
    directory.mkdir(parents=True, exist_ok=True)
    temporary = registry_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(registry, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(registry_path)
    return registry
