import requests

# URL for the commits page
url = "https://api.github.com/repos/jman-github/revanced-patch-bundles/commits"
response = requests.get(url)
commits = response.json()

# Find the latest commit URL made by "github-actions[bot]"
latest_commit_url = None
for commit in commits:
    if commit['author']['login'] == "github-actions[bot]":
        latest_commit_url = commit['html_url']
        break

if latest_commit_url:
    print(f"[View Commit]({latest_commit_url})")
else:
    print("No commits found.")