import requests

# URL for the commits page
url = "https://api.github.com/repos/jman-github/revanced-patch-bundles/commits"
response = requests.get(url)
commits = response.json()

# Find the latest commit made by "github-actions[bot]"
latest_commit_url = None
for commit in commits:
    if commit['commit']['author']['name'] == "github-actions[bot]":
        latest_commit_url = commit['html_url']
        break

if latest_commit_url:
    with open('changed_files.txt', 'w') as f:
        f.write(f"\n[View Commit]({latest_commit_url})\n")
else:
    print("No commits found.")
