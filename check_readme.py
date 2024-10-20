import sys
import os
import requests
import base64

def check_readme(artifact_url):
    headers = {
        "Authorization": f"Bearer {os.environ['GIT_TOKEN']}",
        "Content-Type": "application/json"
    }
    response = requests.get(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/contents/README.md",
        headers=headers
    )
    if response.status_code == 200:
        readme_content = response.json()
        readme_content_decoded = base64.b64decode(readme_content["content"]).decode("utf-8")
        if artifact_url in readme_content_decoded:
            needs_update = 'false'
        else:
            needs_update = 'true'
    else:
        needs_update = 'true'
        print(f"Failed to fetch README. Status code: {response.status_code}")

    # Write the output to GITHUB_OUTPUT
    with open(os.environ['GITHUB_OUTPUT'], 'a') as output_file:
        output_file.write(f"needs_update={needs_update}\n")

if __name__ == "__main__":
    artifact_url = sys.argv[1]
    check_readme(artifact_url)