import os
import requests

repo = "Jman-Github/ReVanced-Patch-Bundles"
author = "github-actions[bot]"

files = os.popen('git diff --name-only HEAD^ -- "*.json"').read().splitlines()

for file in files:
    url = f"https://api.github.com/repos/{repo}/commits?author={author}&path={file}"
    response = requests.get(url).json()
    if response:
        commit_sha = response[0]['sha']
        print(f"- [{file}](https://github.com/{repo}/commit/{commit_sha})")
    else:
        print(f"No commits found for {file}")
