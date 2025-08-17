from __future__ import annotations

import base64
import os
import sys
from typing import Tuple

import requests


def _get_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {os.environ['GIT_TOKEN']}",
        "Accept": "application/vnd.github+json",
    }


def _fetch_readme() -> Tuple[str, str]:
    branch = os.environ.get("TARGET_BRANCH") or os.environ.get("GITHUB_REF_NAME", "bundles")
    response = requests.get(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/contents/README.md",
        headers=_get_headers(),
        params={"ref": branch},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return base64.b64decode(data["content"]).decode("utf-8"), data["sha"]


def _apply_update(readme: str, artifact_url: str) -> str:
    lines = readme.splitlines()
    try:
        idx = lines.index("#### 📩 Latest Download:") + 1
        if idx < len(lines):
            lines[idx] = artifact_url
        else:
            lines.append(artifact_url)
    except ValueError:
        lines.append("#### 📩 Latest Download:")
        lines.append(artifact_url)
    return "\n".join(lines) + "\n"


def update_readme(artifact_url: str) -> None:
    readme, sha = _fetch_readme()
    new_content = _apply_update(readme, artifact_url)
    if new_content == readme:
        print("README already up to date.")
        return

    data = {
        "message": "feat: Update manager download link to latest",
        "content": base64.b64encode(new_content.encode()).decode("utf-8"),
        "sha": sha,
        "branch": os.environ.get("TARGET_BRANCH") or os.environ.get("GITHUB_REF_NAME", "bundles"),
        "committer": {
            "name": "github-actions[bot]",
            "email": "41898282+github-actions[bot]@users.noreply.github.com",
        },
        "author": {
            "name": "github-actions[bot]",
            "email": "41898282+github-actions[bot]@users.noreply.github.com",
        },
    }
    response = requests.put(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/contents/README.md",
        headers=_get_headers(),
        json=data,
        timeout=30,
    )
    if response.status_code not in {200, 201}:
        raise RuntimeError(f"Failed to update README: {response.status_code} {response.text}")
    print("README updated successfully.")


if __name__ == "__main__":
    update_readme(sys.argv[1])
