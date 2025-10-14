import os
import sys
from collections.abc import Iterable, Mapping
from datetime import UTC, datetime, timedelta
from typing import Any

import httpx

API_VERSION = "2022-11-28"
HTTP_TIMEOUT = httpx.Timeout(30.0)


def _parse_iso_z(dt: str | None) -> datetime | None:
    if not dt:
        return None
    try:
        if dt.endswith("Z"):
            dt = dt[:-1] + "+00:00"
        return datetime.fromisoformat(dt).astimezone(UTC)
    except Exception:
        return None


def _fmt_iso_z(dt: datetime) -> str:
    return (
        dt.astimezone(UTC)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _gh_get(
    client: httpx.Client, url: str, token: str | None, params: Mapping[str, Any] | None = None
) -> httpx.Response:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = client.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response


def _first_bot_commit_in(
    commits: Iterable[Mapping[str, Any]], actor_login: str
) -> Mapping[str, Any] | None:
    for commit in commits:
        author = commit.get("author") or {}
        commit_block = commit.get("commit") or {}
        committer_block = commit_block.get("committer") or {}
        author_name = (commit_block.get("author") or {}).get("name") or ""
        committer_name = committer_block.get("name") or ""
        if (
            author.get("login") == actor_login
            or author_name == actor_login
            or committer_name == actor_login
        ):
            return commit
    return None


def _commit_timestamp(commit: Mapping[str, Any]) -> datetime | None:
    commit_block = commit.get("commit") or {}
    committer_block = commit_block.get("committer") or {}
    author_block = commit_block.get("author") or {}
    if committer_block.get("date"):
        return _parse_iso_z(committer_block.get("date"))
    if author_block.get("date"):
        return _parse_iso_z(author_block.get("date"))
    return None


def _commit_message(commit: Mapping[str, Any]) -> str:
    return ((commit.get("commit") or {}).get("message") or "").strip()


def _commit_in_branch(
    client: httpx.Client,
    repo: str,
    token: str | None,
    sha: str,
    branch: str,
) -> bool:
    """
    Verify that `sha` is reachable from `branch` by using the compare API.
    If base=sha and head=branch, the commit is in branch if status is one of:
    'behind', 'identical' (not 'diverged').
    """
    url = f"https://api.github.com/repos/{repo}/compare/{sha}...{branch}"
    try:
        response = _gh_get(client, url, token)
        payload = response.json()
    except httpx.HTTPError:
        return False
    if not isinstance(payload, Mapping):
        return False
    status = payload.get("status", "")
    return status in ("behind", "identical")


def _get_commit(client: httpx.Client, repo: str, token: str | None, sha: str) -> dict[str, Any]:
    url = f"https://api.github.com/repos/{repo}/commits/{sha}"
    payload = _gh_get(client, url, token).json()
    if not isinstance(payload, dict):
        raise RuntimeError(f"Unexpected payload fetching commit {sha}.")
    return payload


def _validate_commit(
    client: httpx.Client,
    commit: Mapping[str, Any],
    *,
    repo: str,
    branch: str,
    token: str | None,
    required_prefix: str,
    min_commit_time: datetime | None,
    max_future_pad: datetime | None,
    max_age_minutes: int,
) -> Mapping[str, Any]:
    if required_prefix and not _commit_message(commit).startswith(required_prefix):
        raise RuntimeError("Commit message does not satisfy REQUIRED_COMMIT_MSG_PREFIX.")

    commit_timestamp = _commit_timestamp(commit)
    if not commit_timestamp:
        raise RuntimeError("Commit is missing a timestamp; refusing to proceed.")
    if min_commit_time and commit_timestamp < min_commit_time:
        raise RuntimeError(
            "Commit is older than "
            f"{max_age_minutes} minutes relative to the run; refusing to proceed."
        )
    if max_future_pad and commit_timestamp > max_future_pad:
        raise RuntimeError("Commit timestamp appears after allowable pad; refusing to proceed.")

    sha = commit.get("sha")
    if not sha:
        raise RuntimeError("Commit is missing its SHA; refusing to proceed.")
    if not _commit_in_branch(client, repo, token, sha, branch):
        raise RuntimeError(f"Commit {sha} is not reachable from branch '{branch}'.")

    return commit


def _resolve_by_explicit_sha(
    client: httpx.Client,
    repo: str,
    token: str | None,
    branch: str,
    actor_login: str,
    required_prefix: str,
    min_commit_time: datetime | None,
    max_future_pad: datetime | None,
    max_age_minutes: int,
    explicit_sha: str,
) -> Mapping[str, Any]:
    try:
        commit = _get_commit(client, repo, token, explicit_sha)
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Failed to fetch commit {explicit_sha}: {exc}") from exc

    if not _first_bot_commit_in([commit], actor_login):
        raise RuntimeError("Explicit SHA is not authored by github-actions[bot].")

    return _validate_commit(
        client,
        commit,
        repo=repo,
        branch=branch,
        token=token,
        required_prefix=required_prefix,
        min_commit_time=min_commit_time,
        max_future_pad=max_future_pad,
        max_age_minutes=max_age_minutes,
    )


def _resolve_by_window(
    client: httpx.Client,
    repo: str,
    token: str | None,
    branch: str,
    actor_login: str,
    required_prefix: str,
    min_commit_time: datetime | None,
    max_future_pad: datetime | None,
    max_age_minutes: int,
    since_dt: datetime | None,
    until_dt: datetime | None,
) -> Mapping[str, Any]:
    base_url = f"https://api.github.com/repos/{repo}/commits"

    params: dict[str, Any] = {"sha": branch, "per_page": 100}
    if since_dt:
        params["since"] = _fmt_iso_z(since_dt)
    if until_dt:
        params["until"] = _fmt_iso_z(until_dt)

    try:
        payload = _gh_get(client, base_url, token, params=params).json()
    except httpx.HTTPError as exc:
        raise RuntimeError(f"Error fetching commits: {exc}") from exc

    if not isinstance(payload, list):
        raise RuntimeError("Unexpected payload while fetching commits.")
    commits: list[dict[str, Any]] = [item for item in payload if isinstance(item, dict)]

    match = _first_bot_commit_in(commits, actor_login)
    if not match:
        raise RuntimeError("No github-actions[bot] commit found for the triggering run window.")

    return _validate_commit(
        client,
        match,
        repo=repo,
        branch=branch,
        token=token,
        required_prefix=required_prefix,
        min_commit_time=min_commit_time,
        max_future_pad=max_future_pad,
        max_age_minutes=max_age_minutes,
    )


def main() -> None:
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo or "/" not in repo:
        print("Invalid GITHUB_REPOSITORY", file=sys.stderr)
        sys.exit(1)

    token = os.environ.get("GITHUB_TOKEN")
    branch = os.environ.get("TARGET_BRANCH", "bundles")
    actor_login = os.environ.get("ACTOR_LOGIN", "github-actions[bot]")
    strict = os.environ.get("STRICT_TO_TRIGGERING_RUN", "true").lower() == "true"
    required_prefix = os.environ.get("REQUIRED_COMMIT_MSG_PREFIX", "").strip()
    explicit_sha = (os.environ.get("COMMIT_SHA") or "").strip()

    run_started_at = _parse_iso_z(os.environ.get("WORKFLOW_RUN_STARTED_AT"))
    run_updated_at = _parse_iso_z(os.environ.get("WORKFLOW_RUN_UPDATED_AT"))

    try:
        max_age_minutes = int(os.environ.get("MAX_AGE_MINUTES", "2"))
    except ValueError:
        max_age_minutes = 2

    if strict and not (run_started_at and run_updated_at):
        print(
            "Strict mode: missing WORKFLOW_RUN_* timestamps; cannot match to a specific run.",
            file=sys.stderr,
        )
        sys.exit(1)

    since_dt = (
        run_started_at - timedelta(minutes=2)
        if run_started_at
        else None
    )
    until_dt = (
        run_updated_at + timedelta(minutes=2)
        if run_updated_at
        else None
    )
    min_commit_time = (
        run_updated_at - timedelta(minutes=max_age_minutes)
        if run_updated_at
        else None
    )
    max_future_pad = (
        run_updated_at + timedelta(minutes=5)
        if run_updated_at
        else None
    )

    try:
        with httpx.Client(timeout=HTTP_TIMEOUT) as client:
            if explicit_sha:
                commit = _resolve_by_explicit_sha(
                    client,
                    repo=repo,
                    token=token,
                    branch=branch,
                    actor_login=actor_login,
                    required_prefix=required_prefix,
                    min_commit_time=min_commit_time,
                    max_future_pad=max_future_pad,
                    max_age_minutes=max_age_minutes,
                    explicit_sha=explicit_sha,
                )
            else:
                commit = _resolve_by_window(
                    client,
                    repo=repo,
                    token=token,
                    branch=branch,
                    actor_login=actor_login,
                    required_prefix=required_prefix,
                    min_commit_time=min_commit_time,
                    max_future_pad=max_future_pad,
                    max_age_minutes=max_age_minutes,
                    since_dt=since_dt,
                    until_dt=until_dt,
                )
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    latest_commit_url = commit.get("html_url")
    if not latest_commit_url:
        print("Matched commit has no html_url; refusing to proceed.", file=sys.stderr)
        sys.exit(1)

    with open("commit-link.txt", "w", encoding="utf-8") as handle:
        handle.write(f"[View Commit]({latest_commit_url})")

    print(f"Wrote commit link for triggering run: {latest_commit_url}")


if __name__ == "__main__":
    main()
