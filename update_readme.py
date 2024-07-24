import sys
import os
import requests
import base64

def update_readme(artifact_url):
    readme_path = os.path.join(os.environ["GITHUB_WORKSPACE"], "README.md")
    headers = {
        "Authorization": f"Bearer {os.environ['GH_PAT']}",
        "Content-Type": "application/json"
    }
    response = requests.get(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/contents/README.md",
        headers=headers
    )
    if response.status_code == 200:
        readme_content = response.json()
        readme_content_decoded = base64.b64decode(readme_content["content"]).decode("utf-8")
        lines = readme_content_decoded.split("\n")
        lines[208] = f"Download link: {artifact_url}"
        new_content = "\n".join(lines)
        update_data = {
            "message": "Updated manager download link to latest",
            "content": base64.b64encode(new_content.encode()).decode("utf-8"),
            "sha": readme_content["sha"]
        }
        response = requests.put(
            f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/contents/README.md",
            headers=headers,
            json=update_data
        )
        if response.status_code == 200:
            print("README updated successfully.")
        else:
            print(f"Failed to update README. Status code: {response.status_code}")
    else:
        print(f"Failed to fetch README. Status code: {response.status_code}")

if __name__ == "__main__":
    artifact_url = sys.argv[1]
    update_readme(artifact_url)
