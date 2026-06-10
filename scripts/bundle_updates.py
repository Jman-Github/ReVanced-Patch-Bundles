"""Utilities for discovering bundle version changes.

This module centralizes the logic that inspects the git history and extracts
version transitions for generated ``*-patches-bundle.json`` files. Both
``build_updated_bundles.py`` and ``build_summary.py`` import these helpers to
ensure they stay in sync.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CHANGED_FILES_PATH = PROJECT_ROOT / "changed_files.txt"
_GIT_BIN = shutil.which("git")

if _GIT_BIN is None:  # pragma: no cover - environment issue
    raise RuntimeError("git executable not found in PATH")

GIT_BIN = _GIT_BIN


@dataclass(slots=True)
class BundleUpdate:
    """Represents a version transition for a single bundle artifact."""

    name: str
    repo_path: str
    old_version: str | None
    new_version: str | None

    def format_line(self, missing: str = "?") -> str:
        """Return the canonical summary line used in release artifacts."""

        previous = self.old_version or missing
        current = self.new_version or missing
        return f"{self.name}: {previous} ---> {current}"


def _read_lines(path: Path) -> list[str]:
    if not path.is_file():
        return []
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _git_output(*args: str) -> str:
    """Return stdout for a git invocation using an absolute executable path."""

    return cast(str, subprocess.check_output([GIT_BIN, *args], text=True, cwd=str(PROJECT_ROOT)))


def _read_git(rev: str, path: str) -> str:
    try:
        return _git_output("show", f"{rev}:{path}")
    except subprocess.CalledProcessError:
        return ""


def _resolve_path(path: str) -> str | None:
    if "/" in path:
        return path
    try:
        matches = _git_output("ls-files", f"**/{path}").splitlines()
    except subprocess.CalledProcessError:
        matches = []
    if not matches:
        return None
    exact = [item for item in matches if item.endswith("/" + path)]
    return exact[0] if exact else matches[0]


def _extract_version(raw: str) -> str | None:
    if not raw:
        return None
    try:
        data = json.loads(raw)
        if isinstance(data, dict):
            for key in ("version", "Version", "bundleVersion", "patchesVersion", "latestVersion"):
                value = data.get(key)
                if isinstance(value, str):
                    return value
    except (json.JSONDecodeError, TypeError):
        pass

    match = re.search(r'"(?:version|Version|latestVersion)"\s*:\s*"([^"]+)"', raw)
    return match.group(1) if match else None


def _iter_bundle_targets(changed_files: Iterable[str]) -> Iterable[str]:
    for candidate in changed_files:
        if candidate.endswith("-patches-bundle.json"):
            yield candidate


def collect_bundle_updates(
    changed_files_path: Path | str = CHANGED_FILES_PATH,
) -> list[BundleUpdate]:
    """Return bundle updates discovered in the provided ``changed_files`` list."""

    path = Path(changed_files_path)
    changed = _read_lines(path)
    updates: list[BundleUpdate] = []
    for target in _iter_bundle_targets(changed):
        repo_path = _resolve_path(target)
        if not repo_path:
            continue
        new_content = _read_git("HEAD", repo_path)
        old_content = _read_git("HEAD~1", repo_path)
        filename = repo_path.rsplit("/", 1)[-1]
        bundle_name = filename.replace("-patches-bundle.json", "")
        updates.append(
            BundleUpdate(
                name=bundle_name,
                repo_path=repo_path,
                old_version=_extract_version(old_content),
                new_version=_extract_version(new_content),
            )
        )
    return updates
