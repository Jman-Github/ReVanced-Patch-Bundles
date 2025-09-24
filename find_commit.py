import json
import os
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Sequence

import requests


def _normalize_sha(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_positive_int(value: Optional[str], default: int) -> int:
    if not value:
        return default
    try:
        parsed = int(str(value).strip())
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def load_processed_commits(path: str) -> List[str]:
    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, ValueError, TypeError):
        return []
    if isinstance(data, dict):
        candidates = data.get("processed")
        if isinstance(candidates, list):
            data = candidates
        else:
            data = []
    if not isinstance(data, list):
        return []
    normalized: List[str] = []
    seen = set()
    for item in data:
        if not isinstance(item, str):
            continue
        commit = _normalize_sha(item)
        if not commit or commit in seen:
            continue
        seen.add(commit)
        normalized.append(commit)
    return normalized


def save_processed_commits(path: str, commits: Iterable[str], limit: int = 100) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    normalized: List[str] = []
    seen = set()
    for commit in commits:
        key = _normalize_sha(commit)
        if not key or key in seen:
            continue
        seen.add(key)
        normalized.append(key)
    if limit <= 0:
        limit = 1
    trimmed = normalized[-limit:]
    payload = {
        "processed": trimmed,
        "updated": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
    }
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def ensure_file(path: str, content: str) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)
        if content and not content.endswith("\n"):
            handle.write("\n")


def resolve_token() -> Optional[str]:
    for key in ("GH_TOKEN", "GH_PAT", "GITHUB_TOKEN"):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return None


def fetch_commits(
    repo: str,
    branch: str,
    token: Optional[str],
    max_pages: int = 5,
    per_page: int = 100,
) -> List[Dict]:
    url = f"https://api.github.com/repos/{repo}/commits"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    commits: List[Dict] = []
    with requests.Session() as session:
        for page in range(1, max_pages + 1):
            params = {"sha": branch, "per_page": per_page, "page": page}
            response = session.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, list) or not data:
                break
            commits.extend(data)
            if len(data) < per_page:
                break
    return commits


def is_patch_bundle_commit(data: Dict) -> bool:
    commit = data.get("commit") or {}
    message = str(commit.get("message", "")).strip()
    lowered = message.lower()
    if not lowered:
        return False
    if "patch-bundles" not in lowered:
        return False
    if "update" not in lowered:
        return False
    author = data.get("author") or {}
    committer = data.get("committer") or {}
    commit_author = commit.get("author") or {}
    commit_committer = commit.get("committer") or {}
    identities = {
        str(author.get("login", "")).lower(),
        str(committer.get("login", "")).lower(),
        str(commit_author.get("name", "")).lower(),
        str(commit_committer.get("name", "")).lower(),
    }
    return "github-actions[bot]" in identities or "github-actions" in identities


def select_commit(commits: Sequence[Dict], processed: Sequence[str]) -> Optional[Dict]:
    processed_set = {_normalize_sha(item) for item in processed if _normalize_sha(item)}
    for entry in commits:
        sha = _normalize_sha(str(entry.get("sha", "")))
        if not sha or sha in processed_set:
            continue
        if not is_patch_bundle_commit(entry):
            continue
        return entry
    return None


def build_commit_entry(data: Dict) -> str:
    link = str(data.get("html_url", "")).strip()
    commit = data.get("commit") or {}
    message = str(commit.get("message", "")).strip()
    summary = message.splitlines()[0].strip() if message else ""
    parts: List[str] = []
    if link:
        parts.append(f"[View Commit]({link})")
    if summary:
        parts.append(summary)
    return "\n".join(parts)


def main() -> None:
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if not repo or "/" not in repo:
        ensure_file(os.environ.get("COMMIT_LINK_FILE", "commit-link.txt"), "")
        print("Invalid GITHUB_REPOSITORY")
        raise SystemExit(1)
    branch = os.environ.get("TARGET_BRANCH", "bundles").strip() or "bundles"
    state_file = os.environ.get("COMMIT_STATE_FILE", "commit_state/processed_commits.json").strip() or "commit_state/processed_commits.json"
    commit_file = os.environ.get("COMMIT_LINK_FILE", "commit-link.txt").strip() or "commit-link.txt"
    limit = _parse_positive_int(os.environ.get("COMMIT_STATE_LIMIT"), 256)
    processed = load_processed_commits(state_file)
    token = resolve_token()
    try:
        commits = fetch_commits(
            repo,
            branch,
            token,
            max_pages=_parse_positive_int(os.environ.get("COMMIT_FETCH_PAGES"), 5),
            per_page=_parse_positive_int(os.environ.get("COMMIT_FETCH_PER_PAGE"), 100),
        )
    except requests.RequestException as error:
        ensure_file(commit_file, "")
        save_processed_commits(state_file, processed, limit=limit)
        print(error)
        raise SystemExit(1)
    except ValueError as error:
        ensure_file(commit_file, "")
        save_processed_commits(state_file, processed, limit=limit)
        print(error)
        raise SystemExit(1)
    target = select_commit(commits, processed)
    if not target:
        ensure_file(commit_file, "")
        save_processed_commits(state_file, processed, limit=limit)
        print("No new commits found")
        return
    entry = build_commit_entry(target)
    ensure_file(commit_file, entry)
    sha = str(target.get("sha", "")).strip()
    if sha:
        processed.append(sha)
    save_processed_commits(state_file, processed, limit=limit)


if __name__ == "__main__":
    main()
