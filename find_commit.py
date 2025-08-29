import os
import requests


def main():
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not repo or "/" not in repo:
        print("Invalid GITHUB_REPOSITORY")
        return
    url = f"https://api.github.com/repos/{repo}/commits"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        commits = response.json()
    except (requests.RequestException, ValueError) as e:
        print(e)
        return
    latest_commit_url = None
    for commit in commits:
        if commit.get("author", {}).get("login") == "github-actions[bot]":
            latest_commit_url = commit.get("html_url")
            break
    if latest_commit_url:
        with open("commit-link.txt", "w") as file:
            file.write(f"[View Commit]({latest_commit_url})")
    else:
        print("No commits found")


if __name__ == "__main__":
    main()
