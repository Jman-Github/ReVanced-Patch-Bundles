import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

METADATA_PATH = Path("bundle-run-metadata.json")
CHANGELOG_PATH = Path("bundle-changelog.md")


def load_metadata() -> dict[str, dict[str, str]]:
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
        line.lstrip("-*•").strip()
        for line in lines
        if line.startswith(("-", "*", "•"))
    ]
    if bullet_lines:
        selected = bullet_lines[:max_items]
        return "<br>".join(f"- {item}" for item in selected if item)

    description = " ".join(lines)
    if len(description) > max_chars:
        description = description[: max_chars - 1].rstrip() + "…"
    return description


def format_timestamp(value: str | None) -> str:
    if not value:
        return "Unknown"
    try:
        # Attempt to normalise common timestamp formats and ensure UTC suffix.
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")  # noqa: UP017


def read_git(rev, path):
    try:
        return subprocess.check_output(
            ["git", "show", f"{rev}:{path}"],
            text=True,
        )
    except subprocess.CalledProcessError:
        return ""

def resolve_path(path):
    if "/" in path:
        return path
    try:
        matches = subprocess.check_output(
            ["git", "ls-files", f"**/{path}"],
            text=True,
        ).splitlines()
    except subprocess.CalledProcessError:
        matches = []
    if not matches:
        return None
    exact = [item for item in matches if item.endswith("/" + path)]
    return exact[0] if exact else matches[0]

def get_version(s):
    if not s:
        return None
    try:
        data = json.loads(s)
        for k in ["version", "Version", "bundleVersion", "patchesVersion", "latestVersion"]:
            if isinstance(data, dict) and k in data and isinstance(data[k], str):
                return data[k]
    except (json.JSONDecodeError, TypeError):
        return None
    m = re.search(r'"(?:version|Version|latestVersion)"\s*:\s*"([^"]+)"', s)
    return m.group(1) if m else None

def write_env(key, value):
    path = os.environ.get("GITHUB_ENV")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{key}={value}\n")

try:
    with open("changed_files.txt", encoding="utf-8") as fh:
        changed = [line.strip() for line in fh if line.strip()]
except OSError:
    changed = []

targets = [n for n in changed if n.endswith("-patches-bundle.json")]

if not targets:
    write_env("has_bundle_updates", "false")
    sys.exit(0)

metadata = load_metadata()
lines: list[str] = []
changelog_rows: list[str] = []

for path in targets:
    repo_path = resolve_path(path)
    if not repo_path:
        continue
    new = read_git("HEAD", repo_path)
    old = read_git("HEAD~1", repo_path)
    v_new = get_version(new) or "?"
    v_old = get_version(old) or "?"
    name = repo_path.rsplit("/", 1)[-1]
    bundle_key = name.replace('-patches-bundle.json', '')
    lines.append(f"{bundle_key}: {v_old} ---> {v_new}")

    metadata_entry = metadata.get(bundle_key)
    if isinstance(metadata_entry, dict):
        patches_raw = metadata_entry.get("patches")
        patches_meta = patches_raw if isinstance(patches_raw, dict) else {}
        integrations_raw = metadata_entry.get("integrations")
        integrations_meta = integrations_raw if isinstance(integrations_raw, dict) else {}

        patch_summary = summarize_notes(str(patches_meta.get("notes") or ""))
        published = format_timestamp(patches_meta.get("published_at"))
        release_url = patches_meta.get("release_url") or ""

        highlight_parts: list[str] = [patch_summary]
        if release_url:
            highlight_parts.append(f"[Full notes]({release_url})")

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
        highlight = "<br>".join(part for part in highlight_parts if part)
    else:
        published = "Unknown"
        highlight = "No metadata captured for this bundle update."

    changelog_rows.append(
        f"| `{bundle_key}` | `{v_old} → {v_new}` | {published} | {highlight} |"
    )

if not lines:
    write_env("has_bundle_updates", "false")
    sys.exit(0)

with open("updated-bundles.txt", "w", encoding="utf-8") as out:
    out.write("\n".join(lines))

timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")  # noqa: UP017
changelog_header = [
    "# Patch Bundle Updates",
    "",
    f"Generated: {timestamp}",
    "",
    "| Bundle | Version | Released | Highlights |",
    "|--------|---------|----------|------------|",
]
CHANGELOG_PATH.write_text("\n".join(changelog_header + changelog_rows) + "\n", encoding="utf-8")

write_env("has_bundle_updates", "true")

print("\n".join(lines))
