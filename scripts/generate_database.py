"""Generate immutable catalog snapshots from private release/extraction inputs."""

import argparse
import hashlib
import json
import re
import shutil
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode, urlparse

try:
    from scripts.git_hosts import hosts
    from scripts.git_hosts import normalize_source as normalize_repository
    from scripts.release_assets import digest_matches
    from scripts.release_history import release_is_prerelease
    from scripts.snapshot_retention import apply_retention, published_snapshots, retention_plan
except ModuleNotFoundError:
    from git_hosts import hosts
    from git_hosts import normalize_source as normalize_repository
    from release_assets import digest_matches
    from release_history import release_is_prerelease
    from snapshot_retention import apply_retention, published_snapshots, retention_plan

try:
    from scripts.source_policy import disabled_sources, unavailable_sources, write_extraction_policy
except ModuleNotFoundError:
    from source_policy import disabled_sources, unavailable_sources, write_extraction_policy

ROOT = Path(__file__).resolve().parents[1]
PATCH_METADATA_SCHEMA_VERSION = 3


def read_json(path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def runtime_config_hash(root):
    config = root / "config/patcher-runtimes.json"
    return digest(config.read_bytes() if config.is_file() else b"")


def runtime_fingerprint(root):
    files = (
        root / "config/patcher-runtimes.json",
        root / "bundle-parser/build/runtime-classpaths.json",
    )
    return digest(b"".join(path.read_bytes() for path in files if path.is_file()))


def paused_failure(root, status, raw, family):
    # Before runtime preparation on a fresh runner, compare the portable config
    # hash. Once installed, also account for runtime availability/classpaths.
    manifest = root / "bundle-parser/build/runtime-classpaths.json"
    return bool(
        status.get("terminal") is True
        and status.get("status") != "verified"
        and status.get("file_hash")
        and status.get("bundle_type") == family
        and status.get("failure_fingerprint")
        and status.get("runtime_config_hash") == runtime_config_hash(root)
        and (not manifest.is_file() or status["failure_fingerprint"] == runtime_fingerprint(root))
        and digest_matches(
            raw.get("provider_digest"), status["file_hash"], status.get("provider_digest")
        )
    )


def timestamp_rank(value):
    try:
        stamp = datetime.fromisoformat(str(value))
        return (stamp.replace(tzinfo=UTC) if stamp.tzinfo is None else stamp).timestamp()
    except (TypeError, ValueError, OverflowError):
        return float("-inf")


def normalize_source(value, root=ROOT):
    return normalize_repository(value, root)


def packages_for(patch):
    def versions_list(value):
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [str(item) for item in value if isinstance(item, str | int | float)]
        return []

    value = patch.get("compatiblePackages")
    if isinstance(value, dict):
        return [
            {"name": name, "versions": versions_list(versions)}
            for name, versions in value.items()
            if isinstance(name, str) and name and not (isinstance(versions, list) and not versions)
        ]
    result = []
    for item in value if isinstance(value, list) else []:
        if isinstance(item, str):
            result.append({"name": item, "versions": []})
        elif isinstance(item, dict):
            name = item.get("name") or item.get("packageName")
            if isinstance(name, str) and name:
                versions = item.get("versions")
                targets = item.get("targets")
                if versions is None and isinstance(targets, list):
                    versions = [
                        target["version"]
                        for target in targets
                        if isinstance(target, dict) and target.get("version")
                    ]
                if isinstance(versions, list) and not versions:
                    continue
                result.append({"name": name, "versions": versions_list(versions)})
    return result


def grams(text):
    text = text.lower()
    return {text[i : i + 3] for i in range(max(0, len(text) - 2))}


def restore_catalog_cache(root=ROOT):
    """Restore current channel inputs from the last committed, trusted snapshot."""
    write_extraction_policy(root)
    manifest = read_json(root / "database/manifest.json", {})
    snapshot = manifest.get("snapshot", "")
    if not re.fullmatch(r"snapshots/[a-f0-9]{24}", snapshot):
        return
    history = read_json(root / "database" / snapshot / "history.json", {})
    availability = read_json(root / "database" / snapshot / "availability.json", {})
    missing_channels = {
        (row["source_id"], row["channel"])
        for row in availability.get("missing", [])
        if row.get("reason") == "no_release"
    }
    inventory = read_json(root / "config/sources.json", {})
    if not isinstance(inventory, dict):
        return
    cache = root / "internal/cache/bundles"
    discovery_path = cache / "discovery-status.json"
    discovery = read_json(discovery_path, {})
    for key, settings in inventory.items():
        if not isinstance(settings, dict) or not isinstance(settings.get("patches"), str):
            continue
        source_id = digest(normalize_source(settings["patches"], root).lower().encode())[:16]
        channel = (
            "latest"
            if settings.get("latest")
            else "dev"
            if settings.get("prerelease")
            else "stable"
        )
        if (source_id, channel) in missing_channels:
            discovery.setdefault(key, "no_matching_release")
        item = next(
            (
                item
                for item in history.values()
                if item["bundle"]["source_id"] == source_id
                and channel in item["bundle"]["channels"]
            ),
            None,
        )
        if item is None:
            continue
        base = re.sub(r"-(latest|stable|dev)$", "", key)
        folder = cache / f"{base}-patch-bundles"
        raw_path = folder / f"{key}-patches-bundle.json"
        if raw_path.exists():
            continue
        bundle = item["bundle"]
        folder.mkdir(parents=True, exist_ok=True)
        if bundle["bundle_type"] == "ReVanced:V3":
            raw = {
                "patches": {"version": bundle["version"], "url": bundle["download_url"]},
                "integrations": bundle.get("integrations"),
                "provider_digest": bundle.get("provider_digest"),
                "created_at": bundle.get("created_at"),
                "description": bundle.get("description"),
                "signature_download_url": bundle.get("signature_download_url"),
                "is_prerelease": bundle.get("is_prerelease"),
                "bundle_type": bundle["bundle_type"],
            }
        else:
            raw = {
                field: bundle.get(field)
                for field in (
                    "version",
                    "download_url",
                    "provider_digest",
                    "signature_download_url",
                    "bundle_type",
                    "is_prerelease",
                    "created_at",
                    "description",
                )
            }
        raw_path.write_bytes(encoded(raw))
        patch_path = folder / f"{key}-patches-list.json"
        if isinstance(bundle["patch_metadata_version"], str):
            patch_path.write_bytes(
                encoded(
                    {
                        "version": bundle["patch_metadata_version"],
                        "patches": item["patches"],
                        "metadata_schema_version": bundle.get("patch_metadata_schema_version", 0),
                    }
                )
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
            "patch_list_hash": (
                digest(patch_path.read_bytes()) if bundle["metadata_status"] == "verified" else None
            ),
        }
        (folder / f"{key}-extraction.json").write_bytes(encoded(status))
        discovery.setdefault(key, bundle.get("release_status", "unverified"))
    if discovery:
        cache.mkdir(parents=True, exist_ok=True)
        discovery_path.write_bytes(encoded(discovery))
    try:
        from scripts.historical_cache import restore_history
    except ModuleNotFoundError:
        from historical_cache import restore_history
    catalog_sources = read_json(root / "database" / snapshot / "sources.json", [])
    active_urls = {
        normalize_source(item["patches"], root).lower()
        for item in inventory.values()
        if isinstance(item, dict) and item.get("patches")
    }
    restore_history(
        root,
        history,
        {item["id"]: item for item in catalog_sources if item["url"].lower() in active_urls},
    )
    write_extraction_policy(root)


def build_database(root=ROOT, *, restore=True):
    if restore:
        restore_catalog_cache(root)
    config = read_json(root / "config/site.json")
    inventory = read_json(root / "config/sources.json")
    if not isinstance(inventory, dict) or not config:
        raise ValueError("Source inventory and site configuration are required")
    output = root / "database"
    previous = read_json(output / "manifest.json", {})
    previous_path = previous.get("snapshot", "")
    history = {}
    if re.fullmatch(r"snapshots/[a-f0-9]{24}", previous_path):
        history = read_json(output / previous_path / "history.json", {})
    disabled = disabled_sources(inventory, root)
    unavailable = unavailable_sources(inventory, root)
    configured_urls = {
        normalize_source(item["patches"], root).lower()
        for item in inventory.values()
        if isinstance(item, dict) and item.get("patches")
    }
    historical_inventory = read_json(root / "internal/cache/history/sources.json", {})
    inventory = {
        **inventory,
        **{
            key: item
            for key, item in historical_inventory.items()
            if normalize_source(item["patches"], root).lower() in configured_urls
        },
    }
    sources, bundles, details = {}, {}, {}
    detail_ranks = {}
    input_bundles = set()
    historical_inputs = set()
    missing, retired = [], []
    run = read_json(root / "internal/cache/bundle-run-metadata.json", {}).get("bundles", {})
    discovery = read_json(root / "internal/cache/bundles/discovery-status.json", {})
    repository_metadata = read_json(root / "database/repository-metadata.json", {})
    for key, settings in sorted(inventory.items()):
        if not isinstance(settings, dict) or not isinstance(settings.get("patches"), str):
            continue
        url = normalize_source(settings["patches"], root)
        source_id = digest(url.lower().encode())[:16]
        base = settings.get("alias") or re.sub(r"-(latest|stable|dev)$", "", key)
        channel = (
            "latest"
            if settings.get("latest")
            else ("dev" if settings.get("prerelease") else "stable")
        )
        parsed = urlparse(url)
        namespace, repo = parsed.path.strip("/").rsplit("/", 1)
        source = sources.setdefault(
            source_id,
            {
                "id": source_id,
                "url": url,
                "host": parsed.hostname,
                "enabled": url.lower() not in disabled,
                "unavailable_reason": unavailable.get(url.lower()),
                "namespace": namespace,
                "repo": repo,
                "aliases": [],
                "bundles": [],
                "source_metadatum": {
                    "owner_name": namespace,
                    "repo_name": repo,
                    "owner_avatar_url": None,
                    "repo_description": None,
                    "repo_stars": None,
                    "repo_pushed_at": None,
                    "is_repo_archived": None,
                },
            },
        )
        enriched = repository_metadata.get(url.lower(), {}).get("source_metadatum")
        if isinstance(enriched, dict):
            source["source_metadatum"].update(
                {key: value for key, value in enriched.items() if key in source["source_metadatum"]}
            )
        if base not in source["aliases"]:
            source["aliases"].append(base)
        if not source["enabled"]:
            continue
        relative = f"internal/cache/bundles/{base}-patch-bundles/{key}-patches-bundle.json"
        if settings.get("historical"):
            relative = settings["cache_path"]
            resolved = (root / relative).resolve()
            if not resolved.is_relative_to((root / "internal/cache/history").resolve()):
                raise ValueError("Historical input escaped cache directory")
        path = root / relative
        raw = read_json(path)
        patch_path = path.with_name(f"{key}-patches-list.json")
        patches = read_json(patch_path, {})
        if not isinstance(patches, dict):
            patches = {}
        status = read_json(path.with_name(f"{key}-extraction.json"), {})
        if not isinstance(status, dict):
            status = {}
        if not settings.get("historical") and discovery.get(key) == "no_matching_release":
            missing.append({"source_id": source_id, "channel": channel, "reason": "no_release"})
            continue
        if not isinstance(raw, dict):
            missing.append({"source_id": source_id, "channel": channel, "reason": "missing_bundle"})
            continue
        modern = "download_url" in raw
        artifact = raw if modern else raw.get("patches", {})
        if not isinstance(artifact, dict):
            missing.append({"source_id": source_id, "channel": channel, "reason": "invalid_bundle"})
            continue
        version = artifact.get("version")
        download = artifact.get("download_url" if modern else "url")
        if (
            not version
            or not download
            or str(version).startswith("N/A")
            or str(download).startswith("N/A")
        ):
            missing.append({"source_id": source_id, "channel": channel, "reason": "no_release"})
            continue
        if status.get("version") != version or status.get("download_url") != download:
            status = {}
        prior_release = next(
            (
                item["bundle"]
                for item in history.values()
                if item["bundle"]["source_id"] == source_id and item["bundle"]["version"] == version
            ),
            {},
        )
        file_hash = status.get("file_hash")
        identity = digest(
            encoded(
                [
                    source_id,
                    version,
                    download,
                    file_hash,
                    raw.get("provider_digest"),
                    raw.get("bundle_type"),
                ]
            )
        )[:24]
        input_bundles.add(identity)
        if settings.get("historical"):
            historical_inputs.add(identity)
        patch_array = patches.get("patches") if isinstance(patches, dict) else None
        valid = (
            isinstance(patch_array, list)
            and (bool(patch_array) or isinstance(patches.get("version"), str))
            and all(
                isinstance(p, dict) and (p.get("name") is None or isinstance(p["name"], str))
                for p in patch_array
            )
        )
        same_version = isinstance(patches, dict) and patches.get("version") == version
        family = raw.get("bundle_type") or (
            "Morphe:V1"
            if urlparse(download).path.lower().endswith(".mpp")
            else ("ReVanced:V4" if modern else "ReVanced:V3")
        )
        if family not in {"Morphe:V1", "ReVanced:V4", "ReVanced:V3"}:
            raise ValueError("Unsupported bundle type: " + str(family))
        # Older extraction could overwrite repeated compatibility entries.
        # Keep its list readable, but re-extract before trusting its compatibility.
        schema_current = patches.get("metadata_schema_version") == PATCH_METADATA_SCHEMA_VERSION
        proof = bool(
            valid
            and same_version
            and schema_current
            and status.get("status") == "verified"
            and status.get("download_url") == download
            and status.get("version") == version
            and file_hash
            and digest_matches(raw.get("provider_digest"), file_hash, status.get("provider_digest"))
            and status.get("patch_list_hash") == digest(patch_path.read_bytes())
        )
        freshness = (
            "verified"
            if proof
            else ("stale" if valid and not same_version else "unverified" if valid else "missing")
        )
        paused = not proof and paused_failure(root, status, raw, family)
        bundle = bundles.setdefault(
            identity,
            {
                "id": identity,
                "source_id": source_id,
                "bundle_type": family,
                "release_status": discovery.get(key, "unverified"),
                "ecosystem": family.split(":")[0].lower(),
                "version": version,
                "created_at": raw.get("created_at"),
                "description": raw.get("description") or "",
                "download_url": download,
                "signature_download_url": raw.get("signature_download_url"),
                "integrations": raw.get("integrations"),
                "file_hash": file_hash,
                "provider_digest": raw.get("provider_digest"),
                "extracted_provider_digest": status.get("provider_digest"),
                "channels": [],
                "import_urls": {},
                "is_prerelease": run.get(key, {}).get(
                    "is_prerelease",
                    raw.get(
                        "is_prerelease",
                        history.get(identity, {})
                        .get("bundle", {})
                        .get(
                            "is_prerelease",
                            channel == "dev" or release_is_prerelease({"tag_name": version}),
                        ),
                    ),
                ),
                "is_latest": False,
                "metadata_status": freshness,
                "need_patches_update": not (proof or paused),
                "extraction_terminal": paused,
                "patcher_failure_config_hash": status.get("runtime_config_hash"),
                "patch_list_available": valid,
                "patch_metadata_version": patches.get("version"),
                "patch_metadata_schema_version": patches.get("metadata_schema_version", 0),
                "patcher_runtime": status.get("runtime"),
                "extraction_status": status.get("status", "unverified"),
                "patch_refresh_attempted_at": status.get("attempted_at"),
                "patcher_failure_fingerprint": status.get("failure_fingerprint"),
                "patch_count": len(patch_array) if proof else 0,
                "packages": [],
                "release_url": run.get(key, {}).get("patches", {}).get("release_url")
                or prior_release.get("release_url"),
            },
        )
        if timestamp_rank(status.get("attempted_at")) > timestamp_rank(
            bundle["patch_refresh_attempted_at"]
        ):
            bundle["patch_refresh_attempted_at"] = status["attempted_at"]
            if bundle["metadata_status"] != "verified":
                bundle.update(
                    extraction_status=status.get("status", "unverified"),
                    extracted_provider_digest=status.get("provider_digest"),
                    patcher_runtime=status.get("runtime"),
                    extraction_terminal=paused,
                    patcher_failure_fingerprint=status.get("failure_fingerprint"),
                    patcher_failure_config_hash=status.get("runtime_config_hash"),
                    need_patches_update=not (proof or paused),
                )
        detail_rank = (
            proof,
            same_version,
            timestamp_rank(status.get("attempted_at")),
            not settings.get("historical"),
        )
        preferred_metadata = valid and (
            identity not in detail_ranks or detail_rank >= detail_ranks[identity]
        )
        preferred_proof = proof and preferred_metadata
        if preferred_metadata:
            bundle.update(
                metadata_status=freshness,
                patch_metadata_version=patches.get("version"),
                patch_metadata_schema_version=patches.get("metadata_schema_version", 0),
                patch_list_available=True,
                patch_count=len(patch_array) if proof else 0,
            )
        if preferred_proof:
            bundle.update(
                metadata_status="verified",
                need_patches_update=False,
                extraction_terminal=False,
                patcher_failure_fingerprint=None,
                patch_count=len(patch_array),
                patcher_runtime=status.get("runtime"),
                extracted_provider_digest=status.get("provider_digest"),
                extraction_status=status.get("status"),
                patch_metadata_version=patches.get("version"),
                patch_metadata_schema_version=patches.get("metadata_schema_version", 0),
                patch_list_available=True,
            )
        if not settings.get("historical"):
            # History may be visited first and carry an old integration APK.
            # Current channel metadata also takes precedence when it removes it.
            bundle["integrations"] = raw.get("integrations")
            if channel not in bundle["channels"]:
                bundle["channels"].append(channel)
            bundle["import_urls"][channel] = (
                config["api"].rstrip("/")
                + "/api/v3/bundle?"
                + urlencode(
                    {
                        "source_url": url,
                        "version": "latest",
                        "channel": {"latest": "any", "stable": "stable", "dev": "prerelease"}[
                            channel
                        ],
                    }
                )
            )
            if channel == "stable":
                bundle["is_prerelease"] = False
        if identity not in source["bundles"]:
            source["bundles"].append(identity)
        if preferred_metadata:
            detail_ranks[identity] = detail_rank
            details[identity] = patch_array
            bundle["packages"] = sorted(
                {p["name"] for patch in patch_array for p in packages_for(patch)}
            )
        elif identity not in details:
            details[identity] = patch_array if valid else []
            if valid:
                bundle["packages"] = sorted(
                    {p["name"] for patch in patch_array for p in packages_for(patch)}
                )
    for identity, item in history.items():
        if item["bundle"]["source_id"] not in sources:
            retired.append(identity)
            continue
        if identity not in bundles:
            bundle = item["bundle"].copy()
            if sources[bundle["source_id"]]["enabled"]:
                bundle.update(channels=[], is_latest=False, import_urls={})
            bundles[identity], details[identity] = bundle, item["patches"]
            sources[bundle["source_id"]]["bundles"].append(identity)

    # Upstream upserts one record per source/version/release category. Keep the
    # previously published ID while replacing its artifact and extraction proof.
    groups = {}
    for key, bundle in bundles.items():
        group = (bundle["source_id"], bundle["version"], bool(bundle["is_prerelease"]))
        groups.setdefault(group, []).append(key)
    canonical, canonical_details, canonical_inputs = {}, {}, set()
    for keys in groups.values():
        # The historical registry contains the asset currently selected by
        # discovery, even if a channel still has an older extraction input.
        def asset(key):
            row = bundles[key]
            return (row["download_url"], row["bundle_type"], row.get("provider_digest"))

        selected_asset = max(
            keys,
            key=lambda key: (
                key in historical_inputs,
                key in input_bundles,
                "latest" in bundles[key]["channels"],
                bool(bundles[key]["channels"]),
            ),
        )
        candidates = [key for key in keys if asset(key) == asset(selected_asset)]

        def observed_rank(key):
            row = bundles[key]
            return (
                timestamp_rank(row.get("patch_refresh_attempted_at")),
                "latest" in row["channels"],
                bool(row["channels"]),
            )

        observed = [key for key in candidates if key in input_bundles and bundles[key]["file_hash"]]
        if observed:
            # A successful download establishes which binary is at this URL,
            # even when parsing it fails. Old proof applies only to that hash.
            observed_hash = bundles[max(observed, key=observed_rank)]["file_hash"]
            candidates = [key for key in candidates if bundles[key]["file_hash"] == observed_hash]
        selected = max(
            candidates,
            key=lambda key: (
                key in input_bundles,
                bundles[key]["metadata_status"] == "verified",
                "latest" in bundles[key]["channels"],
                bool(bundles[key]["channels"]),
            ),
        )
        previous_keys = [key for key in keys if key in history]
        retained = (
            max(
                previous_keys,
                key=lambda key: (
                    bool(history[key]["bundle"].get("is_latest")),
                    bool(history[key]["bundle"].get("channels")),
                    history[key]["bundle"]["metadata_status"] == "verified",
                ),
            )
            if previous_keys
            else selected
        )
        bundle = bundles[selected].copy()
        # Integrations are channel metadata, independent of which cache supplied
        # the selected binary's extraction proof.
        current = [
            key
            for key in keys
            if key in input_bundles
            and bundles[key]["channels"]
            and asset(key) == asset(selected_asset)
        ]
        if current:
            bundle["integrations"] = bundles[max(current, key=observed_rank)]["integrations"]
        bundle["id"] = retained
        bundle["channels"] = sorted(
            {channel for key in keys for channel in bundles[key]["channels"]}
        )
        bundle["import_urls"] = {
            channel: url for key in keys for channel, url in bundles[key]["import_urls"].items()
        }
        canonical[retained] = bundle
        canonical_details[retained] = details.get(selected, [])
        if selected in input_bundles:
            canonical_inputs.add(retained)
    bundles, details, input_bundles = canonical, canonical_details, canonical_inputs
    for source in sources.values():
        source["bundles"] = [
            key for key, bundle in bundles.items() if bundle["source_id"] == source["id"]
        ]

    # History can survive without a restored extraction input. Runtime changes
    # must still make its paused failures eligible in the published catalog.
    for bundle in bundles.values():
        if (
            bundle["metadata_status"] == "verified"
            and bundle.get("patch_metadata_schema_version") != PATCH_METADATA_SCHEMA_VERSION
        ):
            bundle.update(metadata_status="unverified", patch_count=0, need_patches_update=True)
        if bundle.get("extraction_terminal"):
            status = {
                "terminal": True,
                "status": bundle["extraction_status"],
                "file_hash": bundle["file_hash"],
                "bundle_type": bundle["bundle_type"],
                "provider_digest": bundle.get("extracted_provider_digest"),
                "failure_fingerprint": bundle.get("patcher_failure_fingerprint"),
                "runtime_config_hash": bundle.get("patcher_failure_config_hash"),
            }
            if not paused_failure(root, status, bundle, bundle["bundle_type"]):
                bundle.update(extraction_terminal=False, need_patches_update=True)

    # Upstream ranks releases separately for stable and prerelease, across
    # formats. Channel pointers continue to reflect their configured choices.
    def release_time(bundle):
        try:
            parsed = datetime.fromisoformat(str(bundle.get("created_at")).replace("Z", "+00:00"))
            return (
                parsed.replace(tzinfo=UTC).timestamp()
                if parsed.tzinfo is None
                else parsed.timestamp()
            )
        except (TypeError, ValueError, OverflowError):
            return float("-inf")

    def latest_rank(bundle):
        # Fresh runners restore all retained assets. Keep the published choice
        # on ties, unless discovery supplied a replacement input this run.
        return (
            release_time(bundle),
            bool(bundle["channels"]),
            bundle["id"] in input_bundles,
            bool(history.get(bundle["id"], {}).get("bundle", {}).get("is_latest")),
        )

    newest = {}
    for bundle in bundles.values():
        if not sources[bundle["source_id"]]["enabled"]:
            continue
        bundle["is_latest"] = False
        category = (bundle["source_id"], bool(bundle["is_prerelease"]))
        current = newest.get(category)
        if current is None or latest_rank(bundle) > latest_rank(current):
            newest[category] = bundle
    for bundle in newest.values():
        bundle["is_latest"] = True
    identifiers = read_json(output / "ids.json", {})
    next_ids = {table: max(mapping.values(), default=0) for table, mapping in identifiers.items()}

    def numeric_id(table, key):
        mapping = identifiers.setdefault(table, {})
        if key not in mapping:
            next_ids[table] = next_ids.get(table, 0) + 1
            mapping[key] = next_ids[table]
        return mapping[key]

    for source in sorted(sources.values(), key=lambda item: item["id"]):
        source["legacy_id"] = numeric_id("source", source["id"])
        source["source_metadatum"].update(
            id=numeric_id("source_metadata", source["id"]), source_fk=source["legacy_id"]
        )
    for bundle in sorted(bundles.values(), key=lambda item: item["id"]):
        bundle["legacy_id"] = numeric_id("bundle", bundle["id"])
    summaries = []
    for bundle in bundles.values():
        files_name = f"bundles/{bundle['id']}.json"
        # Predicates, text extrema and stream cursors use this shared index.
        # Keep the same description as the detail response for SQL comparisons.
        summary = {**bundle, "detail_file": files_name}
        summaries.append(summary)
    files = {"sources.json": list(sources.values()), "bundles.json": summaries}
    files.update({f"bundles/{key}.json": value for key, value in bundles.items()})
    index = {"packages": {}, "bundles": {}, "patch_ids": {}, "pages": []}
    search = {str(bucket): {} for bucket in range(16)}
    app_versions, rows = {}, []
    for identity, patches in sorted(details.items()):
        for position, patch in enumerate(patches):
            packages = packages_for(patch)
            rows.append(
                {
                    **patch,
                    "name": patch.get("name"),
                    "id": f"{identity}:{position}",
                    "legacy_id": numeric_id("patch", f"{identity}:{position}"),
                    "bundle_id": identity,
                    "source_id": bundles[identity]["source_id"],
                    "packages": packages,
                    "metadata_status": bundles[identity]["metadata_status"],
                    "patch_metadata_version": bundles[identity]["patch_metadata_version"],
                }
            )
            for package in packages:
                app_versions.setdefault(package["name"], set()).update(
                    str(v) for v in package["versions"]
                )
    package_records = {}
    for row in rows:
        for package in row["packages"]:
            for version in package["versions"] or [None]:
                key = json.dumps([package["name"], version], separators=(",", ":"))
                package_records[key] = {
                    "id": numeric_id("package", key),
                    "name": package["name"],
                    "version": version,
                }
    files["package-records.json"] = sorted(package_records.values(), key=lambda item: item["id"])
    files["ids.json"] = identifiers
    run_metadata = read_json(root / "internal/cache/bundle-run-metadata.json", {})
    prior_jobs = (
        read_json(output / previous_path / "refresh-jobs.json", []) if previous_path else []
    )
    timestamp = run_metadata.get("generated_at")
    progress = read_json(root / "internal/cache/refresh-jobs.json", [])
    jobs = prior_jobs
    if timestamp and not progress:
        job_id = digest(timestamp.encode())[:24]
        jobs = [item for item in jobs if item["job_id"] != job_id]
        jobs.append(
            {
                "id": numeric_id("refresh_jobs", job_id),
                "job_id": job_id,
                "job_type": "BUNDLES",
                "status": run_metadata.get("status", "COMPLETED"),
                "started_at": run_metadata.get("started_at", timestamp),
                "completed_at": timestamp,
                "error": run_metadata.get("error"),
            }
        )
    by_id = {row["job_id"]: row for row in jobs}
    for row in progress:
        by_id[row["job_id"]] = {**row, "id": numeric_id("refresh_jobs", row["job_id"])}
    files["refresh-jobs.json"] = [
        {**row, "status": "STARTED" if row["status"] in {"PENDING", "RUNNING"} else row["status"]}
        for row in by_id.values()
    ]
    rows.sort(key=lambda row: row["legacy_id"])
    try:
        from scripts.catalog_statistics import patch_statistics
    except ModuleNotFoundError:
        from catalog_statistics import patch_statistics
    public_bundles = {
        key: value for key, value in bundles.items() if sources[value["source_id"]]["enabled"]
    }
    files["patch-statistics.json"] = patch_statistics(
        [row for row in rows if row["bundle_id"] in public_bundles],
        public_bundles,
        config.get("postgres_locale", "en_US.utf8"),
    )
    page_size = config.get("page_size", 100)
    for start in range(0, len(rows), page_size):
        page_id = f"patches/{start // page_size:05d}.json"
        page = rows[start : start + page_size]
        files[page_id] = page
        index["pages"].append(page_id)
        for row in page:
            if row["bundle_id"] in public_bundles:
                index["patch_ids"][str(row["legacy_id"])] = [page_id]
            index["bundles"].setdefault(row["bundle_id"], set()).add(page_id)
            for package in row["packages"]:
                index["packages"].setdefault(package["name"], set()).add(page_id)
            for gram in grams((row.get("name") or "") + " " + (row.get("description") or "")):
                search[str(ord(gram[0]) % 16)].setdefault(gram, set()).add(page_id)
    for bucket, values in search.items():
        files[f"search/{bucket}.json"] = {
            key: sorted(value) for key, value in sorted(values.items())
        }
    for group in ("packages", "bundles"):
        index[group] = {key: sorted(value) for key, value in sorted(index[group].items())}
    files["patch-index.json"] = index
    files["packages.json"] = [
        {"name": name, "versions": sorted(versions)}
        for name, versions in sorted(app_versions.items())
    ]
    files["history.json"] = {
        key: {"bundle": value, "patches": details.get(key, [])} for key, value in bundles.items()
    }
    files["availability.json"] = {"missing": missing, "retired_history": retired}
    payloads = {name: encoded(value) for name, value in files.items()}
    generation = digest(encoded({name: digest(value) for name, value in payloads.items()}))[:24]
    snapshot = f"snapshots/{generation}"
    target = output / snapshot
    target.mkdir(parents=True, exist_ok=True)
    for name, value in payloads.items():
        destination = target / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists() or destination.read_bytes() != value:
            destination.write_bytes(value)
    manifest = {
        "schema_version": 1,
        "generation": generation,
        "snapshot": snapshot,
        "files": {
            name: {"sha256": digest(value), "bytes": len(value)}
            for name, value in payloads.items()
            if name != "history.json"
        },
        "counts": {"sources": len(sources), "bundles": len(bundles), "patches": len(rows)},
    }
    # Retain the immutable Git anchor when a rebuild produces the same files.
    # New generations receive their anchor only after their snapshot is committed.
    reference = previous.get("snapshot_ref")
    if previous.get("generation") == generation and isinstance(reference, str):
        if re.fullmatch(r"[a-f0-9]{40}", reference):
            manifest["snapshot_ref"] = reference
    plan = retention_plan(output, snapshot, previous_path)
    ids_temp = output / "ids.tmp"
    ids_temp.write_bytes(encoded(identifiers))
    ids_temp.replace(output / "ids.json")
    temp = output / "manifest.tmp"
    temp.write_bytes(encoded(manifest))
    temp.replace(output / "manifest.json")
    apply_retention(output, plan)
    print(f"Catalog {generation}: {manifest['counts']}")
    return manifest


def build_site(root=ROOT):
    destination = root / "site-dist"
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(root / "web", destination)
    shutil.copytree(root / "shared", destination / "shared")
    output = root / "database"
    manifest = read_json(output / "manifest.json")
    public = destination / "database"
    public.mkdir()
    (public / "manifest.json").write_bytes(encoded(manifest))
    for snapshot in published_snapshots(output, manifest["snapshot"]):
        shutil.copytree(
            snapshot,
            public / "snapshots" / snapshot.name,
            ignore=shutil.ignore_patterns("history.json"),
        )
    config = read_json(root / "config/site.json")
    (destination / "config.json").write_bytes(encoded(config))
    (destination / "config").mkdir(exist_ok=True)
    (destination / "config/git-hosts.json").write_bytes(encoded(hosts(root)))
    (destination / "CNAME").write_text(urlparse(config["website"]).hostname + "\n")
    (destination / ".nojekyll").touch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", action="store_true")
    parser.add_argument(
        "--prepare", action="store_true", help="Restore private extraction inputs only"
    )
    args = parser.parse_args()
    if args.prepare:
        restore_catalog_cache()
        raise SystemExit(0)
    build_database()
    if args.site:
        build_site()
