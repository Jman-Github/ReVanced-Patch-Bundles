import os
import sys
import requests
from datetime import datetime, timedelta, timezone

API_VERSION = "2022-11-28"


def _parse_iso_z(dt: str | None) -> datetime | None:
    if not dt:
        return None
    try:
        if dt.endswith("Z"):
            dt = dt[:-1] + "+00:00"
        return datetime.fromisoformat(dt).astimezone(timezone.utc)
    except Exception:
        return None


def _fmt_iso_z(dt: datetime) -> str:
    return (
        dt.astimezone(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _gh_get(url: str, token: str | None, params: dict | None = None):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp


def _first_bot_commit_in(commits, actor_login: str) -> dict | None:
    for c in commits:
        author = c.get("author") or {}
        commit_block = c.get("commit") or {}
        committer_block = (commit_block.get("committer") or {})
        name = (commit_block.get("author") or {}).get("name") or ""
        committer_name = committer_block.get("name") or ""
        if (
            author.get("login") == actor_login
            or name == actor_login
            or committer_name == actor_login
        ):
            return c
    return None


def _commit_timestamp(commit: dict) -> datetime | None:
    cb = commit.get("commit") or {}
    committer_block = cb.get("committer") or {}
    author_block = cb.get("author") or {}
    if committer_block.get("date"):
        return _parse_iso_z(committer_block.get("date"))
    if author_block.get("date"):
        return _parse_iso_z(author_block.get("date"))
    return None


def _commit_message(commit: dict) -> str:
    return ((commit.get("commit") or {}).get("message") or "").strip()


def _commit_in_branch(repo: str, token: str | None, sha: str, branch: str) -> bool:
    """
    Verify that `sha` is reachable from `branch` by using the compare API.
    If base=sha and head=branch, the commit is in branch if status is one of:
    'behind', 'identical' (not 'diverged').
    """
    url = f"https://api.github.com/repos/{repo}/compare/{sha}...{branch}"
    try:
        r = _gh_get(url, token)
        data = r.json()
        status = data.get("status", "")
        return status in ("behind", "identical")
    except requests.RequestException:
        return False


def _get_commit(repo: str, token: str | None, sha: str) -> dict:
    url = f"https://api.github.com/repos/{repo}/commits/{sha}"
    return _gh_get(url, token).json()


def main():
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

    since_dt = (run_started_at - timedelta(minutes=2)) if run_started_at else None
    until_dt = (run_updated_at + timedelta(minutes=2)) if run_updated_at else None

    min_commit_time = run_updated_at - timedelta(minutes=max_age_minutes) if run_updated_at else None
    max_future_pad = run_updated_at + timedelta(minutes=5) if run_updated_at else None

    latest_commit_url = None
    chosen_commit = None

    if explicit_sha:
        try:
            c = _get_commit(repo, token, explicit_sha)
        except requests.RequestException as e:
            print(f"Failed to fetch commit {explicit_sha}: {e}", file=sys.stderr)
            sys.exit(1)

        if not _first_bot_commit_in([c], actor_login):
            print("Explicit SHA is not authored by github-actions[bot].", file=sys.stderr)
            sys.exit(1)

        if not _commit_in_branch(repo, token, explicit_sha, branch):
            print(f"Explicit SHA {explicit_sha} is not reachable from branch '{branch}'.", file=sys.stderr)
            sys.exit(1)

        if required_prefix and not _commit_message(c).startswith(required_prefix):
            print("Commit message does not satisfy REQUIRED_COMMIT_MSG_PREFIX.", file=sys.stderr)
            sys.exit(1)

        cdt = _commit_timestamp(c)
        if not cdt:
            print("Explicit SHA has no timestamp; refusing to proceed.", file=sys.stderr)
            sys.exit(1)

        if min_commit_time and cdt < min_commit_time:
            print(
                f"Explicit SHA commit is older than {max_age_minutes} minutes relative to the run; refusing to proceed.",
                file=sys.stderr,
            )
            sys.exit(1)

        if max_future_pad and cdt > max_future_pad:
            print("Explicit SHA commit timestamp appears after allowable pad; refusing to proceed.", file=sys.stderr)
            sys.exit(1)

        latest_commit_url = c.get("html_url")
        chosen_commit = c

    else:
        base_url = f"https://api.github.com/repos/{repo}/commits"

        def fetch_commits(since, until):
            params = {"sha": branch, "per_page": 100}
            if since:
                params["since"] = _fmt_iso_z(since)
            if until:
                params["until"] = _fmt_iso_z(until)
            return _gh_get(base_url, token, params=params).json()

        try:
            commits = fetch_commits(since_dt, until_dt)
        except requests.RequestException as e:
            print(f"Error fetching commits: {e}", file=sys.stderr)
            sys.exit(1)

        match = _first_bot_commit_in(commits, actor_login)
        if not match:
            print(
                "No github-actions[bot] commit found for the triggering run window.",
                file=sys.stderr,
            )
            sys.exit(1)

        if required_prefix and not _commit_message(match).startswith(required_prefix):
            print(
                "Found bot commit but its message does not satisfy REQUIRED_COMMIT_MSG_PREFIX.",
                file=sys.stderr,
            )
            sys.exit(1)

        cdt = _commit_timestamp(match)
        if not cdt:
            print("Matched commit has no timestamp; refusing to proceed.", file=sys.stderr)
            sys.exit(1)

        if min_commit_time and cdt < min_commit_time:
            print(
                f"Found commit is older than {max_age_minutes} minutes relative to the run; refusing to proceed.",
                file=sys.stderr,
            )
            sys.exit(1)

        if max_future_pad and cdt > max_future_pad:
            print("Found commit timestamp appears after allowable pad; refusing to proceed.", file=sys.stderr)
            sys.exit(1)

        latest_commit_url = match.get("html_url")
        chosen_commit = match

    if not latest_commit_url:
        print("Matched commit has no html_url; refusing to proceed.", file=sys.stderr)
        sys.exit(1)

    with open("commit-link.txt", "w", encoding="utf-8") as f:
        f.write(f"[View Commit]({latest_commit_url})")

    print(f"Wrote commit link for triggering run: {latest_commit_url}")


if __name__ == "__main__":
    main()
