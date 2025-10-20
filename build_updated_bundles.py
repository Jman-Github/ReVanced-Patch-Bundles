import json
import os
import re
import subprocess
import sys
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
        selected = [item for item in bullet_lines[:max_items] if item]
        return "; ".join(selected)

    description = " ".join(lines)
    if len(description) > max_chars:
        description = description[: max_chars - 1].rstrip() + "…"
    return description


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
changelog_entries: list[tuple[str, str]] = []

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
    highlight_text = ""
    if isinstance(metadata_entry, dict):
        patches_raw = metadata_entry.get("patches")
        patches_meta = patches_raw if isinstance(patches_raw, dict) else {}
        integrations_raw = metadata_entry.get("integrations")
        integrations_meta = integrations_raw if isinstance(integrations_raw, dict) else {}

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

with open("updated-bundles.txt", "w", encoding="utf-8") as out:
    out.write("\n".join(lines))

changelog_lines: list[str] = []
for bundle_name, summary in changelog_entries:
    changelog_lines.append(f"- {bundle_name}:")
    changelog_lines.append(summary)
    changelog_lines.append("")

CHANGELOG_PATH.write_text("\n".join(changelog_lines).rstrip() + "\n", encoding="utf-8")

write_env("has_bundle_updates", "true")

print("\n".join(lines))
