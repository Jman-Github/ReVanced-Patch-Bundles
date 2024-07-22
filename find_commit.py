import requests
import os

# URL for the commits page
url = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/commits"
response = requests.get(url)
commits = response.json()

# Find the latest commit URL made by "github-actions[bot]"
latest_commit_url = None
for commit in commits:
    if commit['author']['login'] == "github-actions[bot]":
        latest_commit_url = commit['html_url']
        break

if latest_commit_url:
    with open("commit-link.txt", "w") as file:
        file.write(f"[View Commit]({latest_commit_url})")
else:
    print("No commits found.")
