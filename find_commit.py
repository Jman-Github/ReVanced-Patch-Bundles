import os
import requests

repo = "Jman-Github/ReVanced-Patch-Bundles"
author = "github-actions[bot]"

files = os.popen('git diff --name-only HEAD^ -- "*.json"').read().splitlines()

for file in files:
    url = f"https://api.github.com/repos/{repo}/commits?author={author}"
    response = requests.get(url).json()
    commit_sha = None
    for commit in response:
        files_modified = [f['filename'] for f in commit['files']]
        if file in files_modified:
            commit_sha = commit['sha']
            break
    if commit_sha:
        print(f"- [{file}](https://github.com/{repo}/commit/{commit_sha})")
    else:
        print(f"No commits found for {file}")
