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
    with open('commit_link.txt', 'w') as f:
        f.write(f"\n[View Commit]({latest_commit_url})\n")
else:
    print("No commits found.")

# Save the list of changed files to a file
changed_files = subprocess.check_output(['git', 'diff', '--name-only', 'HEAD^', '--', '*.json']).decode('utf-8').splitlines()

with open('changed_files.txt', 'w') as f:
    f.write(f"\n[View Commit]({latest_commit_url})\n")
    f.write("Changed files:\n")
    for file in changed_files:
        f.write(f"- {file}\n")
