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
    changed_files = []
    for file in commit['files']:
        if file['filename'].endswith('.json'):
            changed_files.append(file['filename'])

    with open('changed_files.txt', 'w') as f:
        if changed_files:
            f.write("Changed .json files:\n")
            for file_name in changed_files:
                f.write(f"- {file_name}\n")
        else:
            f.write("No .json files changed.\n")

        f.write(f"\nLatest commit by github-actions[bot]: [{latest_commit_url}]({latest_commit_url})\n")
        print(f"Changed .json files:")
        for file_name in changed_files:
            print(f"- {file_name}")
        print(f"\nLatest commit by github-actions[bot]: [{latest_commit_url}]({latest_commit_url})")
else:
    print("No commits found.")
