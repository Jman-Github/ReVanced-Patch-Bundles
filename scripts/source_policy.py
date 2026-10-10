"""Canonical source switches shared by discovery, extraction and catalog generation."""

import json

try:
    from scripts.git_hosts import normalize_source
except ModuleNotFoundError:
    from git_hosts import normalize_source


def disabled_sources(inventory, root):
    result = {}
    for settings in inventory.values():
        if not isinstance(settings, dict) or not settings.get("patches"):
            continue
        disabled = settings.get("disabled", False)
        if not isinstance(disabled, bool):
            raise ValueError("Source disabled must be a boolean")
        if disabled:
            result[normalize_source(settings["patches"], root).lower()] = (
                settings.get("unavailable_reason") or "Disabled by the registry maintainer"
            )
    return result


def write_extraction_policy(root):
    import re

    inventory = json.loads((root / "config/sources.json").read_text(encoding="utf-8"))
    disabled = unavailable_sources(inventory, root)
    folders = {
        re.sub(r"-(latest|stable|dev)$", "", key) + "-patch-bundles"
        for key, settings in inventory.items()
        if isinstance(settings, dict)
        and settings.get("patches")
        and normalize_source(settings["patches"], root).lower() in disabled
    }
    registry = root / "internal/cache/history/sources.json"
    if registry.exists():
        history = json.loads(registry.read_text(encoding="utf-8"))
        folders.update(
            settings["cache_path"].split("/")[-2]
            for settings in history.values()
            if isinstance(settings, dict)
            and settings.get("patches")
            and settings.get("cache_path")
            and normalize_source(settings["patches"], root).lower() in disabled
        )
    path = root / "internal/cache/disabled-extraction.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(sorted(folders)), encoding="utf-8")
    temp.replace(path)
    return folders


PERMANENT_STATUS = {
    404: "404: Not Found",
    410: "410: Gone",
    451: "451: Unavailable For Legal Reasons",
}


def source_availability(root):
    try:
        value = json.loads((root / "database/source-availability.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return (
        {key: reason for key, reason in value.items() if isinstance(reason, str)}
        if isinstance(value, dict)
        else {}
    )


def save_availability(root, value):
    path = root / "database/source-availability.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def unavailable_sources(inventory, root):
    return {**source_availability(root), **disabled_sources(inventory, root)}
