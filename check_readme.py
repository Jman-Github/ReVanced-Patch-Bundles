"""Check if the README contains the provided artifact URL.

This script writes ``needs_update=true`` to ``GITHUB_OUTPUT`` when the URL in the
README does not match ``artifact_url``.
"""

from __future__ import annotations

import base64
import os
import sys

import httpx


def _get_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {os.environ['GIT_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }


def _fetch_readme() -> tuple[str, str]:
    branch = os.environ.get("TARGET_BRANCH") or os.environ.get("GITHUB_REF_NAME", "bundles")
    with httpx.Client(timeout=httpx.Timeout(30.0)) as client:
        response = client.get(
            f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/contents/README.md",
            headers=_get_headers(),
            params={"ref": branch},
        )
    response.raise_for_status()
    data = response.json()
    return base64.b64decode(data["content"]).decode("utf-8"), data["sha"]


def _extract_current_url(readme: str) -> str:
    lines = readme.splitlines()
    try:
        idx = lines.index("#### 📩 Latest Download:") + 1
        return lines[idx] if idx < len(lines) else ""
    except ValueError:
        return ""


def check_readme(artifact_url: str) -> None:
    try:
        readme, _ = _fetch_readme()
        current_url = _extract_current_url(readme)
        needs_update = "true" if current_url != artifact_url else "false"
    except Exception as exc:
        print(f"Failed to check README: {exc}")
        needs_update = "true"

    with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as output_file:
        output_file.write(f"needs_update={needs_update}\n")


if __name__ == "__main__":
    check_readme(sys.argv[1])
