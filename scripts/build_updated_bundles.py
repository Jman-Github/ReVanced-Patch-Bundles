import json
import os
import sys
from pathlib import Path
from typing import Any

from bundle_updates import collect_bundle_updates

PROJECT_ROOT = Path(__file__).resolve().parents[1]
METADATA_PATH = PROJECT_ROOT / "bundle-run-metadata.json"
CHANGELOG_PATH = PROJECT_ROOT / "bundle-changelog.md"
UPDATED_BUNDLES_PATH = PROJECT_ROOT / "updated-bundles.txt"
JsonObject = dict[str, Any]


def load_metadata() -> dict[str, JsonObject]:
    if not METADATA_PATH.is_file():
        return {}
    try:
        payload = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Failed to parse {METADATA_PATH}: {exc}")
        return {}
    bundles = payload.get("bundles")
    if isinstance(bundles, dict):
        return bundles
    return {}


def _clean_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def summarize_notes(notes: str, max_items: int = 3, max_chars: int = 300) -> str:
    if not notes:
        return "No release notes provided."
    lines = _clean_lines(notes)
    if not lines:
        return "No release notes provided."
    bullet_lines = [
        line.lstrip("-*•").strip() for line in lines if line.startswith(("-", "*", "•"))
    ]
    if bullet_lines:
        selected = [item for item in bullet_lines[:max_items] if item]
        return "; ".join(selected)

    description = " ".join(lines)
    if len(description) > max_chars:
        description = description[: max_chars - 1].rstrip() + "…"
    return description


def write_env(key: str, value: str) -> None:
    path = os.environ.get("GITHUB_ENV")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{key}={value}\n")


bundle_updates = collect_bundle_updates()

if not bundle_updates:
    write_env("has_bundle_updates", "false")
    sys.exit(0)

metadata = load_metadata()
changelog_entries: list[tuple[str, str]] = []

lines = [update.format_line() for update in bundle_updates]

for update in bundle_updates:
    bundle_key = update.name

    metadata_entry = metadata.get(bundle_key)
    highlight_text = ""
    if isinstance(metadata_entry, dict):
        patches_raw = metadata_entry.get("patches")
        patches_meta: JsonObject = patches_raw if isinstance(patches_raw, dict) else {}
        integrations_raw = metadata_entry.get("integrations")
        integrations_meta: JsonObject = (
            integrations_raw if isinstance(integrations_raw, dict) else {}
        )

        patch_summary = summarize_notes(str(patches_meta.get("notes") or "")).lstrip("*")
        release_url = patches_meta.get("release_url") or ""

        highlight_parts: list[str] = []
        if patch_summary and patch_summary != "No release notes provided.":
            highlight_parts.append(patch_summary)
        release_link = f" ([Full notes]({release_url}))" if release_url else ""

        if integrations_meta:
            integration_summary = summarize_notes(str(integrations_meta.get("notes") or ""))
            if integration_summary:
                integration_version = integrations_meta.get("version")
                if integration_version:
                    integration_prefix = f"<em>Integrations ({integration_version}):</em> "
                else:
                    integration_prefix = "<em>Integrations:</em> "
                integration_link = integrations_meta.get("release_url") or ""
                detail = f"{integration_prefix}{integration_summary}"
                if integration_link:
                    detail = f"{detail} ([details]({integration_link}))"
                highlight_parts.append(detail)
        highlight_text = " ".join(part for part in highlight_parts if part).strip()
        if release_link:
            if highlight_text:
                highlight_text = f"{highlight_text}{release_link}"
            else:
                highlight_text = release_link.strip()
    else:
        highlight_text = "No release notes captured for this bundle update."

    if not highlight_text:
        highlight_text = "No release notes captured for this bundle update."

    changelog_entries.append((bundle_key, highlight_text))

if not lines:
    write_env("has_bundle_updates", "false")
    sys.exit(0)

with UPDATED_BUNDLES_PATH.open("w", encoding="utf-8") as out:
    out.write("\n".join(lines))

changelog_lines: list[str] = []
for bundle_name, summary in changelog_entries:
    changelog_lines.append(f"- {bundle_name}:")
    changelog_lines.append(summary)
    changelog_lines.append("")

CHANGELOG_PATH.write_text("\n".join(changelog_lines).rstrip() + "\n", encoding="utf-8")

write_env("has_bundle_updates", "true")

print("\n".join(lines))
