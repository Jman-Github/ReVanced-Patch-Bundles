import os
import requests

repo = "Jman-Github/ReVanced-Patch-Bundles"
author = "github-actions%5Bbot%5D"

files = os.popen('git diff --name-only HEAD^ -- "*.json"').read().splitlines()

for file in files:
    url = f"https://api.github.com/repos/{repo}/commits?author={author}&path={file}"
    commit_sha = requests.get(url).json()[0]['sha']
    print(f"- [{file}](https://github.com/{repo}/commit/{commit_sha})")
